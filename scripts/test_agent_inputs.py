from pathlib import Path
import tempfile,shutil,json,argparse
import pandas as pd
from evaluate import validate
ROOT=Path(__file__).resolve().parents[1]
def run():
    results=[]
    for case in ['valid','missing_event_file','changed_baseline','missing_spec','invalid_p','duplicate_row']:
        with tempfile.TemporaryDirectory() as tmp:
            t=Path(tmp);shutil.copytree(ROOT/'config',t/'config',ignore=shutil.ignore_patterns('._*'));shutil.copytree(ROOT/'output',t/'output',ignore=shutil.ignore_patterns('._*'));shutil.copytree(ROOT/'data',t/'data',ignore=shutil.ignore_patterns('._*'))
            f=t/'output/all_results.csv';d=pd.read_csv(f)
            if case=='missing_event_file':(t/'output/R1_event_study.csv').unlink()
            if case=='changed_baseline':d.loc[d.test=='baseline','estimate']+=.1
            if case=='missing_spec':d=d[~((d.test=='R7')&(d.spec=='window_2018_2022'))]
            if case=='invalid_p':d.loc[d.index[0],'p_value']=1.2
            if case=='duplicate_row':d=pd.concat([d,d.iloc[[0]]])
            d.to_csv(f,index=False)
            try:validate(t);accepted=True;error=''
            except Exception as e:accepted=False;error=str(e)
            results.append({'case':case,'accepted':accepted,'expected_acceptance':case=='valid','correct':accepted==(case=='valid'),'message':error})
    return results
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();out=run();Path(a.output).write_text(json.dumps(out,ensure_ascii=False,indent=2));print(out)
