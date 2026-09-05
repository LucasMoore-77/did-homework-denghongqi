# 数字化转型与企业生产率课程作业

邓鸿琪｜825200520｜江西财经大学数字经济学院｜2025级产业经济学硕士

提交日期：2026年8月26日

这是“AI时代经济学研究工具与方法”课程作业。基于课堂demo-project建立独立Git历史，完成R1—R7、T1—T4及T5逐行业剔除扩展，提供实际运行的Skill对照、评估Agent、两轮迭代和中文LaTeX论文。**所有数据均为合成数据，不构成现实企业或政策的因果证据。**

## 先看什么

- `submission/纸质提交材料.pdf`：按教师模板完成的纸质材料。
- `submission/纸质提交材料.docx`：可编辑版本；封面已填写实际仓库链接。
- `paper/main.pdf`、`paper/main.tex`：中文论文与LaTeX源稿。
- `output/robustness_summary.md`、`output/eval_robustness_report.md`：完整结果判断。
- `output/iteration_reflection.md`、`audit-log.md`：两轮实际改进证据。
- `GITHUB_UPLOAD.md`：最后的上传步骤。

## 主要发现

基准系数0.12091954，企业聚类SE=0.00472336，与课堂Stata留存结果吻合。事件前联合检验F=0.4926，p=0.6876；DGP却确有每年0.0008额外趋势，不能声称平行趋势得到证明。二维聚类SE=0.026296，短窗口系数0.081471，管理能力交互p=0.5324。多数同类模型点估计正向稳定，推断精度和动态平均对象须分别讨论。

## 复现分析

Python 3.12环境已实际执行；依赖版本记录于requirements.txt及output/environment.json。建议虚拟环境放在本机磁盘，避免部分外置盘AppleDouble元文件干扰包资源读取。

```bash
python3 -m venv ~/.venvs/did-homework
source ~/.venvs/did-homework/bin/activate
pip install -r requirements.txt
python scripts/reproduce.py
```

脚本不重新生成或覆盖data/raw。历史异常与迭代前快照单独保留，最终复现运行修订后的程序。整个流程约数分钟，输出包括300次项目安慰剂与120次迁移安慰剂、完整统计表、图及最终评估。检验由Python脚本执行，Codex按Agent说明解读结果，工具使用范围见audit-log.md。

## 编译与编辑材料

已实际使用Tectonic 0.15.0（XeTeX）编译。安装Tectonic后，在项目根目录运行：

```bash
python scripts/build_paper.py
tectonic paper/main.tex --keep-logs
```

或已装完整TeX Live/MacTeX时：

```bash
cd paper
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
cd ..
```

中文字体优先使用macOS Songti SC/Heiti SC；其他系统回退到TeX发行版中的Fandol字体。只实际验证了当前macOS编译，跨系统可按日志安装缺失字体或宏包。

纸质材料内容来自脚本和保存的Prompt、Git历史；修改config/submission.json的仓库链接后执行 `python scripts/build_submission.py` 可同步更新DOCX及Markdown，再用Word/LibreOffice导出PDF。也可直接编辑Word封面并导出PDF。

## 结构与来源

- `data/raw/`：课堂合成面板，前后哈希见output/provenance.json。
- `source/`：课堂说明、模板、原始论文和原分析脚本留存；只作来源记录。
- `prompts/robustness/`：运行前保存的基准及12张检验Prompt，运行后附结果。
- `.claude/skills/robustness-check/`：通用六模块技能和同步面板安慰剂辅助程序。
- `.claude/agents/eval-did-robustness.md`：只读评估说明；scripts/evaluate.py为项目适配器。
- `output/iterations/`：真实修订前结果及错误输入测试，不复制他人历史。
- `output/migration/`：重新生成的最低工资与就业合成面板及拒绝测试。
- `quality_reports/`：三篇文献的DOI核查及提交核对。

课堂Stata CSV是预存参考，不是本次运行Stata。课堂原Python公式在当前环境下产生异常SE，修复吸收控制项后，两种Python实现与Stata一致，完整记录见baseline_comparison.md。T3没有运行任何Matlab；原课堂论文仅留存在source/，最终论文采用实证交互讨论。

## Git与提交状态

main之外保留5个任务分支与合并记录。远程仓库已创建，地址为 https://github.com/LucasMoore-77/did-homework-denghongqi；封面链接已补齐，本人按GITHUB_UPLOAD.md推送完整历史后提交。不要只通过网页拖文件上传，那会丢失此次作业要求的分支与版本历史。
