import pandas as pd, re, json, unicodedata, collections
d=pd.read_csv('full_clean.csv',dtype=str).fillna('')
cm=pd.read_csv('cdmx_edomex_sorted.csv',dtype=str).fillna('')
norm=dict(zip(cm.CATEGORIA+'|'+cm.NUM, cm.MUNICIPIO_NORM))
def strip(s): return ''.join(c for c in unicodedata.normalize('NFD',s) if unicodedata.category(c)!='Mn').upper()
def key(s): return re.sub(r'[^A-Z0-9 ]','',strip(s)).split() and ' '.join(re.sub(r'[^A-Z0-9 ]',' ',strip(s)).split())
R=[ # (section, sub, pattern, categories or None)
('Trámites','Predial y agua',None,['Predial']),
('Trámites','Notarías y testamentos',r'NOTAR|TESTAMENT',None),
('Trámites','Funerarias',r'FUNERA|FUNERAL|VELATORIO|PREVISOR|CREMATOR|CINERARIA|PANTE[OÓ]N',None),
('Cuidar tu salud','Veterinarias',r'VETERIN|MASCOT|CANIN|\bPET\b',None),
('Cuidar tu salud','Ópticas',r'[ÓO]PTI(?!MUS)|VISI[ÓO]N|DEVLYN|OPTOM|OFTALM|LENTES|SALAUNO|\bOJOS?\b',['Salud','Vestido y hogar']),
('Cuidar tu salud','Aparatos auditivos',r'\bAUDI|AUDICI|AUDITIV|GAES|O[ÍI]DO',['Salud','Vestido y hogar']),
('Cuidar tu salud','Dentistas',r'DENT|ODONT|ORTODON',['Salud']),
('Cuidar tu salud','Laboratorios y estudios',r'LABORAT|AN[ÁA]LISIS|DIAGN[ÓO]S|RAYOS|RADIOL|IMAGEN|ULTRASON|TOMOGR|BIOM[ÉE]D',['Salud']),
('Cuidar tu salud','Rehabilitación y fisioterapia',r'REHABILI|FISIO|ATHLOS|QUIROP|TERAPIA',['Salud']),
('Cuidar tu salud','Psicología',r'PSIC|TANAT',['Salud','Educación, recreación y cultura']),
('Cuidar tu salud','Farmacias y naturistas',r'FARMAC|FERMAC|BOTIC|NATURIST|HOMEOP|HERBOL|SIMILARES',['Salud','Alimentación','Vestido y hogar']),
('Cuidar tu salud','Ortopedia y podología',r'ORTOPED|POD[OÓ]L',None),
('Cuidar tu salud','Médicos, clínicas y hospitales',None,['Salud']),
('Salir y divertirte','Restaurantes y cafés',r'RESTAUR|FONDA|COCINA|TAQUER|PIZZ|CAF[ÉE]|MARISQ|ANTOJ|COMIDA|BUFF?ET|LONCH|TORTA|POZOL|BIRRI|CENADUR|COMEDOR|ASADERO|SUSHI|HAMBURG|POLLO|CARNITAS|BARBACOA|MARISCO|ALITAS|TAMAL',['Alimentación','Educación, recreación y cultura']),
('Salir y divertirte','Gimnasios y deporte',r'SMART FIT|\bGYM|GIMNAS|DEPORT|ACU[ÁA]TIC|NATACI|YOGA|\bSPORT|FITNESS|ALBERCA',None),
('Salir y divertirte','Viajes y hoteles',r'VIAJE|TUR[IÍ]S|HOTEL|POSADA|TOUR|EXCURS|BALNEARIO|ECOTUR|AEROV|CAMPAMENT',None),
('Salir y divertirte','Cultura, libros y teatro',r'TEATR|\bCINE\b|MUSEO|CULTUR|\bARTE|DANZA|M[ÚU]SICA|LIBRER|PORR[ÚU]A|AUDITORIO|ESPECT',['Educación, recreación y cultura','Vestido y hogar']),
('Salir y divertirte','Cursos y clases',None,['Educación, recreación y cultura']),
('Viajar y moverte','Transporte',None,['Transporte']),
('Viajar y moverte','Envíos y paquetería',r'ESTAFETA|\bUPS\b|DHL|PAQUETER|MENSAJER|FEDEX|ENV[ÍI]O',None),
('Compras y hogar','Ropa y zapatos',r'ZAPAT|ROPA|BOUTIQUE|MODA|UNIFORM|SUBURBIA|BONETER|TELA|FAJA|CALZADO|JULIO|VESTID|ONENA|NOVEDADES|LENCER',['Vestido y hogar']),
('Compras y hogar','Belleza y estética',r'EST[ÉE]TICA|SAL[ÓO]N|BARBER|\bSPA\b|BELLEZA|U[ÑN]AS|PELUQ|COSM[ÉE]T',None),
('Compras y hogar','Despensa y comida para llevar',None,['Alimentación']),
('Compras y hogar','Hogar, ferretería y más',None,['Vestido y hogar']),
]
def classify(r):
    for sec,sub,pat,cats in R:
        if cats and r.CATEGORIA not in cats: continue
        if pat and not re.search(pat,r.NOMBRE): continue
        return sec,sub
    return 'Compras y hogar','Hogar, ferretería y más'
