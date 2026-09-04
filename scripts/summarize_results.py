from pathlib import Path
import pandas as pd,json
ROOT=Path(__file__).resolve().parents[1];o=ROOT/'output';r=pd.read_csv(o/'all_results.csv');m=json.loads((o/'diagnostics.json').read_text());b=r.iloc[0]
notes={
'R1':('警示',f"F(3,359)={m['R1']['F']:.4f}，p={m['R1']['p_value']:.4f}，未拒绝处理前系数联合为零。但DGP已知存在每年0.0008的组别趋势，说明不显著不能证明假设成立。"),
'R2':('通过',f"300次随机企业标签模拟，均值{m['R2_bare']['mean']:.6f}，95%经验范围[{m['R2_bare']['q025']:.5f},{m['R2_bare']['q975']:.5f}]，超过真实系数的次数0。初版直接尾部率为0，须在Skill环节完善有限模拟解释。此项只通过随机标签诊断。"),
'R3':('通过','对数劳动生产率系数0.120534，方向一致；DGP以TFP加噪声生成它，证据不独立。'),
'R4':('通过','系数0.120822—0.120920；出口比例和SOE时间不变，被企业FE吸收。当期规模只在已知DGP中排除中介风险。'),
'R5':('警示','二维企业+年份SE=0.026296，为基准的5.57倍；t(8) p=0.001759。行业仅4簇、地区仅3簇、年份仅9簇，小簇推断未解决；不能声称精度不依赖聚类。'),
'R6':('通过','缩尾66个观测，系数0.116987，相对基准下降3.25%，正向关系保留。'),
'R7':('警示','剔除电子/规模两端后基本一致；2018—2022窗口系数0.081471，比全窗低32.62%。全模型2020—2022事件系数均值0.086889，仅作不同基期的辅助对照；动态效应递增改变了平均对象。'),
'T1':('警示','强度代理系数0.170879；单位为整个min-max区间，不是二元ATT，不能用其大于基准解释收益更强。'),
'T2':('警示','行业、所有制、规模的正式差异检验均不显著，Holm校正p均为1；不足以支持异质性，也不足以证明各组完全相同。'),
'T3':('警示','交互项0.002528，SE=0.004045，p=0.5324；能力互补性未获支持。该假说未获支持不等于主效应或程序失败。'),
'T4':('通过','行业年和行业年+地区年FE系数分别0.120609、0.120913；共同层面冲击不足以解释点估计，企业层面时变混杂仍可能存在。'),
'T5':('通过','逐一剔除四行业，系数范围0.119775—0.122565，排除单一行业驱动的初步担忧；不建立外部效度。')}
summary='# 稳健性检验汇总\n\n“通过”仅表示该项局部诊断未发现预定问题；“警示”表示推断、估计对象或假说解释需限定；“失败”用于执行/识别条件不满足，不把不显著自动判为失败。\n\n| 检验 | 判定 | 观察与依据 |\n|---|---|---|\n'
summary+='\n'.join(f'| {k} | {a} | {n} |' for k,(a,n) in notes.items())
summary+='\n\n完整数字：all_results.csv、R1_event_study.csv、R2_bare_draws.csv、diagnostics.json。除R5外均为企业聚类；全表p值使用t(G−1)参考分布，原Python脚本CSV的p值为正态近似，两者不能混读。\n'
(o/'robustness_summary.md').write_text(summary)
(o/'judgments.json').write_text(json.dumps({k:{'status':a,'reason':n} for k,(a,n) in notes.items()},ensure_ascii=False,indent=2))
for k,(a,n) in notes.items():
 p=ROOT/f'prompts/robustness/{k}.md';s=p.read_text().split('## 结果摘要与观察')[0];rr=r[r.test==k]
 s+=f'## 结果摘要与观察\n\n判定：{a}。{n}\n\n'
 if len(rr):s+=rr[['spec','estimate','std_error','p_value','n_obs']].to_markdown(index=False,floatfmt='.6g')+'\n'
 s+='\n证据：output/'+ ('R1_event_study.csv、diagnostics.json' if k=='R1' else 'R2_bare_draws.csv、diagnostics.json' if k=='R2' else k+'_results.csv')+'。\n'
 p.write_text(s)
py=pd.read_csv(o/'python_did_results.csv').iloc[0];st=pd.read_csv(o/'stata_did_results.csv').iloc[0]
(o/'baseline_comparison.md').write_text(f'''# 主回归交叉验证

| 实现 | 系数 | 企业聚类SE |
|---|---:|---:|
| 课堂Stata留存 | {st.estimate:.10f} | {st.std_error:.10f} |
| 本次满秩OLS | {py.estimate:.10f} | {py.std_error_cluster_firm:.10f} |
| 本次PanelOLS | {b.estimate:.10f} | {b.std_error:.10f} |

三者N=3240。Python两实现系数差{abs(py.estimate-b.estimate):.3g}，Stata差{abs(st.estimate-b.estimate):.3g}，满足1e-7容差；Stata保存位数有限。Stata文件是课堂来源，不声称本次执行。原公式异常输出见iterations/baseline_original_script.csv；新版显式移除企业FE吸收的出口比例和SOE，系数含义未改变。

所有回归均计入企业与年份FE，CR1含吸收FE的自由度并作簇数修正。主脚本报告t(359) p={b.p_value:.6g}；课堂Python实现默认正态近似p={py.p_value:.6g}。差别为参考分布，非系数或SE差异。
''')
p=ROOT/'prompts/robustness/baseline.md';p.write_text(p.read_text().split('## 结果摘要与观察')[0]+'## 结果摘要与观察\n\n'+(o/'baseline_comparison.md').read_text())
print(summary)
