#!/usr/bin/env python3
"""maestro-gatekeeper: map an uploaded surplus file (CSV/XLSX, Arabic or English headers)
to the standard FoodRescue columns. Never edits values except date normalisation and
controlled-vocabulary normalisation; every change is logged.

usage: map_columns.py <input.csv|xlsx> <out_standard.csv> <out_mapping.json> [--map custom_map.json]
"""
import sys, json, re, unicodedata
import pandas as pd

STANDARD = ["op_id", "recorded_at", "institution_id", "institution_name", "institution_type", "region",
            "food_item", "food_type", "qty_produced", "qty_sold", "qty_surplus", "unit", "prepared_at",
            "expiry_at", "storage", "temp_c", "packaging", "served_to_consumers", "surplus_reason", "notes"]
REQUIRED = ["recorded_at", "institution_name", "food_item", "qty_surplus", "unit"]

SYN = {
    "op_id": ["رقم العملية", "رقم", "id", "operation id", "op id", "record id"],
    "recorded_at": ["تاريخ التسجيل", "التاريخ", "date", "recorded at", "record date"],
    "institution_id": ["رمز المؤسسة", "كود المؤسسة", "institution id", "org id"],
    "institution_name": ["اسم المؤسسة", "المؤسسة", "institution", "organization", "org", "restaurant"],
    "institution_type": ["نوع المؤسسة", "institution type", "org type"],
    "region": ["المنطقة", "الموقع", "المدينة", "region", "location", "city", "area"],
    "food_item": ["الصنف", "نوع الطعام", "اسم الصنف", "item", "food", "food item", "dish"],
    "food_type": ["فئة الطعام", "تصنيف الصنف", "food type", "category"],
    "qty_produced": ["الكمية المنتجة", "المنتج", "produced", "qty produced"],
    "qty_sold": ["الكمية المباعة", "المباع", "sold", "qty sold", "served qty"],
    "qty_surplus": ["الكمية الفائضة", "الفائض", "الكمية", "surplus", "qty surplus", "quantity", "qty"],
    "unit": ["وحدة القياس", "الوحدة", "unit", "uom"],
    "prepared_at": ["تاريخ التحضير", "وقت التحضير", "prepared at", "prep date", "prepared"],
    "expiry_at": ["الصلاحية", "تاريخ الصلاحية", "تاريخ الانتهاء", "expiry", "expiry at", "best before", "use by"],
    "storage": ["حالة الحفظ", "طريقة الحفظ", "الحفظ", "storage", "storage method"],
    "temp_c": ["الحرارة", "درجة الحرارة", "temp", "temperature", "temp c"],
    "packaging": ["التغليف", "packaging", "pack"],
    "served_to_consumers": ["هل تم تقديمه", "هل قدم للمستهلكين", "قدم للمستهلكين", "served", "served to consumers"],
    "surplus_reason": ["سبب الفائض", "السبب", "reason", "surplus reason"],
    "notes": ["ملاحظات", "notes", "remarks", "comment"],
}
VOCAB = {
    "unit": {"كغ": "kg", "كيلو": "kg", "كيلوغرام": "kg", "kg": "kg", "kilo": "kg", "وجبة": "meal", "وجبات": "meal",
             "meal": "meal", "meals": "meal", "قطعة": "piece", "حبة": "piece", "piece": "piece", "pcs": "piece",
             "لتر": "l", "l": "l", "liter": "l", "litre": "l"},
    "storage": {"مبرد": "refrigerated", "ثلاجة": "refrigerated", "تبريد": "refrigerated", "refrigerated": "refrigerated",
                "مجمد": "frozen", "frozen": "frozen", "حرارة الغرفة": "room", "غرفة": "room", "مكشوف": "room",
                "room": "room", "ambient": "room", "حفظ ساخن": "hot_holding", "ساخن": "hot_holding", "hot": "hot_holding",
                "hot_holding": "hot_holding"},
    "packaging": {"مغلف": "sealed", "مغلق": "sealed", "sealed": "sealed", "مغطى": "covered", "covered": "covered",
                  "مفتوح": "open", "open": "open", "بدون": "open"},
    "served_to_consumers": {"نعم": "yes", "yes": "yes", "y": "yes", "true": "yes", "1": "yes",
                            "لا": "no", "no": "no", "n": "no", "false": "no", "0": "no"},
    "food_type": {"مطبوخ": "cooked", "cooked": "cooked", "وجبات": "cooked", "مغلف": "packaged", "packaged": "packaged",
                  "مخبوزات": "bakery", "خبز": "bakery", "bakery": "bakery", "خضار": "produce", "فواكه": "produce",
                  "خضار وفواكه": "produce", "produce": "produce", "ألبان": "dairy", "dairy": "dairy",
                  "لحوم": "meat", "meat": "meat", "بقايا تحضير": "prep_scraps", "prep_scraps": "prep_scraps",
                  "أخرى": "other", "other": "other"},
}


