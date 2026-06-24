# -*- coding: utf-8 -*-
import openpyxl
F="The Clothing Cove - SEO & AEO Plan.xlsx"
wb=openpyxl.load_workbook(F)
exact={
 "IN-STOCK MISSING SEO TITLE": "IN-STOCK: NO CUSTOM SEO TITLE",
 "Missing SEO title tag": "No custom SEO title (defaults to product name)",
}
changed=[]
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if not isinstance(c.value,str): continue
            v=c.value.strip()
            if v in exact:
                c.value=exact[v]; changed.append(f"{ws.title}!{c.coordinate}")
            elif "auto-generated titles" in c.value:
                c.value="Google shows the raw product name (SKU and all); no keyword targeting."
                changed.append(f"{ws.title}!{c.coordinate} (note)")
wb.save(F)
print("updated cells:", changed)
print("Exec Summary charts intact:", len(wb["Executive Summary"]._charts))
