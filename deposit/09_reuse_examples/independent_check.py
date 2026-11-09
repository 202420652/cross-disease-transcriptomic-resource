#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v15 (G2): independent re-implementation check, a substantive reuse example, and the reference metadata
for the existing harmonisation resources the reviews asked us to position against.

Nothing here imports the project pipeline: the check recomputes an effect, a pooled estimate and a
multiplicity adjustment from the shipped tables alone, using plain Python.
"""
import csv, json, math, os, subprocess, urllib.parse
V15=r"C:\Users\fengq\Desktop\EGFR\EGFR的v15"; PK=os.path.join(V15,"dataset_package"); OUT=os.path.join(V15,"results")
def rd(p):
    if not os.path.exists(p): return []
    with open(p,encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def wr(rows,p):
    os.makedirs(os.path.dirname(p),exist_ok=True)
    with open(p,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()),lineterminator="\n"); w.writeheader(); w.writerows(rows)
# ---------- 1. independent check (pure Python) ----------
PC=rd(os.path.join(PK,"07_estimates","per_cohort_effects.csv"))
META=rd(os.path.join(PK,"07_estimates","meta_primary_reml_knha.csv"))
num=lambda v: float(v) if v not in (None,"","nan","NA","not applicable") else None
def hedges_smdh(m1,sd1,n1,m2,sd2,n2):
    df=n1+n2-2; sp=math.sqrt(((n1-1)*sd1**2+(n2-1)*sd2**2)/df)
    d=(m1-m2)/sp; J=1-3/(4*df-1)
    yi=J*d; v=(n1+n2)/(n1*n2)+yi**2/(2*(n1+n2))
    return yi, v
def reml_hk(y, v):
    k=len(y); assert k>=2
    w=[1/x for x in v]; mu=sum(a*b for a,b in zip(w,y))/sum(w); tau2=0.0
    for _ in range(200):
        tau2=max(0.0, sum(wi*((yi-mu)**2-vi) for wi,yi,vi in zip(w,y,v))/sum(w))
        w=[1/(vi+tau2) for vi in v]; new=sum(a*b for a,b in zip(w,y))/sum(w)
        if abs(new-mu)<1e-13: mu=new; break
        mu=new
    se=math.sqrt(1/sum(w)); q=sum(wi*(yi-mu)**2 for wi,yi in zip(w,y)); se_hk=math.sqrt(q/((k-1)*sum(w)))
    from statistics import NormalDist
    t=abs(mu/se_hk) if se_hk>0 else 0.0
    p=2*(1-NormalDist().cdf(t))
    return mu, se_hk, p, tau2
# (a) one cohort effect recomputed from first principles where the means and SDs are shipped
means=rd(os.path.join(OUT,"v13_percohort_effects_complete.csv")) or rd(os.path.join(PK,"07_estimates","per_cohort_effects.csv"))
cols=set(means[0].keys()) if means else set()
checks=[]
if {"mean_case","sd_case","n_case","mean_control","sd_control","n_control"} <= cols:
    for r in means[:3]:
        yi,v=hedges_smdh(num(r["mean_case"]),num(r["sd_case"]),int(r["n_case"]),
                         num(r["mean_control"]),num(r["sd_control"]),int(r["n_control"]))
        checks.append(dict(check="SMDH recomputed from means and SDs (independent implementation)",
                           state=f"{r['disease']}/{r['feature']}/{r['accession']}",
                           shipped=round(num(r["yi"]),10), independent=round(yi,10),
                           absolute_difference=abs(num(r["yi"])-yi), tolerance=1e-6,
                           within_tolerance=abs(num(r["yi"])-yi)<=1e-6))
else:
    checks.append(dict(check="SMDH recomputation skipped: means and SDs are not shipped in the per-cohort table",
                       state="",shipped="",independent="",absolute_difference="",tolerance=1e-6,within_tolerance=False))
# (b) one pooled state recomputed with REML + Hartung-Knapp
target=None
for r in META:
    if r.get("pooled")=="yes" and int(r["k"])>=3:
        sub=[x for x in PC if x["disease"]==r["feature"] or True]
        tgt=[x for x in PC if x.get("disease")==r.get("disease") and x.get("feature")==r.get("feature") and num(x.get("yi")) is not None]
        if len(tgt)>=3: target=(r,tgt); break
if target:
    r,tgt=target
    y=[num(x["yi"]) for x in tgt]; v=[num(x["vi"]) for x in tgt]
    mu,se,p,tau2=reml_hk(y,v)
    checks.append(dict(check="REML + Hartung-Knapp pooled estimate recomputed independently",
                       state=f"{r['disease']}/{r['feature']} (k={r['k']})",
                       shipped=f"est {r['est']}, se {r['se']}, p {r['p']}",
                       independent=f"est {mu:.6f}, se {se:.6f}, p {p:.6g}",
                       absolute_difference=f"est {abs(num(r['est'])-mu):.2e}, se {abs(num(r['se'])-se):.2e}",
                       tolerance=1e-6, within_tolerance=abs(num(r["est"])-mu)<=1e-6))
# (c) Benjamini-Hochberg recomputation for one family
qc=rd(os.path.join(OUT,"v13_qc_coverage_threshold_sensitivity.csv"))
if qc:
    ps=[num(r.get("p")) for r in qc if num(r.get("p")) is not None]
    order=sorted(range(len(ps)),key=lambda i:ps[i]); m=len(ps); adj=[0.0]*m; run=1.0
    for j in range(m-1,-1,-1):
        run=min(run, ps[order[j]]*m/(j+1)); adj[j]=run
    got=[adj[pos] for pos in range(m)]
    shipped=[num(r.get("fdr")) for r in qc if num(r.get("p")) is not None]
    diff=max(abs(a-b) for a,b in zip(got,shipped)) if shipped else float("nan")
    checks.append(dict(check="Benjamini-Hochberg adjustment recomputed for one family",
                       state=f"coverage-threshold sensitivity family (n={m})",shipped="shipped fdr column",
                       independent="plain-Python step-up",absolute_difference=f"{diff:.2e}",tolerance=1e-6,
                       within_tolerance=diff<=1e-6))
wr(checks, os.path.join(PK,"08_qc","qc_independent_reimplementation.csv")); wr(checks, os.path.join(OUT,"v15_independent_check.csv"))
ok=sum(1 for c in checks if c["within_tolerance"])
print(f"independent check: {ok}/{len(checks)} within 1e-6")
for c in checks: print("  -",c["check"][:72],"|",c["absolute_difference"])
# ship the script
open(os.path.join(PK,"09_reuse_examples","independent_check.py"),"w",encoding="utf-8").write(
    open(os.path.join(V15,"scripts","G2_v15_independent_and_example4.py"),encoding="utf-8").read())
# ---------- 2. substantive reuse example: cross-context signals ----------
sig=[]
for r in META:
    if r.get("pooled")!="yes": continue
    e=num(r.get("est")); f=num(r.get("fdr"))
    if e is None or f is None: continue
    sig.append(dict(disease=r["disease"], module=r["feature"], k=r["k"], est=e, fdr=f,
                    direction="up in disease" if e>0 else "down in disease"))
by_mod={}
for s in sig: by_mod.setdefault(s["module"],[]).append(s)
rows=[]
for mod,items in by_mod.items():
    up=[i for i in items if i["est"]>0 and i["fdr"]<0.05]; dn=[i for i in items if i["est"]<0 and i["fdr"]<0.05]
    row=dict(module=mod, contexts_pooled=len(items),
             contexts_significant_up=";".join(i["disease"] for i in up),
             contexts_significant_down=";".join(i["disease"] for i in dn),
             n_up=len(up), n_down=len(dn))
    row["same_sign_consistency"]=("mixed" if up and dn else ("consistent up" if up else ("consistent down" if dn else "none significant")))
    rows.append(row)
wr(sorted(rows,key=lambda r:-(r["n_up"]+r["n_down"])), os.path.join(PK,"09_reuse_examples","example4_cross_context_signals.csv"))
top=[r for r in rows if r["n_up"]>=2 or r["n_down"]>=2]
print("\nexample 4 (cross-context signals):", len(rows),"modules;",len(top),"with a significant effect in at least two contexts")
for r in top[:6]: print(f"  {r['module']}: up in {r['contexts_significant_up'] or '-'} | down in {r['contexts_significant_down'] or '-'}")
# ---------- 3. references for the existing harmonisation resources ----------
def eut(path,**kw):
    url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"+path+"?"+urllib.parse.urlencode(kw)
    return subprocess.run(["curl","-sS","--max-time","60",url],capture_output=True,text=True).stdout
LOOK={"recount3":"recount3 a multi-organ multi-species resource","archs4":"ARCHS4 massively analysis-ready",
      "dee2":"DEE2 the digital expression explorer 2","xena_toil":"Toil enables reproducible open source big data analyses",
      "gtex":"The GTEx Consortium atlas of genetic regulatory effects across human tissues",
      "refinebio":"refine.bio uniform processing of public gene expression data"}
found={}
for k,q in LOOK.items():
    ids=json.loads(eut("esearch.fcgi",db="pubmed",term=q,retmode="json",retmax=3)).get("esearchresult",{}).get("idlist",[])
    if not ids: found[k]=None; print(f"  {k}: NOT FOUND"); continue
    js=json.loads(eut("esummary.fcgi",db="pubmed",id=ids[0],retmode="json") or "{}")
    rec=list((js.get("result") or {}).values())
    rec=[r for r in rec if isinstance(r,dict) and r.get("title")]
    if rec:
        r=rec[0]; a=r.get("authors") or []
        doi=""
        for x in r.get("articleids") or []:
            if x.get("idtype")=="doi": doi=x.get("value","")
        found[k]=dict(pmid=ids[0],first_author=(a[0]["name"] if a else "Unknown"),n_authors=len(a),
                      title=r.get("title").strip().rstrip("."),journal=r.get("source") or "",
                      year=(r.get("pubdate") or "")[:4],volume=r.get("volume") or "",pages=r.get("pages") or "",doi=doi)
        print(f"  {k}: {found[k]['first_author']} {found[k]['year']} {found[k]['journal']} | {found[k]['title'][:60]}")
meta=json.load(open(os.path.join(OUT,"v14_reference_metadata.json"),encoding="utf-8"))
meta.setdefault("crossref",{})
for k,v in found.items():
    if v:
        for uid,s in meta.get("summaries",{}).items():
            pass
        meta["crossref"][f"res_{k}"]=dict(first_author=v["first_author"],n_authors=v["n_authors"],title=v["title"],
            journal=v["journal"],year=v["year"],volume=v["volume"],pages=v["pages"],doi=v["doi"],pmid=v["pmid"])
json.dump(meta, open(os.path.join(OUT,"v14_reference_metadata.json"),"w",encoding="utf-8"), indent=1)
print("\ncomparison resources added to the metadata:", [k for k,v in found.items() if v])
