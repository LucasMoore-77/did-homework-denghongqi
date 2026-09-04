"""Generic simultaneous-adoption panel placebo engine; semantics supplied in contract."""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
import pandas as pd
from scipy import stats
from linearmodels.panel import PanelOLS

def execute(contract, root, out):
    c=json.loads(Path(contract).read_text());root=Path(root);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    path=root/c['data'];sha=hashlib.sha256(path.read_bytes()).hexdigest();d=pd.read_csv(path)
    id,t,y,D=[c[k] for k in ['id','time','outcome','treatment']];controls=c['controls'];d=d.sort_values([id,t])
    assert not d.duplicated([id,t]).any(),'duplicate id-time'
    assert not d[[id,t,y,D]+controls].isna().any().any(),'missing inputs'
    assert set(d[D].unique())<={0,1},'treatment must be binary'
    assert (d.groupby(id)[D].diff().dropna()>=0).all(),'reversal'
    cohort=d[d[D]==1].groupby(id)[t].min();assert cohort.nunique()==1,'staggered treatment requires another estimator'
    start=cohort.iloc[0];assert start>d[t].min(),'no pre-period'
    assert d.groupby(id)[t].apply(tuple).nunique()==1,'helper currently requires balanced panel'
    treated=d.groupby(id)[D].max();assert 0<treated.sum()<len(treated),'need both treated and never-treated'
    absorbed=[x for x in controls if d.groupby(id)[x].nunique().max()==1];controls=[x for x in controls if x not in absorbed]
    idx=d.set_index([id,t]);rng=np.random.default_rng(c['seed']);ids=treated.index.to_numpy();nt=int(treated.sum())
    def model(z):
        X=idx[controls].copy();X.insert(0,'exposure',np.asarray(z))
        fit=PanelOLS(idx[y],X,entity_effects=True,time_effects=True).fit(cov_type='clustered',cluster_entity=True,auto_df=False,count_effects=True,group_debias=True)
        b=float(fit.params.exposure);se=float(fit.std_errors.exposure);return b,se,float(2*stats.t.sf(abs(b/se),len(ids)-1))
    actual=model(d[D]);rows=[]
    for b in range(c['repetitions']):
        selected=rng.choice(ids,nt,replace=False);pseudo=d[id].isin(selected)*(d[t]>=start)
        try:
            est,se,p=model(pseudo);rows.append(dict(draw=b+1,estimate=est,std_error=se,p_value=p,n_obs=len(d),error=''))
        except Exception as e:rows.append(dict(draw=b+1,estimate=np.nan,error=str(e)))
    draws=pd.DataFrame(rows);draws.to_csv(out/'draws.csv',index=False);vals=draws.estimate.dropna();tail=int((abs(vals)>=abs(actual[0])).sum())
    report={'observed_estimate':actual[0],'observed_se':actual[1],'B':c['repetitions'],'successful':len(vals),'failed':int(draws.estimate.isna().sum()),'tail_count':tail,'tail_rate':tail/len(vals),'mean':vals.mean(),'sd':vals.std(),'q025':vals.quantile(.025),'q975':vals.quantile(.975),'seed':c['seed'],'sha256_before':sha,'sha256_after':hashlib.sha256(path.read_bytes()).hexdigest(),'absorbed':absorbed,'treatment_year':int(start),'treated_units':nt,'control_units':len(ids)-nt,'mapping':{k:c[k] for k in ['id','time','outcome','treatment']}}
    report.update(status='complete' if len(vals)==c['repetitions'] else 'incomplete',
                  smoothed_tail_rate=(tail+1)/(len(vals)+1), resolution=1/(len(vals)+1),
                  tail_probability_upper95=(1-.05**(1/len(vals))) if tail==0 else float(stats.beta.ppf(.95,tail+1,len(vals)-tail)),
                  interpretation='Simulation diagnostic under supplied assignment, not a causal randomization p-value')
    assert report['sha256_before']==report['sha256_after']
    (out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=float));return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('contract');p.add_argument('--root',default='.');p.add_argument('--out',required=True);a=p.parse_args();print(json.dumps(execute(a.contract,a.root,a.out),ensure_ascii=False,indent=2,default=float))
