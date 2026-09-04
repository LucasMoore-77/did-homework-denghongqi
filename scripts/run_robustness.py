"""Reproducible synthetic DID checks. Original data are never written."""
from pathlib import Path
import json, hashlib, warnings
import numpy as np
import pandas as pd
from scipy import stats
from linearmodels.panel import PanelOLS
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)

def fit(d, terms=('digital','capital_intensity'), y='log_tfp', clusters=('firm_id',), extra=None):
    d=d.copy().set_index(['firm_id','year']).sort_index()
    X=d[list(terms)].copy()
    if extra is not None:
        for cols in extra:
            # Omit one category and one year; main effects already absorbed by FE.
            frame=d.reset_index(); cat,time=cols
            for level in sorted(frame[cat].unique())[1:]:
                for year in sorted(frame[time].unique())[1:]:
                    X[f'{cat}_{level}_{year}']=((frame[cat]==level)&(frame[time]==year)).to_numpy(dtype=float)
    c=pd.DataFrame(index=d.index)
    for name in clusters:
        vals=d.index.get_level_values(name) if name in d.index.names else d[name]
        c[name]=pd.Categorical(vals).codes
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        m=PanelOLS(d[y],X,entity_effects=True,time_effects=True,drop_absorbed=True).fit(cov_type='clustered',clusters=c,auto_df=False,count_effects=True,group_debias=True)
    return m,min(c.nunique())-1

def row(d,m,df,term='digital',test='baseline',spec='baseline'):
    b=float(m.params[term]);se=float(np.sqrt(m.cov.loc[term,term]));p=float(2*stats.t.sf(abs(b/se),df))
    return dict(test=test,spec=spec,term=term,estimate=b,std_error=se,p_value=p,df=int(df),ci_low=b-stats.t.ppf(.975,df)*se,ci_high=b+stats.t.ppf(.975,df)*se,n_obs=int(m.nobs),n_firms=d.firm_id.nunique(),treated_firms=d.groupby('firm_id').treated.max().sum(),control_firms=(1-d.groupby('firm_id').treated.max()).sum())

def placebo(d, B=300, seed=825200520):
    rng=np.random.default_rng(seed);ids=d.firm_id.unique();nt=int(d.groupby('firm_id').treated.max().sum());rows=[]
    for b in range(B):
        z=d.copy();pick=rng.choice(ids,nt,replace=False);z['pseudo']=z.firm_id.isin(pick).astype(int)*(z.year>=2020)
        try:
            m,df=fit(z,('pseudo','capital_intensity'));rr=row(z,m,df,'pseudo','R2',f'draw_{b+1}');rr['error']=''
        except Exception as e:
            rr=dict(test='R2',spec=f'draw_{b+1}',estimate=np.nan,error=str(e))
        rr['draw']=b+1;rows.append(rr)
    return pd.DataFrame(rows)