def pct(s):
    v=[float(x) for x in re.findall(r'(\d+(?:\.\d+)?)\s*%',s)]
    if v: return max(v)
    if re.search(r'GRATIS|SIN COSTO|GRATUIT',s): return 100
    return None
def title(s):
    small={'DE','DEL','LA','LAS','LOS','Y','EL'}
    w=s.lower().split()
    return ' '.join(x if (i>0 and x.upper() in small) else x[:1].upper()+x[1:] for i,x in enumerate(w))
# municipality display
mun=[]
for _,r in d.iterrows():
    m=norm.get(r.CATEGORIA+'|'+r.NUM) if r.ENTIDAD in ('CIUDAD DE MÉXICO','ESTADO DE MÉXICO') else None
    if not m:
        m=r.MUNICIPIO.strip()
        if not re.search('[A-Za-zÁÉÍÓÚÑ]',m): m='SIN MUNICIPIO'
    mun.append(m)
d['MUN']=mun
d['MK']=d.ENTIDAD+'|'+d.MUN.map(key)
disp=d.groupby('MK').MUN.agg(lambda s: collections.Counter(s).most_common(1)[0][0])
d['MUN']=d.MK.map(disp).map(title)
d['EST']=d.ENTIDAD.map(title)
cls=d.apply(classify,axis=1); d['SEC']=[c[0] for c in cls]; d['SUB']=[c[1] for c in cls]
d['PCT']=d.DESCUENTO.map(pct)
print(d.groupby(['SEC','SUB']).size().to_string())
tel=d.TELEFONO.where(~d.TELEFONO.str.fullmatch(r'-+|PENDIENTE'),'')
recs=[[r.EST,r.MUN,title(r.NOMBRE) if r.NOMBRE.isupper() else r.NOMBRE,r.DOMICILIO,t,r.DESCUENTO,None if pd.isna(r.PCT) else r.PCT,r.SEC,r.SUB] for r,t in zip(d.itertuples(),tel)]
json.dump({'cols':['estado','municipio','nombre','domicilio','telefono','descuento','pct','actividad','tipo'],'rows':recs},open('buscador/datos.json','w'),ensure_ascii=False,separators=(',',':'),allow_nan=False)
import os; print(os.path.getsize('buscador/datos.json'))
d[['EST','MUN','NOMBRE','DOMICILIO','TELEFONO','DESCUENTO','PCT','SEC','SUB','CATEGORIA','NUM','PAGINA']].to_csv('INAPAM_directorio_clasificado.csv',index=False,encoding='utf-8-sig')
