import pandas as pd, re, unicodedata, sys
sys.path.insert(0,'.')
from zones import Z
def strip(s): return ''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn').upper().strip()
KEY={strip(k):k for k in Z}
ALIAS={'ALVARO OBREGON':'ÁLVARO OBREGÓN','GUSTAVO A MADERO':'GUSTAVO A. MADERO','CUAJIMALPA':'CUAJIMALPA DE MORELOS','MAGDALENA CONTRERAS':'LA MAGDALENA CONTRERAS','TLALAPAN':'TLALPAN',
'ATIZAPAN':'ATIZAPÁN DE ZARAGOZA','CALPULHUAC':'CAPULHUAC','CIUDAD NEZAHUALCOYOTL':'NEZAHUALCÓYOTL','COACALCO':'COACALCO DE BERRIOZÁBAL','ECATEPEC':'ECATEPEC DE MORELOS',
'IXTAPAN DE LA SAL':'IXTAPAN DE LA SAL','JOCOTITLAN':'JOCOTITLÁN','LERMA DE VILLADA':'LERMA','NAUCALPAN':'NAUCALPAN DE JUÁREZ','TALNEPANTLA':'TLALNEPANTLA DE BAZ','TLANEPANTLA':'TLALNEPANTLA DE BAZ',
'TLANEPANTLA DE BAZ':'TLALNEPANTLA DE BAZ','TLALNEPANTLA':'TLALNEPANTLA DE BAZ','TECAMAC':'TECÁMAC','TEJUPILCO DE HIDALGO':'TEJUPILCO','TEMAZCALTEPEC':'TEMASCALTEPEC','TENAGO DE VALLE':'TENANGO DEL VALLE',
'TEPETLAXTOC':'TEPETLAOXTOC','TEPOZOTLAN':'TEPOTZOTLÁN','TEPOZTLAN':'TEPOTZOTLÁN','TEQUISQUIAC':'TEQUIXQUIAC','TEXCATITLAN':'TEXCALTITLÁN','TIAGUISTENGO':'TIANGUISTENCO','TIANGUISTENGO':'TIANGUISTENCO',
'TLAMANALCO':'TLALMANALCO','TOLUCA DE LERDO':'TOLUCA','TZOLOTEPEC':'OTZOLOTEPEC','VALLE DE CHALCO':'VALLE DE CHALCO SOLIDARIDAD','ZICANTEPEC':'ZINACANTEPEC','ZUMPANGO DE REYES':'ZUMPANGO',
'TEPETLIXCA':'TEPETLIXPA','TEPETIXTLA':'TEPETLIXPA','TEQUISISTLAN':'TEZOYUCA','LOS REYES':'LA PAZ','SANTA MARIA NORTE':'MALINALCO','SAN PEDRO TLATLAX':'TEMASCALTEPEC',
'ARAGON':'ECATEPEC DE MORELOS','CENTER DE KM':'TECÁMAC','COACALCO DE FRANCISCO':'COACALCO DE BERRIOZÁBAL','COSMOPOL':'COACALCO DE BERRIOZÁBAL','ECATEPEC DE GONZALES':'ECATEPEC DE MORELOS',
'ECATEPEC DE LT':'ECATEPEC DE MORELOS','ECATEPEC DE Y':'ECATEPEC DE MORELOS','GUADALUPE':'ATIZAPÁN DE ZARAGOZA','IXTAPALUCA DE BARBARA':'IXTAPALUCA','JOYA':'CUAUTITLÁN','MAZO DE MAZO':'TOLUCA',
'METEPEC DE CP':'METEPEC','MIGUEL DE AVENIDA':'CUAUTITLÁN IZCALLI','MORELOS DE STA':'ECATEPEC DE MORELOS','MULTIPLAZA':'ATIZAPÁN DE ZARAGOZA','REMEDIOS':'TLALNEPANTLA DE BAZ','SANTIN':'TOLUCA',
'SATELITE':'NAUCALPAN DE JUÁREZ','SANTA ANA JILOTZINGO':'OTZOLOTEPEC','SANTA MARIA RAYON':'SANTA MARÍA RAYÓN','IXTAPAN DE LA SAL':'IXTAPAN DE LA SAL','SAN JUAN TEOTIHUACAN':'TEOTIHUACÁN','MAZATEPEC':None,'----------':None}
d=pd.read_csv('raw.csv',dtype=str)
d=d[d.ENTIDAD.notna()].copy()
d.loc[d.NUM.isna(),'NUM']='2450'
d['CATEGORIA']=d.CATEGORIA.map({'Alimentacio_n':'Alimentación','Asesori_a_y_servicios_legales':'Asesoría y servicios legales','Educacio_n__recreacio_n_y_cultura':'Educación, recreación y cultura','Predial':'Predial','Salud':'Salud','Transporte':'Transporte','Vestido_y_hogar':'Vestido y hogar'})
d=d.fillna('')
def pct(s):
    v=[float(x) for x in re.findall(r'(\d+(?:\.\d+)?)\s*%',s)]
    return max(v) if v else None
d['DESC_MAX_%']=d.DESCUENTO.map(pct)
d['DESC_MIN_%']=d.DESCUENTO.map(lambda s: min([float(x) for x in re.findall(r'(\d+(?:\.\d+)?)\s*%',s)] or [float('nan')]))
d['CP']=d.DOMICILIO.str.extract(r'C\.?\s*P\.?\s*:?\s*(\d{5})')[0].fillna(d.DOMICILIO.str.extract(r'CP\s*(\d{5})')[0])
d.to_csv('full_clean.csv',index=False)
f=d[d.ENTIDAD.isin(['ESTADO DE MÉXICO','CIUDAD DE MÉXICO'])].copy()
def norm(m):
    s=strip(m)
    if s in ALIAS: return ALIAS[s]
    if s in KEY: return KEY[s]
    return '??'+m
f['MUNICIPIO_NORM']=f.MUNICIPIO.map(norm)
# fix by CP where name blank or obviously wrong
f.loc[f.DOMICILIO.str.contains('C.P. 55717'),'MUNICIPIO_NORM']='COACALCO DE BERRIOZÁBAL'
print('unmapped:',f.MUNICIPIO_NORM[f.MUNICIPIO_NORM.astype(str).str.startswith('??')].value_counts().to_dict())
print('none:',f[f.MUNICIPIO_NORM.isna()][['NUM','MUNICIPIO','NOMBRE','DOMICILIO','CATEGORIA']].to_string())
f['MIN_AUTO_EST']=f.MUNICIPIO_NORM.map(lambda m: Z.get(m,(None,''))[0])
f['RUTA_PRINCIPAL']=f.MUNICIPIO_NORM.map(lambda m: Z.get(m,(None,''))[1])
f=f.sort_values(['MIN_AUTO_EST','DESC_MAX_%','MUNICIPIO_NORM','NOMBRE'],ascending=[True,False,True,True],na_position='last')
f.to_csv('cdmx_edomex_sorted.csv',index=False)
print(len(f))