def norm(s):
    s = unicodedata.normalize("NFKC", str(s)).strip().lower()
    s = re.sub(r"[ـ_\-\.:]+", " ", s)
    s = s.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")
    return re.sub(r"\s+", " ", s)


def build_map(cols, custom):
    mapping, used = {}, set()
    for std, src in (custom or {}).items():
        if src in cols:
            mapping[src] = std; used.add(std)
    syn = {std: [norm(x) for x in v + [std]] for std, v in SYN.items()}
    for c in cols:
        if c in mapping:
            continue
        nc = norm(c)
        for std in STANDARD:  # exact first
            if std not in used and nc in syn[std]:
                mapping[c] = std; used.add(std); break
    for c in cols:  # then containment
        if c in mapping:
            continue
        nc = norm(c)
        for std in STANDARD:
            if std not in used and any(len(s) > 3 and (s in nc or nc in s) for s in syn[std]):
                mapping[c] = std; used.add(std); break
    return mapping


def main():
    a = sys.argv[1:]
    src, out_csv, out_json = a[0], a[1], a[2]
    custom = json.load(open(a[a.index("--map") + 1])) if "--map" in a else {}
    df = pd.read_excel(src, dtype=str) if src.lower().endswith((".xlsx", ".xls")) else pd.read_csv(src, dtype=str)
    mapping = build_map(list(df.columns), custom)
    out = df.rename(columns=mapping)
    log = []
    for std in STANDARD:
        if std not in out.columns:
            out[std] = ""
    for col, vocab in VOCAB.items():
        nv = {norm(k): v for k, v in vocab.items()}
        for i, v in out[col].fillna("").items():
            if str(v).strip() == "":
                continue
            nvv = nv.get(norm(v))
            if nvv and nvv != v:
                log.append({"row": int(i) + 2, "col": col, "before": v, "after": nvv, "why": "توحيد القيم"})
                out.at[i, col] = nvv
    for col in ["recorded_at", "prepared_at", "expiry_at"]:
        for i, v in out[col].fillna("").items():
            if not str(v).strip():
                continue
            sv = str(v).strip()
            iso = re.match(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}", sv)
            d = pd.to_datetime(sv.replace("/", "-") if iso else sv, errors="coerce", dayfirst=not iso,
                               format="mixed" if iso else None)
            if pd.isna(d):
                log.append({"row": int(i) + 2, "col": col, "before": v, "after": v, "why": "تاريخ غير مقروء — بقي كما هو"})
                continue
            nvv = d.strftime("%Y-%m-%d %H:%M") if (d.hour or d.minute) else d.strftime("%Y-%m-%d")
            if nvv != v:
                out.at[i, col] = nvv
    extra = [c for c in out.columns if c not in STANDARD]
    out[STANDARD + extra].to_csv(out_csv, index=False, encoding="utf-8")
    missing_required = [c for c in REQUIRED if c not in mapping.values()]
    res = {"source": src, "rows": len(df), "mapping": mapping, "unmapped_source_columns": extra,
           "missing_standard_columns": [c for c in STANDARD if c not in mapping.values()],
           "missing_required": missing_required, "status": "blocked" if missing_required else "ok",
           "value_normalisations": log}
    json.dump(res, open(out_json, "w"), ensure_ascii=False, indent=2)
    print(json.dumps({k: res[k] for k in ["rows", "status", "missing_required"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
