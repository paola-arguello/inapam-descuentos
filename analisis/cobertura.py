"""Lugares con descuento por cada 1,000 personas de 60 años o más, por estado."""
import sys

import pandas as pd

base = pd.read_csv(sys.argv[1], dtype=str, encoding="utf-8-sig")
pob = pd.read_csv(sys.argv[2])

lugares = base.groupby("EST").size().rename("LUGARES")
salud = base[base.SEC == "Cuidar tu salud"].groupby("EST").size().rename("LUGARES_SALUD")
t = pob.set_index("EST").join([lugares, salud])
assert t.LUGARES.notna().all(), "hay estados sin unir"
t["POR_1000"] = (t.LUGARES / t.POB_60_MAS * 1000).round(2)
t["SALUD_POR_1000"] = (t.LUGARES_SALUD / t.POB_60_MAS * 1000).round(2)
t["PERSONAS_POR_LUGAR"] = (t.POB_60_MAS / t.LUGARES).round(0).astype(int)
t = t.sort_values("POR_1000", ascending=False)
t.to_csv(sys.argv[3], encoding="utf-8")
print(t.to_string())
print("\nNacional:", round(t.LUGARES.sum() / t.POB_60_MAS.sum() * 1000, 2), "por 1,000;",
      round(t.POB_60_MAS.sum() / t.LUGARES.sum()), "personas por lugar")
