from pathlib import Path
import json,hashlib,importlib.metadata
import numpy as np,pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups
from evaluate import validate
ROOT=Path(__file__).resolve().parents[1];o=ROOT/'output';r=validate(ROOT);d=pd.read_csv(ROOT/'data/raw/digital_transformation_firm_panel.csv')
m=smf.ols('log_tfp ~ digital + capital_intensity + C(firm_id) + C(year)',d).fit()
v=cov_cluster_2groups(m,d.firm_id,d.year)[0];i=list(m.params.index).index('digital');se=float(np.sqrt(v[i,i]));ref=r[(r.test=='R5')&(r.spec=='firm_id+year')].iloc[0]
assert abs(se-ref.std_error)<1e-9
assert abs(m.params.digital-r.iloc[0].estimate)<1e-10
assert (r[r.test=='R7'].n_obs.values==np.array([2376,2916,1800])).all()
assert np.allclose(r[(r.test=='T2')&r.spec.str.endswith('difference')].p_holm,1)
assert (d['digital']==d['treated_post']).all()
rep={'status':'passed','independent_twfe_coefficient':m.params.digital,'independent_two_way_se':se,'panel_two_way_se':ref.std_error,'two_way_se_difference':abs(se-ref.std_error),'raw_sha256':hashlib.sha256((ROOT/'data/raw/digital_transformation_firm_panel.csv').read_bytes()).hexdigest(),'checks':['full-rank OLS matches PanelOLS','CGM covariance matches two-way PanelOLS','sample counts','Holm adjustment','treatment aliases','evaluation evidence gate']}
(o/'verification.json').write_text(json.dumps(rep,indent=2));print(rep)
versions={k:importlib.metadata.version(k) for k in ['numpy','pandas','scipy','statsmodels','linearmodels','matplotlib','tabulate','python-docx','pypdf','pyyaml']}
(ROOT/'requirements.txt').write_text('\n'.join(f'{k}=={v}' for k,v in versions.items())+'\n');(o/'environment.json').write_text(json.dumps(versions,indent=2))
