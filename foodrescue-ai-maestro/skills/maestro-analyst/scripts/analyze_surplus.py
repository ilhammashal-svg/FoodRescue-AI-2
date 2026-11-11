#!/usr/bin/env python3
"""maestro-analyst: clean the standard surplus log, classify every row into the three
FoodRescue tracks (human / compost / dispose) with a reason, match to partners, compute
KPIs and write Excel + one-page report + insights.json.

Classification is a decision aid only — never a food-safety certificate. Every row is
written with manager_approval = pending.

usage: analyze_surplus.py <current_std.csv> <prev_std.csv|-> <config.json> <outdir> <run_date>
"""
import sys, json, os, re
import pandas as pd
from datetime import datetime

SPOIL = ["تلف", "تالف", "رائحة", "عفن", "متعفن", "فاسد", "ملوث", "تلوث", "حشرات", "spoil", "mold", "mould", "smell", "rotten", "contaminat"]
CHEM = ["منظف", "كيماوي", "كيميائي", "مبيد", "بلاستيك", "زجاج", "chemical", "detergent", "plastic", "glass"]
ORGANIC = {"produce", "bakery", "prep_scraps", "cooked", "packaged", "other"}
TRACK_AR = {"human": "صالح للاستخدام البشري", "compost": "قابل للتحويل إلى سماد", "dispose": "غير صالح — إتلاف آمن"}
DAY_AR = {"Monday": "الاثنين", "Tuesday": "الثلاثاء", "Wednesday": "الأربعاء", "Thursday": "الخميس", "Friday": "الجمعة", "Saturday": "السبت", "Sunday": "الأحد"}
KPI_AR = {"total_surplus_kg": "إجمالي الفائض", "human_kg": "التوزيع", "compost_kg": "السماد", "dispose_kg": "الإتلاف", "meals_redirected": "الوجبات"}
PRIORITY_AR = {"urgent": "عاجلة", "high": "عالية", "medium": "متوسطة", "low": "منخفضة"}
DEF = {"meal_kg": 0.4, "piece_kg": 0.1, "l_kg": 1.0, "co2e_per_kg": 2.5,
       "room_temp_max_h": 2, "cooked_chilled_max_h": 48, "fridge_max_c": 5, "hot_min_c": 63,
       "min_quality_score": 60, "anomaly_multiplier": 3, "suspicious_dispose_share": 0.3}


def has(text, words):
    t = str(text or "").lower()
    return any(w in t for w in words)


def to_kg(q, unit, c):
    f = {"kg": 1.0, "meal": c["meal_kg"], "piece": c["piece_kg"], "l": c["l_kg"]}.get(str(unit), None)
    return None if f is None or pd.isna(q) else round(float(q) * f, 3)


