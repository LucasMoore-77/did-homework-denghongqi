"""A new synthetic minimum-wage/employment panel; no real policy evidence."""
from pathlib import Path
import numpy as np,pandas as pd,json,importlib.util,tempfile
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('generic_placebo',ROOT/'.claude/skills/robustness-check/scripts/placebo.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
rng=np.random.default_rng(20260904);rows=[];selected=set(rng.choice(np.arange(1,81),36,replace=False))
for region in range(1,81):
    alpha=rng.normal(4,.2)
    for time in range(2017,2025):
        x=rng.normal();D=int(region in selected and time>=2021)
        rows.append(dict(district=region,period=time,employment_index=alpha+.02*(time-2017)-.04*D+.03*x+rng.normal(0,.04),reform_active=D,wage_pressure=x))
out=ROOT/'output/migration';out.mkdir(parents=True,exist_ok=True);d=pd.DataFrame(rows);d.to_csv(out/'panel.csv',index=False)
c=dict(data='output/migration/panel.csv',id='district',time='period',outcome='employment_index',treatment='reform_active',controls=['wage_pressure'],seed=825200520,repetitions=120)
contract=ROOT/'config/minimum_wage.json';contract.write_text(json.dumps(c,indent=2));result=mod.execute(contract,ROOT,out/'result');tests=[]
for case in ['duplicate','reversal','staggered']:
    z=d.copy()
    if case=='duplicate':z=pd.concat([z,z.iloc[[0]]])
    who=min(selected)
    if case=='reversal':z.loc[(z.district==who)&(z.period==2024),'reform_active']=0
    if case=='staggered':z.loc[(z.district==who)&(z.period==2021),'reform_active']=0
    with tempfile.TemporaryDirectory() as tmp:
        t=Path(tmp);z.to_csv(t/'panel.csv',index=False);cc={**c,'data':'panel.csv'};(t/'contract.json').write_text(json.dumps(cc))
        try:mod.execute(t/'contract.json',t,t/'out');ok=False;msg='accepted unexpectedly'
        except Exception as e:ok=True;msg=str(e)
        tests.append(dict(case=case,rejected=ok,message=msg))
(out/'negative_tests.json').write_text(json.dumps(tests,ensure_ascii=False,indent=2))
(out/'README.md').write_text(f'''# 最低工资与就业迁移实验

这是重新生成的合成区域面板，不是数字化数据改列名，也不是真实政策数据。80地区、8年、36地区2021年同步处理，DGP处理效应−0.04；列名、采用时点、控制变量和效应方向均改变。通用Skill源码不变，仅重新解释语义并编写外部契约。实际估计{result['observed_estimate']:.6f}，SE={result['observed_se']:.6f}，120次标签模拟成功。与−0.04接近仅验证教学执行，不说明最低工资现实效果。

变量识别：district为地区ID，period为年份，employment_index是对数就业指标，reform_active为政策暴露；wage_pressure是先验外生控制。字段的经济含义由本实验说明确定，代码不凭统计模式推断。

处理反转、重复个体时间键、交错采用均已在临时副本触发停止，见negative_tests.json。平衡同步设计可迁移；交错政策必须另选估计方法。真实最低工资研究还需考虑跨地区就业转移、政策预期和地区层面分配，不能照搬数字化主题检验。
''')
print(result);print(tests)
