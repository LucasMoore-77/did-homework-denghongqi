"""Deterministic evidence checks and report assembly; not an independent LLM call."""
from pathlib import Path
import json,argparse
import pandas as pd

def validate(root):
    o=Path(root)/'output';r=pd.read_csv(o/'all_results.csv')
    assert {'test','spec','estimate','std_error','p_value','n_obs'}<=set(r.columns)
    assert not r.duplicated(['test','spec']).any()
    return r

def report(root):
    root=Path(root);o=root/'output';r=validate(root);b=r[r.test=='baseline'].iloc[0]
    return f'''# DID稳健性综合评估报告

## 1 主结果
合成面板360家企业、3240个观测，处理组151家，对照组209家。企业与年份固定效应，企业聚类：系数{b.estimate:.8f}，SE={b.std_error:.8f}，95%区间[{b.ci_low:.6f},{b.ci_high:.6f}]，t(359) p={b.p_value:.4g}。证据：all_results.csv，test=baseline，spec=firm_cluster；与课堂Stata留存结果一致，未在本次运行Stata。

## 2 稳健性判定表
{(o/'robustness_summary.md').read_text().split('| 检验')[1].join(['| 检验',''])}

## 3 结论稳定性
完整时期内，同类二元处理回归的点估计方向稳定。R5显示推断精度对相关结构敏感；二维聚类SE放大约5.57倍，小簇问题不能由更换t分布完全解决。R7短窗口下降约32.62%，而DGP处理收益逐年增长，窗口变化对应不同平均处理效应；不能简单认定主结论失败。T1的单位已变，不能与0/1系数直接比较。

## 4 残余威胁
DGP实际包含每年0.0008的处理组额外趋势，R1仍未拒绝零预趋势，提供了“未拒绝不等于证明”的具体反例。2016—2019与2020—2024的平均时间差为4.5年，趋势项对简单DID的理论贡献约0.0036。已知处理效应五年平均0.115，估计偏离约0.00592还包含有限样本噪声及控制残差化影响。这些反事实知识只在模拟中可得。

真实应用中采用由管理能力、规模和出口暴露驱动，未观测的同期组织改革与融资改善可能造成时变混杂；数字平台网络可能产生溢出；能力代理有测量误差。R4控制敏感性不能排除这些问题。四行业三地区的小簇推断没有得到充分解决，合成样本也不建立外部效度。

## 5 主题解读
T2三个正式差异检验及Holm校正均未支持行业、所有制、规模差异，不能以各组显著为据宣布异质性成立。T3能力交互系数0.002528、p=0.5324，互补性假说未获支持；DGP只把能力放入生产率水平与采用选择，没有植入收益交互。T1构造强度正相关不能推翻T3，也不能替代机制识别。T4吸收行业和地区年度冲击后方向保持，但不覆盖企业特定冲击。R3替代指标由原指标加噪声生成，不能视为独立复制。

## 6 对论文写作的建议
可以写：“在合成面板的多数同类设定中，转型与生产率上升呈稳定正向关系。”
需要限定后写：“未拒绝处理前差异趋势联合为零，但已知DGP存在轻微非平行趋势，且检验功效有限。”
不能写：“数字化使真实企业TFP提高12.85%”“平行趋势已被证明”“管理能力互补机制得到验证”“全部稳健性检验通过”。

## 边界声明
全部数据为合成教学数据，任何结果均不能解释为真实企业或政策的因果证据。没有虚构文献；论文所引三篇方法文献另有Crossref核查。Agent只评估与建议，未直接改写论文。此报告由Codex按Agent说明评估，辅助脚本负责确定性装配；没有声称启动另一独立模型。最终判断由署名研究者复核。
'''
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--output',default='output/eval_robustness_report.md');a=p.parse_args();root=Path(a.root);target=(root/a.output).resolve();assert target.is_relative_to((root/'output').resolve()),'report output must stay under output/'
    text=report(root);target.parent.mkdir(exist_ok=True,parents=True);target.write_text(text)
