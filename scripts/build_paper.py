from pathlib import Path
import pandas as pd
r=Path(__file__).resolve().parents[1];a=pd.read_csv(r/'output/all_results.csv')
intro=r'''\documentclass[UTF8,11pt,fontset=none]{ctexart}
\usepackage[a4paper,margin=2.4cm]{geometry}
\IfFontExistsTF{Songti SC}{\setCJKmainfont{Songti SC}}{\setCJKmainfont{FandolSong-Regular}}
\IfFontExistsTF{Heiti SC}{\setCJKsansfont{Heiti SC}}{\setCJKsansfont{FandolHei-Regular}}
\usepackage{amsmath,booktabs,longtable,graphicx,hyperref}
\hypersetup{hidelinks}
\setlength{\parskip}{2pt}
\setlength{\emergencystretch}{2em}
\renewcommand{\arraystretch}{1.08}
\title{数字化转型与企业生产率\\合成面板中的DID稳健性检验与AI研究流程审计}
\author{邓鸿琪\quad 825200520\\江西财经大学数字经济学院\\2025级产业经济学硕士研究生}
\date{2026年9月4日}
\begin{document}
\maketitle
\begin{abstract}
本文以课堂提供的2016—2024年360家企业合成面板为基础，复现双向固定效应DID，并完成七项常规、四项主题检验及一项逐行业剔除扩展。基准系数为0.120920，企业聚类标准误为0.004723，与课堂Stata留存结果一致。多数同类设定保留正向关系，但二维聚类标准误扩大约5.57倍，短窗口系数降至0.081471，管理能力交互项未获统计支持。数据生成过程包含每年0.0008的处理组差异趋势，而预趋势联合检验未拒绝零假设，直观显示检验不显著并不证明识别成立。本文还通过固定随机种子的Skill对照及评估输入验证，建立Prompt、程序、结果、评估与写作的证据链。所有结果仅用于合成数据教学，不能作为真实企业数字化收益或政策效果的因果证据。
\end{abstract}
\noindent\textbf{关键词：}数字化转型；全要素生产率；双重差分；合成数据；AI研究审计

\section{研究问题与研究边界}
数字技术可能改善信息传递、生产调度和管理决策，生产率收益也可能取决于组织能力。产业经济学的实证工作需要把企业采用选择、行业共同冲击和收益异质性分开讨论。本作业的问题是：在已知数据生成过程的教学面板中，数字化转型与生产率的正向关系是否对模型和样本选择敏感？进一步的问题是：AI能否把诊断结果转化为有边界、可追溯的研究判断？

本文不估计真实企业数字化的政策效应，不把合成显著结果包装为经验事实。方法依据包括DID序列相关推断的讨论\cite{bdm}、多维聚类方法\cite{cgm}和预趋势检验局限\cite{roth}。三篇文献均核对DOI元数据；它们支持方法论论述，不提供本作业的现实数字化证据。

\section{数据与识别目标}
样本包含3240个企业年观测，其中151家企业在2020年统一采用数字化，209家始终未处理。数据无缺失，企业与年份联合唯一，四行业、三地区均为合成类别。原数据只读，分析前后SHA256一致。

目标是2020—2024年处理组平均处理效应的跨年平均。只有在条件平行趋势、无预期、无溢出、处理定义一致等条件成立时，回归系数才能与目标ATT建立联系。DGP中采用选择依赖能力、基期规模和出口比例；控制组是从未采用者，不是“尚未采用者”。同期处理避免了交错采用时的部分比较问题，却不能消除采用选择或共同冲击。

DGP赋予处理收益 $0.045+0.035\min(t-2020,4)$，五年平均为0.115；另加入处理组每年0.0008的时间趋势。能力影响生产率水平和采用概率，但没有能力与处理收益的交互项。知道这些设定使我们可以检查诊断方法的局限；真实应用无法观察这种反事实真值。

\section{基准模型与复现}
\begin{equation}
 y_{it}=\alpha_i+\lambda_t+\tau D_{it}+X_{it}'\beta+\varepsilon_{it}.
\end{equation}
其中 $y$ 为对数TFP，$D$ 是2020年起处理组的数字化指标，$\alpha_i$、$\lambda_t$ 分别为企业和年份固定效应。课堂控制集为资本密集度、出口比例和所有制。后两者在企业内不变，被企业固定效应吸收；程序显式移除它们，不单独解释其系数。除另行说明，标准误聚类到企业，采用CR1簇数修正并计入吸收固定效应的自由度，报告 $t(359)$ 参考分布的p值和区间。

基准系数为0.12091954，SE为0.00472336，95\%区间为[0.111631,0.130208]。满秩虚拟变量OLS与PanelOLS结果一致；与课堂Stata留存系数差小于$10^{-7}$。课堂原Python公式在当前版本中因冗余项产生异常SE=5.82118，已保留原输出并修复。复现的标准是数据和设定一致后数值吻合，不是修改数据追求预定系数。本次没有运行Stata。

\section{稳健性检验}
\subsection{识别诊断与随机标签安慰剂}
事件研究以2019年为基期，加入处理组与各年交互项。三个处理前系数的聚类Wald统计量除以3，按 $F(3,359)$ 作有限样本参考，得到F=0.4926、p=0.6876。图\ref{fig:event}中处理前区间覆盖零，但这既不是等价性检验，也不证明趋势相同。特别是DGP已知有非零差异趋势，检验仍不显著，与Roth\cite{roth}关于检验功效的讨论相符。

R2固定处理企业数151、种子825200520及2020年处理时点，在企业层面重新抽取伪处理组300次。伪系数均值0.000119，2.5\%与97.5\%分位数为$-0.013939$和0.016515，零次达到真实估计的绝对值。直接比例0/300不意味着概率为零；加一平滑比例为1/301=0.003322，零超越对应尾部概率单侧95\%二项上界约0.009936。真实采用并非随机，这些量是指定分配机制下的模拟诊断，不能当作消除内生性的精确随机化p值。

\begin{figure}[htbp]
\centering\includegraphics[width=.83\textwidth]{../output/digital_event_study.png}
\caption{合成面板事件研究及企业聚类95\%区间。2019年系数归零。}\label{fig:event}
\end{figure}

\subsection{测量、控制、推断与样本}
R3使用对数劳动生产率得到0.120534；但该变量由对数TFP加噪声后取指数生成，不能视为独立数据复制。R4不控制、完整控制及加入企业规模的系数为0.120908、0.120920、0.120822。规模轨迹在DGP中不受处理影响；真实研究若规模是中介，不应机械控制当期规模。

R5行业、地区及企业加年份二维聚类SE分别为0.001901、0.003249、0.026296。二维聚类是企业方差加年份方差减交集方差，不是聚类到企业年唯一标识\cite{cgm}。使用最小簇数减1作t参考自由度后，二维p=0.001759，但仅有4个行业、3个地区、9个年份，渐近推断可靠性仍受限制。更小的行业或地区SE不是更可信的证据，不能选择最显著的口径。

R6对结果变量做全样本1\%/99\%缩尾，阈值1.079696和2.519095，共替换66个观测，系数0.116987，较基准下降3.25\%。R7剔除电子业及基期规模上下5\%企业后分别为0.120382和0.120954；缩短至2018—2022后为0.081471，下降32.62\%。规模界限在企业层面由处理前均值计算，避免用处理后结果选择样本。

短窗口只覆盖处理后的前三年，因此DGP处理收益平均由0.115变成0.080。全事件模型的2020—2022系数均值0.086889提供辅助对照，其2019基期与短窗口回归处理前平均的口径仍不同。这里首先应讨论估计量变化，不能把大幅下降直接归为程序失败，也不能只凭仍显著就宣称数值稳定。

\subsection{研究主题特定检验}
T1把处理前能力按企业min-max归一化，再与数字化指标相乘，构造强度代理。系数0.170879对应整个代理区间的一单位变化，估计对象不再是二元ATT。该构造同时改变权重及函数形式；正相关不是独立的剂量反应识别。

T2对电子与纺织、SOE与非SOE、基期规模高低分组估计。正式差异模型允许组别年冲击和控制斜率不同。组间差分别为$-0.001375$、$-0.008703$、$-0.002554$，原始p分别为0.9164、0.4475、0.7910，三个预定差异检验Holm校正p均为1。不存在支持这些异质性的充分证据，也不能据此断言组间完全相同。

T3加入 $D_{it}(M_i-\bar M)$，能力为处理前企业均值，按企业样本中心化。交互系数0.002528，SE=0.004045，p=0.5324，未支持能力互补性假说。该结果与DGP没有植入收益交互相容；不能通过T1显著来挽救机制叙述。即使交互显著，非随机能力代理也不足以识别机制因果效应。

T4加入行业年固定效应及进一步的地区年固定效应后，系数为0.120609、0.120913，方向保持；共同冲击吸收不等于排除企业特定混杂。T5为自选扩展，逐一剔除四行业后系数范围0.119775—0.122565。评分标准的必做主题项目是T1—T4，此扩展补足说明书部分段落出现的T5编号。

\section{讨论与局限}
本作业支持的是一套可审计流程，而非现实政策结论。首先，严格平行趋势在已知DGP下不成立，额外趋势对简单DID的理论贡献约为 $0.0008\times4.5=0.0036$。基准与真处理收益平均0.115的差约0.00592，还包含有限样本随机噪声和控制残差化。只有模拟允许这种核对，不能把DGP解释当作现实识别策略。

其次，标准误的敏感性、窗口的动态权重、结果变量的机械关系、能力代理的非随机性分别对应不同威胁，不应合并为“多数检验通过”的得票结论。尚未充分解决的真实研究问题包括网络溢出、企业同期管理改革、融资变化、测量误差和样本选择。少簇情况下即使p值低，仍需更适合研究设计的推断方法和更多有效簇。本文没有声称解决这些问题。

\section{AI协作与可复核性}
每项检验在运行前保存目标、边界、验证和汇报四要素。Skill先从说明和数据识别变量角色，再交由通用契约校验程序检查；不是凭列名猜因果含义。第一轮对照固定数据、种子和模型，300个伪系数完全一致，改进体现在有限模拟尾部解释与证据保存。评估Agent按读结果、判定、稳定性、残余威胁、主题解读、写作建议六步工作，只返回报告，不直接修改论文。第二轮对评估输入完整性与交叉一致性另行验证，证据及反思见仓库相应记录。

\appendix
\section{完整回归结果索引}
表中b为系数，SE为相应聚类标准误；p按最小簇数减1的t分布计算。基准及其他模型含企业和年份FE；T4另加共同冲击FE。R1、R2为诊断分布，分别见事件图、正文及CSV，不与处理效应系数混列。T2的difference为正式组间差；T3第一行为交互项、第二行为平均能力处数字化系数。
\small
\begin{longtable}{llrrrr}
\toprule 项目 & 设定 & b & SE & p & N\\\midrule\endhead
'''
labels={'firm_cluster':'企业聚类','log_labor_productivity':'对数劳动生产率','no_controls':'无控制','full_controls_absorbed':'完整控制','add_firm_size':'加入规模','industry':'行业聚类','province':'地区聚类','firm_id+year':'企业+年份聚类','winsor_1_99':'结果缩尾','drop_electronics':'剔除电子','trim_size_firms_5_95':'剔除规模两端','window_2018_2022':'短窗口','minmax_capability_proxy':'能力强度代理','industry_group0':'纺织','industry_group1':'电子','industry_difference':'电子减纺织','ownership_group0':'非SOE','ownership_group1':'SOE','ownership_difference':'SOE减非SOE','size_group0':'小规模','size_group1':'大规模','size_difference':'大减小','capability_interaction':'能力交互','digital_at_mean_capability':'平均能力处处理','industry_year':'行业年FE','industry_province_year':'行业年+地区年FE','drop_chemicals':'剔除化工','drop_machinery':'剔除机械','drop_textile':'剔除纺织'}
rows=[]
for _,z in a.iterrows():
 p='<0.001' if z.p_value<.001 else f'{z.p_value:.4f}'
 rows.append(f"{z.test.replace('baseline','基准')} & {labels[z.spec]} & {z.estimate:.5f} & {z.std_error:.5f} & ${p}$ & {int(z.n_obs)}"+r'\\')
end=r'''\bottomrule\end{longtable}\normalsize
\begin{thebibliography}{9}
\bibitem{bdm} Bertrand, M., Duflo, E., and Mullainathan, S. (2004). How Much Should We Trust Differences-In-Differences Estimates? \emph{The Quarterly Journal of Economics}, 119(1), 249--275. \url{https://doi.org/10.1162/003355304772839588}.
\bibitem{cgm} Cameron, A. C., Gelbach, J. B., and Miller, D. L. (2011). Robust Inference With Multiway Clustering. \emph{Journal of Business \& Economic Statistics}, 29(2), 238--249. \url{https://doi.org/10.1198/jbes.2010.07136}.
\bibitem{roth} Roth, J. (2022). Pretest with Caution: Event-Study Estimates after Testing for Parallel Trends. \emph{American Economic Review: Insights}, 4(3), 305--322. \url{https://doi.org/10.1257/aeri.20210236}.
\end{thebibliography}
\end{document}
'''
(r/'paper/main.tex').write_text(intro+'\n'.join(rows)+'\n'+end)
