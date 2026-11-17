"""Convierte la tabla del Censo 2020 (INEGI) a población de 60+ por estado."""
import re
import sys

import pandas as pd

NOMBRES = {"México": "Estado de México",
           "Veracruz de Ignacio de la Llave": "Veracruz"}


def leer_censo(ruta):
    filas, estado = [], None
    for linea in open(ruta, encoding="utf-8"):
        partes = linea.rstrip("\n").split("\t")
        if len(partes) == 3:
            estado = partes[0]
            partes = partes[1:]
        if len(partes) == 2 and "años" in partes[0]:
            filas.append((estado, partes[0], int(partes[1].replace(",", ""))))
    d = pd.DataFrame(filas, columns=["EST", "EDAD", "POB"])
    d["EST"] = d.EST.replace(NOMBRES)
    return d


if __name__ == "__main__":
    d = leer_censo(sys.argv[1])
    t = d.groupby("EST", as_index=False).POB.sum().rename(columns={"POB": "POB_60_MAS"})
    t.to_csv(sys.argv[2], index=False, encoding="utf-8")
    print(len(t), "estados,", t.POB_60_MAS.sum(), "personas")