def classify(r, c):
    reasons, missing = [], []
    for f in ["prepared_at", "expiry_at", "storage", "served_to_consumers", "food_type"]:
        if not str(r.get(f, "") or "").strip() or str(r.get(f)) == "nan":
            missing.append(f)
    ft, st = r.get("food_type"), r.get("storage")
    ref = pd.to_datetime(r.get("recorded_at"), errors="coerce")
    prep = pd.to_datetime(r.get("prepared_at"), errors="coerce")
    exp = pd.to_datetime(r.get("expiry_at"), errors="coerce")
    temp = pd.to_numeric(r.get("temp_c"), errors="coerce")
    hours = (ref - prep).total_seconds() / 3600 if pd.notna(ref) and pd.notna(prep) else None
    hours_left = (exp - ref).total_seconds() / 3600 if pd.notna(ref) and pd.notna(exp) else None
    if pd.notna(exp) and pd.notna(ref) and exp.normalize() == exp and exp.normalize() >= ref.normalize():
        hours_left = (exp + pd.Timedelta(hours=23, minutes=59) - ref).total_seconds() / 3600

    spoiled = has(r.get("notes"), SPOIL) or has(r.get("surplus_reason"), SPOIL)
    chem = has(r.get("notes"), CHEM)
    expired = hours_left is not None and hours_left < 0
    temp_bad = (st == "refrigerated" and pd.notna(temp) and temp > c["fridge_max_c"]) or \
               (st == "hot_holding" and pd.notna(temp) and temp < c["hot_min_c"])
    perishable = ft in {"cooked", "dairy", "meat"}
    time_bad = hours is not None and perishable and (
        (st == "room" and hours > c["room_temp_max_h"]) or (st in {"refrigerated", "hot_holding"} and hours > c["cooked_chilled_max_h"]))
    served = r.get("served_to_consumers") == "yes"
    critical_missing = [m for m in missing if m in ("expiry_at", "storage", "served_to_consumers")] + \
                       (["prepared_at"] if "prepared_at" in missing and perishable else [])

    if spoiled: reasons.append("ملاحظة تلف/رائحة/تلوث")
    if chem: reasons.append("احتمال تلوث كيميائي أو مواد غير عضوية")
    if expired: reasons.append("تجاوز تاريخ الصلاحية")
    if temp_bad: reasons.append(f"حرارة حفظ غير آمنة ({temp}°C)")
    if time_bad: reasons.append(f"مدة منذ التحضير {hours:.0f} ساعة تتجاوز الحد الآمن لحفظ {st}")
    if served: reasons.append("قُدّم للمستهلكين")
    if critical_missing: reasons.append("معلومات ناقصة: " + "، ".join(critical_missing))

    if chem or (spoiled and ft in {"meat", "dairy"}):
        track = "dispose"
    elif ft == "prep_scraps":
        track = "compost"
        reasons.append("بقايا تحضير — مسار سماد بحكم النوع (جدول التصنيف في ملف المشروع)")
    elif spoiled or expired or temp_bad or time_bad or served or critical_missing:
        organic_ok = ft in ORGANIC and not chem and not (ft in {"meat", "dairy"})
        # missing critical info -> dispose per project table, unless clearly plant/bakery organic
        if critical_missing and not (spoiled or expired or temp_bad or time_bad or served):
            track = "dispose"
        else:
            track = "compost" if organic_ok else "dispose"
    else:
        track = "human"
        reasons.append("محفوظ جيدًا، غير مقدّم، ضمن الفترة الآمنة، ومعلوماته مكتملة")
        if r.get("packaging") == "open":
            track = "compost" if ft in ORGANIC else "dispose"
            reasons[-1] = "تغليف مفتوح — لا يوزّع بشريًا"

    kg = r.get("qty_kg") or 0
    if track == "human":
        pr = "urgent" if hours_left is not None and hours_left <= 12 else "high" if hours_left is not None and hours_left <= 36 else "medium"
    elif track == "compost":
        pr = "high" if kg >= 20 else "medium"
    else:
        pr = "high" if critical_missing else "medium"
    return track, "؛ ".join(reasons), pr, ", ".join(missing)


def match(r, partners):
    want = {"human": {"orphanage", "charity", "food_bank", "intermediary"}, "compost": {"compost", "collection_point", "municipality"}}.get(r["classification"])
    if not want:
        return None, None, None, 0, "لا مطابقة — إتلاف وفق الإجراءات المحلية"
    best, bs = None, -1
    for p in partners:
        if p.get("type") not in want:
            continue
        acc = [a.lower() for a in p.get("accepts", [])]
        if acc and r.get("food_type") not in acc and "all" not in acc:
            continue
        s = 0
        s += 40 if p.get("region") == r.get("region") else 10
        cap = float(p.get("capacity_kg") or 0)
        s += 20 if cap >= (r.get("qty_kg") or 0) else 5
        s += 20 if p.get("verified") in (True, "yes", "true") else 0
        s += 10 if p.get("transport") in (True, "yes", "true") else 0
        s += 10 if (r.get("qty_kg") or 0) >= float(p.get("min_qty") or 0) else -30
        if r["classification"] == "human" and p.get("type") == "orphanage" and r.get("priority") in ("urgent", "high"):
            s += 5
        if s > bs:
            best, bs = p, s
    if not best:
        return None, None, None, 0, "لا جهة مسجلة تقبل هذا الصنف — أضيفي جهة في الداشبورد"
    v = "موثّقة" if best.get("verified") in (True, "yes", "true") else "غير موثّقة — تحقّق قبل التواصل"
    return best.get("id"), best.get("name"), best.get("region"), bs, v


