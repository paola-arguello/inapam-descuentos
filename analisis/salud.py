"""Estadísticas de los lugares de salud del directorio INAPAM.

Uso:
python3 analisis/salud.py datos/INAPAM_directorio_clasificado.csv \
    datos/poblacion_60mas_estado.csv analisis/salud
"""
import re
import sys
from pathlib import Path

import pandas as pd

# Cadenas que se reconocen por el nombre. Se revisaron a mano.
CADENAS = {
    "+Visión": r"^\s*\+\s*VISI[ÓO]N",
    "Ópticas Lux / Audio Lux": r"[ÓO]PTICAS LUX|AUDIO LUX",
    "Devlyn": r"DEVLYN",
    "Ópticas América": r"[ÓO]PTICAS AM[ÉE]RICA",
    "Ópticas Evolution": r"[ÓO]PTICAS EVOLUTION",
    "Óptica Espadas": r"[ÓO]PTICA ESPADAS",
    "GAES": r"\bGAES\b",
    "Clínicas del Azúcar (Diasalud)": r"DIASALUD",
    "Hospitales MAC": r"CENTRO HOSPITALARIO MAC|HOSPITALES? MAC",
    "Familylabs": r"FAMILYLABS",
    "Laboratorio Exakta": r"EXAKTA",
    "Salauno": r"SALAUNO",
}


def cargar_salud(ruta):
    """Filas de 'Cuidar tu salud' sin veterinarias, con PCT numérico."""
    d = pd.read_csv(ruta, dtype=str, encoding="utf-8-sig").fillna("")
    s = d[(d.SEC == "Cuidar tu salud") & (d.SUB != "Veterinarias")].copy()
    s["PCT"] = pd.to_numeric(s.PCT, errors="coerce")
    return s


def forma_descuento(texto):
    """Cómo viene escrito el descuento."""
    t = texto.upper()
    pcts = re.findall(r"\d+(?:\.\d+)?\s*%", t)
    if not pcts:
        if re.search(r"GRATIS|SIN COSTO|GRATUIT", t):
            return "gratis"
        if "$" in t:
            return "precio fijo"
        return "sin porcentaje (vago)"
    if len(pcts) == 1:
        return "un porcentaje"
    return "varios porcentajes"


def cadena(nombre):
    for c, patron in CADENAS.items():
        if re.search(patron, nombre.upper()):
            return c
    return ""


def sin_telefono(tel):
    return bool(re.fullmatch(r"\s*(-+|PENDIENTE)?\s*", tel))


def por_tipo(s, pob_total):
    g = s.groupby("SUB")
    t = pd.DataFrame({
        "lugares": g.size(),
        "por_100mil_60mas": g.size() / pob_total * 1e5,
        "estados_con_alguno": g.EST.nunique(),
        "mediana_pct": g.PCT.median(),
        "q1_pct": g.PCT.quantile(0.25),
        "q3_pct": g.PCT.quantile(0.75),
        "pct_50_o_mas": g.PCT.apply(lambda x: (x >= 50).mean() * 100),
        "pct_varios_porcentajes": g.FORMA.apply(
            lambda x: (x == "varios porcentajes").mean() * 100),
        "pct_de_cadena": g.CADENA.apply(lambda x: (x != "").mean() * 100),
        "pct_sin_telefono": g.SIN_TEL.mean() * 100,
    })
    return t.round(1).sort_values("lugares", ascending=False)


def por_estado(s, pob):
    t = pd.crosstab(s.EST, s.SUB)
    t["TOTAL_SALUD"] = t.sum(axis=1)
    t = pob.set_index("EST").join(t).fillna(0)
    t["SALUD_POR_1000"] = (t.TOTAL_SALUD / t.POB_60_MAS * 1000).round(2)
    t["PERSONAS_POR_LUGAR"] = (t.POB_60_MAS / t.TOTAL_SALUD).round(0)
    t["PCT_SIN_TELEFONO"] = (s.groupby("EST").SIN_TEL.mean() * 100).round(1)
    return t.sort_values("SALUD_POR_1000", ascending=False)


def main(base, poblacion, salida):
    s = cargar_salud(base)
    pob = pd.read_csv(poblacion)
    s["FORMA"] = s.DESCUENTO.map(forma_descuento)
    s["CADENA"] = s.NOMBRE.map(cadena)
    s["SIN_TEL"] = s.TELEFONO.map(sin_telefono)
    out = Path(salida)
    out.mkdir(parents=True, exist_ok=True)

    tipos = por_tipo(s, pob.POB_60_MAS.sum())
    estados = por_estado(s, pob)
    cadenas = (s[s.CADENA != ""].groupby("CADENA")
               .agg(lugares=("EST", "size"), estados=("EST", "nunique"),
                    descuentos_distintos=("DESCUENTO", "nunique"),
                    descuento=("DESCUENTO", "first"))
               .sort_values("lugares", ascending=False))
    formas = s.FORMA.value_counts().rename("lugares").to_frame()
    formas["porcentaje"] = (formas.lugares / len(s) * 100).round(1)

    tipos.to_csv(out / "salud_por_tipo.csv")
    estados.to_csv(out / "salud_por_estado.csv")
    cadenas.to_csv(out / "salud_cadenas.csv")
    formas.to_csv(out / "salud_forma_descuento.csv")

    print(f"Lugares de salud: {len(s):,}  (sin veterinarias)")
    print(f"Por cada 1,000 personas de 60+: "
          f"{len(s) / pob.POB_60_MAS.sum() * 1000:.2f}")
    print(f"Mediana del descuento: {s.PCT.median():.0f}%   "
          f"50% o más: {(s.PCT >= 50).mean() * 100:.1f}%")
    print(f"De cadenas: {(s.CADENA != '').sum():,} "
          f"({(s.CADENA != '').mean() * 100:.1f}%)")
    print(f"Sin teléfono: {s.SIN_TEL.sum():,} ({s.SIN_TEL.mean() * 100:.1f}%)")
    print("\n", tipos.to_string())
    print("\n", formas.to_string())
    print("\n", cadenas.drop(columns="descuento").to_string())
    cols = ["POB_60_MAS", "TOTAL_SALUD", "SALUD_POR_1000", "PERSONAS_POR_LUGAR",
            "Psicología", "Aparatos auditivos", "Ortopedia y podología",
            "PCT_SIN_TELEFONO"]
    print("\n", estados[cols].to_string())


if __name__ == "__main__":
    main(*sys.argv[1:4])