def main():
    path=ROOT/'data/raw/digital_transformation_firm_panel.csv';sha=hashlib.sha256(path.read_bytes()).hexdigest();d=pd.read_csv(path)
    assert not d.duplicated(['firm_id','year']).any() and not d.isna().any().any()
    assert (d.digital==d.treated*(d.year>=2020)).all()
    assert d.groupby('firm_id').year.nunique().eq(9).all()
    base=d[d.year<2020].groupby('firm_id')[['firm_size','managerial_capability']].mean()
    d['size_pre']=d.firm_id.map(base.firm_size);d['cap_pre']=d.firm_id.map(base.managerial_capability)
    d['cap_centered']=d.cap_pre-base.managerial_capability.mean()
    d['cap_intensity']=(d.cap_pre-base.managerial_capability.min())/(base.managerial_capability.max()-base.managerial_capability.min())
    rows=[];meta={}
    def add(z,test,spec,terms=('digital','capital_intensity'),term='digital',y='log_tfp',clusters=('firm_id',),extra=None):
        m,df=fit(z,terms,y,clusters,extra);rr=row(z,m,df,term,test,spec);rows.append(rr);return m,df
    bm,bdf=add(d,'baseline','firm_cluster')
    pd.DataFrame([rows[-1]]).to_csv(OUT/'baseline_panel.csv',index=False)
    # Event study omits 2019. Never use the control sentinel relative_year=-99.
    et=[]
    for year in range(2016,2025):
        if year==2019:continue
        name=f'event_{year}';d[name]=d.treated*(d.year==year);et.append(name)
    em,edf=fit(d,et+['capital_intensity']);pre=[f'event_{x}' for x in [2016,2017,2018]]
    b=em.params.loc[pre].to_numpy();v=em.cov.loc[pre,pre].to_numpy();f=float(b@np.linalg.solve(v,b)/3)
    meta['R1']={'F':f,'df_num':3,'df_den':edf,'p_value':float(stats.f.sf(f,3,edf))}
    ev=[]
    for yr in range(2016,2025):
        if yr==2019:ev.append(dict(year=yr,event_time=-1,estimate=0,std_error=0,ci_low=0,ci_high=0,p_value=np.nan));continue
        rr=row(d,em,edf,f'event_{yr}','R1',str(yr));rr.update(year=yr,event_time=yr-2020);ev.append(rr)
    ev=pd.DataFrame(ev);ev.to_csv(OUT/'R1_event_study.csv',index=False)
    fig,ax=plt.subplots(figsize=(7.2,4));ax.errorbar(ev.event_time,ev.estimate,yerr=ev.ci_high-ev.estimate,fmt='o-',color='#24566c',capsize=3);ax.axhline(0,color='grey',lw=.7);ax.axvline(-.5,color='grey',ls='--');ax.set(xlabel='Years relative to 2020 (2019 omitted)',ylabel='Log TFP coefficient');fig.tight_layout();fig.savefig(OUT/'digital_event_study.png',dpi=190);plt.close(fig)
    means=d.groupby(['year','treated']).log_tfp.mean().unstack();means.to_csv(OUT/'pretrend_means.csv')
    fig,ax=plt.subplots(figsize=(7.2,4));means.rename(columns={0:'Control',1:'Treated'}).plot(ax=ax,marker='o');ax.set(ylabel='Mean log TFP',xlabel='Year');fig.tight_layout();fig.savefig(OUT/'digital_parallel_trends.png',dpi=190);plt.close(fig)
    pl=placebo(d);pl.to_csv(OUT/'R2_bare_draws.csv',index=False);valid=pl.estimate.dropna();tail=int((valid.abs()>=abs(bm.params.digital)).sum())
    meta['R2_bare']={'B':300,'seed':825200520,'success':len(valid),'failures':int(pl.estimate.isna().sum()),'mean':valid.mean(),'sd':valid.std(),'q025':valid.quantile(.025),'q975':valid.quantile(.975),'tail_count':tail,'naive_tail_rate':tail/len(valid)}
    fig,ax=plt.subplots(figsize=(7.2,4));ax.hist(valid,bins=24,color='#78a9b5',edgecolor='white');ax.axvline(bm.params.digital,color='#a44231',label='Observed coefficient');ax.legend();ax.set(xlabel='Placebo coefficient',ylabel='Count');fig.tight_layout();fig.savefig(OUT/'R2_placebo.png',dpi=190);plt.close(fig)
    assert (d.labor_productivity>0).all();d['log_lp']=np.log(d.labor_productivity);add(d,'R3','log_labor_productivity',y='log_lp')
    add(d,'R4','no_controls',terms=('digital',));add(d,'R4','full_controls_absorbed',terms=('digital','capital_intensity'))
    add(d,'R4','add_firm_size',terms=('digital','capital_intensity','firm_size'))
    for cluster in [('industry',),('province',),('firm_id','year')]:add(d,'R5','+'.join(cluster),clusters=cluster)
    lo,hi=d.log_tfp.quantile([.01,.99]);d['winsor_y']=d.log_tfp.clip(lo,hi);meta['R6']={'low':lo,'high':hi,'changed':int((d.winsor_y!=d.log_tfp).sum())};add(d,'R6','winsor_1_99',y='winsor_y')
    add(d[d.industry!='electronics'],'R7','drop_electronics');qlo,qhi=base.firm_size.quantile([.05,.95]);add(d[d.size_pre.between(qlo,qhi)],'R7','trim_size_firms_5_95');add(d[d.year.between(2018,2022)],'R7','window_2018_2022')
    meta['R7']={'size_low':qlo,'size_high':qhi,'full_event_post_2020_2022_mean':float(em.params[[f'event_{y}' for y in [2020,2021,2022]]].mean()),'full_event_post_2020_2024_mean':float(em.params[[f'event_{y}' for y in range(2020,2025)]].mean())}
    d['intensity']=d.digital*d.cap_intensity;add(d,'T1','minmax_capability_proxy',terms=('intensity','capital_intensity'),term='intensity');meta['T1']={'cap_min':base.managerial_capability.min(),'cap_max':base.managerial_capability.max(),'scale':'one unit of min-max proxy; not binary ATT'}
    d['large']=(d.size_pre>base.firm_size.median()).astype(int)
    for typ,dd,group in [('industry',d[d.industry.isin(['electronics','textile'])].copy(),'electronics'),('ownership',d.copy(),'soe'),('size',d.copy(),'large')]:
        dd['group']=(dd.industry=='electronics').astype(int) if typ=='industry' else dd[group]
        for g in [0,1]:add(dd[dd.group==g],'T2',f'{typ}_group{g}')
        dd['diff']=dd.digital*dd.group;dd['cap_g']=dd.capital_intensity*dd.group
        add(dd,'T2',f'{typ}_difference',terms=('digital','diff','capital_intensity','cap_g'),term='diff',extra=[('group','year')])
    d['interaction']=d.digital*d.cap_centered
    m,df=add(d,'T3','capability_interaction',terms=('digital','interaction','capital_intensity'),term='interaction');rows.append(row(d,m,df,'digital','T3','digital_at_mean_capability'))
    add(d,'T4','industry_year',extra=[('industry','year')]);add(d,'T4','industry_province_year',extra=[('industry','year'),('province','year')])
    for industry in sorted(d.industry.unique()):add(d[d.industry!=industry],'T5',f'drop_{industry}')
    res=pd.DataFrame(rows)
    from statsmodels.stats.multitest import multipletests
    idx=res.index[(res.test=='T2')&res.spec.str.endswith('difference')];res.loc[idx,'p_holm']=multipletests(res.loc[idx,'p_value'],method='holm')[1]
    res.to_csv(OUT/'all_results.csv',index=False)
    for name,rr in res.groupby('test'):rr.to_csv(OUT/f'{name}_results.csv',index=False)
    meta['data']={'n_obs':len(d),'n_firms':d.firm_id.nunique(),'n_treated':int(d.groupby('firm_id').treated.max().sum()),'n_control':int((1-d.groupby('firm_id').treated.max()).sum()),'sha256':sha,'absorbed_controls':['export_share','soe'],'inference':'CR1 group_debias, absorbed FE counted; t(min clusters-1) for displayed p/CI'}
    assert sha==hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT/'diagnostics.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2,default=float))
    print(res[['test','spec','estimate','std_error','p_value','n_obs']].to_string(index=False));print(json.dumps(meta,ensure_ascii=False,indent=2,default=float))
if __name__=='__main__':main()
