import pdfplumber, sys, re, pandas as pd, numpy as np, os
GAPS = {}
def file_gaps(p):
    cov=np.zeros(800,int)
    for pg in p.pages[2:]:
        for w in pg.extract_words():
            if w['top']<40 or w['bottom']-w['top']>8: continue
            cov[int(w['x0']):int(w['x1'])+1]+=1
    gaps=[];inz=False
    for x in range(20,300):
        if cov[x]==0 and not inz: s=x; inz=True
        if cov[x]>0 and inz: gaps.append((s,x)); inz=False
    gaps=[g for g in gaps if g[1]-g[0]>=2]
    return [ (a+b)/2 for a,b in gaps[1:4] ]  # num|ent, ent|mun, mun|nom
cols=['NUM','ENTIDAD','MUNICIPIO','NOMBRE','DOMICILIO','TELEFONO','DESCUENTO']
rows=[]; issues=[]
for f in sorted(sys.argv[1:]):
    cat=re.sub(r'^[0-9a-f]+-','',os.path.basename(f)).replace('_oct_26.pdf','')
    p=pdfplumber.open(f)
    b1,b2,b3=file_gaps(p)
    for pi,pg in enumerate(p.pages[2:],start=3):
        hdr=[r for r in pg.rects if r['top']<20 and r['bottom']<45 and r['bottom']-r['top']>10]
        xs=sorted(r['x0'] for r in hdr)
        b4,b5=xs[1],xs[2]
        dh=[w for w in pg.extract_words() if w['top']<40 and w['text'].startswith('DESCUENTO')]
        b6=dh[0]['x0']-8
        bounds=[b1,b2,b3,b4,b5,b6]
        ys=sorted(set([round(r['top'],1) for r in pg.rects if r['top']>=38]+[round(r['bottom'],1) for r in pg.rects if r['top']>=38]+[36.0, pg.height]))
        # merge close ys
        lines=[]
        for y in ys:
            if not lines or y-lines[-1]>3: lines.append(y)
        words=[w for w in pg.extract_words(keep_blank_chars=False,use_text_flow=False) if w['top']>=38 and w['bottom']-w['top']<=8]
        for a,bb in zip(lines[:-1],lines[1:]):
            ws=[w for w in words if a-1<= (w['top']+w['bottom'])/2 < bb]
            if not ws: continue
            if all(w['bottom']-w['top']>8 for w in ws): continue  # state band
            cells={c:[] for c in cols}
            for w in ws:
                xc=(w['x0']+w['x1'])/2
                i=sum(xc>=b for b in bounds)
                if i==5 and w['x1']>bounds[5]+3: i=6
                for b in bounds:
                    if w['x0']<b-2 and b+2<w['x1']: issues.append((cat,pi,w['text'],b))
                cells[cols[i]].append(w)
            moved=True
            while moved:
                moved=False
                for w in list(cells['TELEFONO']):
                    if any(abs(o['top']-w['top'])<1.5 and 0<=o['x0']-w['x1']<6 for o in cells['DESCUENTO']):
                        cells['TELEFONO'].remove(w); cells['DESCUENTO'].append(w); moved=True
            rec={c:' '.join(x['text'] for x in sorted(cells[c],key=lambda w:(round(w['top']),w['x0']))) for c in cols}
            rec['CATEGORIA']=cat; rec['PAGINA']=pi
            rows.append(rec)
df=pd.DataFrame(rows)
df.to_csv('raw.csv',index=False)
print(len(df)); print(df.groupby('CATEGORIA').size())
print('straddle issues',len(issues), issues[:15])
