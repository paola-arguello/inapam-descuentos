# Buscador de descuentos INAPAM

Una forma más fácil de buscar los lugares que dan descuento con la credencial INAPAM (personas de 60 años o más en México).

**Buscador:** https://paola-arguello.github.io/inapam-descuentos/

El INAPAM publica su Directorio de Beneficios como siete PDFs, uno por categoría, con 475 páginas en total. Para encontrar un dentista con descuento cerca de tu casa hay que abrir el PDF de Salud y recorrer 190 páginas. Este repo convierte esos PDFs en una tabla y en una página donde eliges qué quieres hacer, tu estado y tu municipio, y ves los lugares ordenados de mayor a menor descuento.

**Esta página no es del INAPAM ni del gobierno.** La hice por mi cuenta a partir del directorio público. Si algo no coincide, lo que vale es el directorio oficial en [gob.mx/inapam](https://www.gob.mx/inapam) y lo que diga el establecimiento. Cada lugar tiene sus restricciones.

Si encuentras un error o un lugar que ya no da descuento, escríbeme a pao.arguello.pascualli@gmail.com.

## Qué hay aquí

| Archivo | Qué es |
|---|---|
| `index.html`, `datos.json` | El buscador. Es una sola página que lee `datos.json`. |
| `datos/INAPAM_directorio_clasificado.csv` | La base completa: 9,874 lugares de los 32 estados. |
| `scripts/` | Cómo se generó la base desde los PDFs. |
| `datos/inegi_censo2020_60mas_por_edad.tsv` | Población de 60 años o más por estado y grupo de edad. INEGI, Censo de Población y Vivienda 2020. |
| `datos/poblacion_60mas_estado.csv` | La misma población sumada por estado. |
| `analisis/` | Estadísticas del directorio. `cobertura.py` calcula lugares por cada 1,000 personas de 60 años o más. `salud.py` hace el análisis de los lugares de salud (sin veterinarias) y guarda las tablas en `analisis/salud/`. |

Para repetir el cálculo de cobertura:

```
python3 analisis/poblacion_60.py datos/inegi_censo2020_60mas_por_edad.tsv datos/poblacion_60mas_estado.csv
python3 analisis/cobertura.py datos/INAPAM_directorio_clasificado.csv datos/poblacion_60mas_estado.csv analisis/cobertura_estados.csv
python3 analisis/salud.py datos/INAPAM_directorio_clasificado.csv datos/poblacion_60mas_estado.csv analisis/salud
```

La población es de 2020 y el directorio de 2026. Para 2026 hay más personas de 60 años o más, así que las tasas reales son algo más bajas que las de la tabla.

## Los datos

Fuente: Directorio de Beneficios con Credencial INAPAM. Los archivos terminan en `oct_26`; lo tomamos como octubre de 2026.

| Categoría (PDF) | Páginas | Lugares |
|---|---|---|
| Salud | 190 | 4,681 |
| Vestido y hogar | 114 | 2,846 |
| Alimentación | 43 | 1,063 |
| Educación, recreación y cultura | 98 | 958 |
| Asesoría y servicios legales | 20 | 235 |
| Predial | 6 | 67 |
| Transporte | 4 | 24 |
| **Total** | **475** | **9,874** |

Columnas del CSV:

| Columna | Significado |
|---|---|
| EST | Estado |
| MUN | Municipio o alcaldía, normalizado |
| NOMBRE, DOMICILIO, TELEFONO, DESCUENTO | Como vienen en el PDF |
| PCT | El porcentaje más alto que aparece en el texto del descuento. GRATIS cuenta como 100. Vacío si no hay porcentaje. |
| SEC, SUB | Actividad y tipo de lugar (ver abajo) |
| CATEGORIA | PDF de origen |
| NUM, PAGINA | Número de fila y página en el PDF, para revisar contra el original |

### Actividades y tipos

Las categorías del PDF no ayudan mucho si lo que quieres es ir al dentista. Por eso cada lugar tiene una actividad ("Cuidar tu salud", "Compras y hogar", "Salir y divertirte", "Viajar y moverte", "Trámites") y un tipo (dentistas, ópticas, funerarias, etc.). Se asignan con palabras clave en el nombre del negocio. Las reglas están en `scripts/classify.py` y gana la primera que coincide.

Esto tiene errores. "Hogar, ferretería y más" y "Médicos, clínicas y hospitales" son los tipos donde cae lo que no encaja en otro lado.

### Lo que hay que saber antes de usar los números

- **El porcentaje es el máximo.** "40%, 20% Ó 10%" queda como 40. Más o menos 1 de cada 8 lugares tiene varios porcentajes, así que usar el máximo infla un poco los números.
- Unos 190 lugares no dan porcentaje ("tarifa preferencial", "consulta $250", "2X1"). En el buscador salen al final.
- **Municipios.** En CDMX y Estado de México se corrigieron a mano con la dirección y el código postal. En los demás estados solo se juntaron nombres que son iguales sin acentos, así que pueden quedar municipios repetidos con nombres un poco distintos. Dos filas del Estado de México no tienen municipio.
- Unos 2,500 lugares no tienen teléfono en el directorio.
- 16 filas repiten nombre y dirección.

## Cómo volver a generar la base

Python 3 con pdfplumber, pandas y numpy. Desde la carpeta `scripts/`, con los 7 PDFs:

```
python3 extract.py <los 7 PDFs>   # → raw.csv
python3 build.py                  # → full_clean.csv y cdmx_edomex_sorted.csv
mkdir -p buscador
python3 classify.py               # → buscador/datos.json e INAPAM_directorio_clasificado.csv
```

`build.py` imprime los municipios que no pudo reconocer; se agregan a `ALIAS` en ese archivo. `zones.py` tiene tiempos de manejo estimados que usé para un flyer familiar. El buscador no los usa, pero `build.py` lo necesita para correr.

## Uso de IA

Usé Claude (Anthropic) para escribir los scripts y la página. Las decisiones sobre qué datos usar, cómo clasificarlos y qué publicar son mías, y revisé los resultados contra los PDFs.