def load(path, c):
    df = pd.read_csv(path, dtype=str).fillna("")
    for col in ["qty_produced", "qty_sold", "qty_surplus", "temp_c"]:
        df[col] = pd.to_numeric(df[col].replace("", None), errors="coerce")
    df["qty_kg"] = [to_kg(q, u, c) for q, u in zip(df["qty_surplus"], df["unit"])]
    return df


def quality(df):
    log, score = [], 100
    n = len(df) or 1
    dup = df[df["op_id"].ne("") & df["op_id"].duplicated(keep="first")]
    if len(dup):
        log.append({"check": "تكرار رقم العملية", "rows": len(dup), "action": "عُزلت النسخ المكررة"}); score -= min(15, 3 * len(dup))
    neg = df[(df["qty_surplus"] <= 0) | df["qty_surplus"].isna()]
    if len(neg):
        log.append({"check": "كمية فائضة صفرية/سالبة/فارغة", "rows": len(neg), "action": "عُزلت"}); score -= min(15, 3 * len(neg))
    unit_bad = df[df["qty_kg"].isna() & df["qty_surplus"].notna()]
    if len(unit_bad):
        log.append({"check": "وحدة قياس غير معروفة", "rows": len(unit_bad), "action": "عُزلت"}); score -= min(10, 2 * len(unit_bad))
    calc = df[df["qty_produced"].notna() & df["qty_sold"].notna() & df["qty_surplus"].notna() &
              ((df["qty_produced"] - df["qty_sold"] - df["qty_surplus"]).abs() > 0.01)]
    if len(calc):
        log.append({"check": "المنتج − المباع ≠ الفائض", "rows": len(calc), "action": "تحذير فقط، الفائض المسجل معتمد"}); score -= min(10, len(calc))
    for f in ["expiry_at", "storage", "prepared_at", "region"]:
        m = (df[f] == "").sum()
        if m:
            log.append({"check": f"قيمة ناقصة: {f}", "rows": int(m), "action": "تُصنّف بحذر"}); score -= min(10, round(10 * m / n))
    iso = pd.concat([dup, neg, unit_bad]).index.unique()
    return max(0, score), log, iso


def kpis(df, c):
    tot = df["qty_kg"].sum()
    by = df.groupby("classification")["qty_kg"].sum().to_dict()
    hum = by.get("human", 0.0)
    prod_kg = sum(to_kg(q, u, c) or 0 for q, u in zip(df["qty_produced"].fillna(0), df["unit"]))
    meals = df.loc[(df.classification == "human") & (df.unit == "meal"), "qty_surplus"].sum() + \
            df.loc[(df.classification == "human") & (df.unit != "meal"), "qty_kg"].sum() / c["meal_kg"]
    return {"total_surplus_kg": round(tot, 1), "human_kg": round(hum, 1), "compost_kg": round(by.get("compost", 0.0), 1),
            "dispose_kg": round(by.get("dispose", 0.0), 1), "meals_redirected": int(round(meals)),
            "rescue_rate": round((hum + by.get("compost", 0.0)) / tot, 3) if tot else None,
            "surplus_rate": round(tot / prod_kg, 3) if prod_kg else None,
            "co2e_avoided_kg": round((hum + by.get("compost", 0.0)) * c["co2e_per_kg"], 1),
            "operations": int(len(df)), "institutions": int(df["institution_name"].nunique())}


def main():
    cur, prev, cfgp, out, run = sys.argv[1:6]
    cfg = json.load(open(cfgp))
    c = {**DEF, **{k: v for k, v in cfg.get("thresholds", {}).items() if v not in (None, "")}}
    for k in ("meal_kg", "co2e_per_kg"):
        if cfg.get(k): c[k] = float(cfg[k])
    partners = cfg.get("partners", [])
    os.makedirs(out, exist_ok=True)

    raw = load(cur, c)
    score, qlog, iso = quality(raw)
    anomalies = raw.loc[iso].copy(); anomalies["anomaly_reason"] = "عُزل في الفحص"
    df = raw.drop(index=iso).copy()
    med = df["qty_kg"].median()
    big = df[df["qty_kg"] > c["anomaly_multiplier"] * med] if med else df.iloc[0:0]
    if len(big):
        qlog.append({"check": f"كمية > {c['anomaly_multiplier']}× الوسيط", "rows": len(big), "action": "تبقى في التحليل وتُعلَّم شاذة"})
        a2 = big.copy(); a2["anomaly_reason"] = "كمية كبيرة غير معتادة"; anomalies = pd.concat([anomalies, a2])

    res = [classify(r, c) for _, r in df.iterrows()]
    df["classification"] = [x[0] for x in res]; df["classification_ar"] = df["classification"].map(TRACK_AR)
    df["classification_reason"] = [x[1] for x in res]; df["priority"] = [x[2] for x in res]
    df["missing_fields"] = [x[3] for x in res]
    m = [match(r, partners) for _, r in df.iterrows()]
    df["suggested_partner_id"] = [x[0] for x in m]; df["suggested_partner"] = [x[1] for x in m]
    df["partner_region"] = [x[2] for x in m]; df["match_score"] = [x[3] for x in m]; df["verification_status"] = [x[4] for x in m]
    df["final_action"] = df["classification"].map({"human": "توزيع بعد فحص بشري", "compost": "تحويل لسماد بعد تأكيد قبول الجهة",
                                                   "dispose": "عدم التوزيع + توثيق سبب الإتلاف + الإجراءات المحلية"})
    df["manager_approval"] = "pending"; df["email_status"] = "none"
    df["weekday"] = pd.to_datetime(df["recorded_at"], errors="coerce").dt.day_name().map(DAY_AR)

    k = kpis(df, c)
    prev_k, wow = None, {}
    if prev != "-" and os.path.exists(prev):
        p = load(prev, c); _, _, piso = quality(p); p = p.drop(index=piso)
        rp = [classify(r, c) for _, r in p.iterrows()]; p["classification"] = [x[0] for x in rp]
        prev_k = kpis(p, c)
        for key in ("total_surplus_kg", "human_kg", "compost_kg", "dispose_kg", "meals_redirected"):
            if prev_k.get(key):
                wow[key] = round((k[key] - prev_k[key]) / prev_k[key], 3)
        if k.get("surplus_rate") is not None and prev_k.get("surplus_rate") is not None:
            wow["surplus_rate_pp"] = round(k["surplus_rate"] - prev_k["surplus_rate"], 3)

    by_item = df.groupby("food_item").agg(kg=("qty_kg", "sum"), ops=("op_id", "count")).sort_values("kg", ascending=False).reset_index()
    by_day = df.groupby("weekday")["qty_kg"].sum().sort_values(ascending=False).reset_index()
    by_inst = df.pivot_table(index=["institution_id", "institution_name"], columns="classification", values="qty_kg", aggfunc="sum", fill_value=0).reset_index()
    for t in ("human", "compost", "dispose"):
        if t not in by_inst: by_inst[t] = 0.0
    by_inst["total"] = by_inst[["human", "compost", "dispose"]].sum(axis=1)
    by_inst = by_inst.sort_values("human", ascending=False)
    by_reason = df.groupby("surplus_reason")["qty_kg"].sum().sort_values(ascending=False).reset_index()
    by_track = df.groupby("classification_ar")["qty_kg"].sum().reset_index()
    matches = df[["op_id", "food_item", "qty_kg", "classification_ar", "priority", "suggested_partner", "partner_region", "match_score", "verification_status", "final_action", "manager_approval"]]

    # reduction plan: rules from data
    plan = []
    ftype = df.groupby("food_item")["food_type"].first().to_dict()
    for _, r in by_item.head(3).iterrows():
        share = r.kg / k["total_surplus_kg"] if k["total_surplus_kg"] else 0
        if ftype.get(r.food_item) == "prep_scraps":
            plan.append(f"«{r.food_item}» ({share:.0%} = {r.kg:.1f} كغ): حسّني التقطيع والاستفادة من الأطراف، ووجّهي الباقي للسماد مباشرة.")
        else:
            plan.append(f"خفض إنتاج «{r.food_item}» تدريجيًا 10–15٪ (يمثل {share:.0%} من الفائض = {r.kg:.1f} كغ) ومراقبة أسبوعين.")
    if len(by_day):
        plan.append(f"يوم {by_day.iloc[0].weekday} هو الأعلى هدرًا ({by_day.iloc[0].qty_kg:.1f} كغ): اربطي كمية التحضير بعدد الحجوزات/الحضور المتوقع لذلك اليوم.")
    if len(by_reason):
        plan.append(f"السبب الأكثر تكرارًا «{by_reason.iloc[0].surplus_reason}»: إجراء تصحيحي مخصص له على مستوى المطبخ.")

    xl = os.path.join(out, f"FR_{run}_analyst_surplus-log.xlsx")
    with pd.ExcelWriter(xl, engine="openpyxl") as w:
        pd.DataFrame([{"المؤشر": a, "القيمة": b} for a, b in k.items()]).to_excel(w, "Summary", index=False)
        df.to_excel(w, "Cleaned", index=False); by_track.to_excel(w, "By_Track", index=False)
        by_item.to_excel(w, "By_Item", index=False); by_day.to_excel(w, "By_Day", index=False)
        by_inst.to_excel(w, "By_Institution", index=False); by_reason.to_excel(w, "By_Reason", index=False)
        matches.to_excel(w, "Matches", index=False); anomalies.to_excel(w, "Anomalies", index=False)
        pd.DataFrame(qlog).to_excel(w, "DataQualityLog", index=False)
        pd.DataFrame([{"key": a, "value": json.dumps(b, ensure_ascii=False) if isinstance(b, (list, dict)) else b} for a, b in c.items()]).to_excel(w, "Config", index=False)
    # live formulas in Summary for traceability
    from openpyxl import load_workbook
    wb = load_workbook(xl); ws = wb["Summary"]; n = len(df) + 1
    cols = {cell.value: cell.column_letter for cell in wb["Cleaned"][1]}
    ws["D1"], ws["E1"] = "تحقق بصيغة حية", "القيمة"
    ws["D2"], ws["E2"] = "مجموع الفائض كغ", f"=SUM(Cleaned!{cols['qty_kg']}2:{cols['qty_kg']}{n})"
    for i, t in enumerate(["human", "compost", "dispose"], start=3):
        ws[f"D{i}"], ws[f"E{i}"] = f"{t} كغ", f'=SUMIF(Cleaned!{cols["classification"]}2:{cols["classification"]}{n},"{t}",Cleaned!{cols["qty_kg"]}2:{cols["qty_kg"]}{n})'
    wb.save(xl)

    low = score < c["min_quality_score"]
    top_inst = by_inst.iloc[0] if len(by_inst) else None
    insights = {"run_date": run, **k, "wow": wow, "previous": prev_k, "data_quality_score": score, "low_quality": low,
                "top_items": [{"item": r.food_item, "kg": round(r.kg, 1)} for _, r in by_item.head(5).iterrows()],
                "top_waste_day": by_day.iloc[0].weekday if len(by_day) else None,
                "top_reason": by_reason.iloc[0].surplus_reason if len(by_reason) else None,
                "top_institution_id": top_inst.institution_id if top_inst is not None else None,
                "by_institution": [{"institution_id": r.institution_id, "human_kg": round(r.human, 1), "compost_kg": round(r.compost, 1),
                                    "dispose_kg": round(r.dispose, 1), "total_kg": round(r.total, 1)} for _, r in by_inst.iterrows()],
                "urgent_human_ops": df[(df.classification == "human") & (df.priority.isin(["urgent", "high"]))]["op_id"].tolist(),
                "unmatched_ops": df[(df.classification != "dispose") & df.suggested_partner.isna()]["op_id"].tolist(),
                "anomalies": len(anomalies), "reduction_plan": plan, "config_used": c,
                "disclaimer": "التصنيف توصية أولية مساعدة على القرار وليس شهادة صلاحية غذائية؛ القرار النهائي بشري."}
    json.dump(insights, open(os.path.join(out, "insights.json"), "w"), ensure_ascii=False, indent=2, default=str)
    matches.to_csv(os.path.join(out, f"FR_{run}_analyst_partner-matches.csv"), index=False)

    # one-page report
    from docx import Document
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    d = Document()
    st = d.styles["Normal"]; st.font.name = "Arial"; st.font.size = Pt(10)
    def P(t, b=False, size=None):
        p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; rr = p.add_run(t); rr.bold = b
        rr.font.rtl = True
        if size: rr.font.size = Pt(size)
        pPr = p._p.get_or_add_pPr(); from docx.oxml.ns import qn; from docx.oxml import OxmlElement
        bidi = OxmlElement("w:bidi"); bidi.set(qn("w:val"), "1"); pPr.append(bidi)
        return p
    if low: P(f"⚠️ تحذير: جودة البيانات {score}/100 أقل من الحد — الأرقام استرشادية فقط.", True)
    P(f"FoodRescue AI — تقرير الفائض الأسبوعي {run}", True, 14)
    hl = f"أُنقذ {k['human_kg'] + k['compost_kg']:.0f} كغ من {k['total_surplus_kg']:.0f} كغ فائض ({(k['rescue_rate'] or 0):.0%})، منها ≈{k['meals_redirected']} وجبة موجهة للتوزيع."
    P(hl, True)
    P(f"• صالح للتوزيع: {k['human_kg']} كغ   • سماد: {k['compost_kg']} كغ   • إتلاف: {k['dispose_kg']} كغ   • العمليات: {k['operations']}   • المؤسسات: {k['institutions']}")
    if wow: P("• التغير عن الأسبوع السابق: " + "، ".join(f"{KPI_AR.get(a, a)} {b:+.0%}" for a, b in wow.items() if not a.endswith("_pp")))
    else: P("• لا مقارنة أسبوعية (لا ملف للأسبوع السابق).")
    P(f"• نسبة الفائض من الإنتاج: {(k['surplus_rate'] or 0):.1%}   • انبعاثات متجنبة تقديرية: {k['co2e_avoided_kg']} كغ CO2e (عامل {c['co2e_per_kg']} افتراضي قابل للتعديل)")
    P("ثلاثة استنتاجات", True)
    if len(by_item): P(f"1) «{by_item.iloc[0].food_item}» أكبر مصدر فائض ({by_item.iloc[0].kg:.1f} كغ) ← راجعي كمية تحضيره.")
    if len(by_day): P(f"2) {by_day.iloc[0].weekday} أعلى يوم هدرًا ({by_day.iloc[0].qty_kg:.1f} كغ) ← اربطي التحضير بالطلب المتوقع.")
    P(f"3) {len(insights['urgent_human_ops'])} عملية توزيع عاجلة/عالية الأولوية و{len(insights['unmatched_ops'])} بلا جهة مطابقة ← تحقّق بشري وتواصل اليوم.")
    P("خطة تقليل الفائض", True)
    for x in plan: P("• " + x)
    P("المخاطر وجودة البيانات", True)
    P(f"درجة الجودة {score}/100؛ عمليات معزولة/شاذة: {len(anomalies)}. " + "؛ ".join(f"{q['check']} ({q['rows']})" for q in qlog[:4]))
    P(insights["disclaimer"], size=8)
    rp = os.path.join(out, f"FR_{run}_analyst_surplus-report.docx"); d.save(rp)
    print(json.dumps({"status": "ok_with_warnings" if (low or qlog) else "ok", "quality": score, "kpis": k, "excel": xl, "report": rp}, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
