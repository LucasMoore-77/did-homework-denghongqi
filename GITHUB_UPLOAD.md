# 最后由本人完成的GitHub上传

本地分析、论文、Word/PDF材料与Git历史均已完成。远程创建与推送尚未执行。无需上传虚拟环境、同学参考文件或父文件夹，只推送本did-homework仓库。

## 1 创建空仓库
登录自己的GitHub，在右上角“+”选择New repository。建议仓库名 `did-homework-denghongqi`；如课程要求教师无需授权即可查看，选择Public。不要勾选自动创建README、.gitignore或License，保持空仓库。复制创建后显示的HTTPS地址，例如 `https://github.com/你的用户名/did-homework-denghongqi.git`。

## 2 填入封面仓库链接
打开submission/纸质提交材料.docx，把封面“待本人创建仓库后填写”替换为实际仓库网页链接，并另存/导出为同目录的纸质提交材料.pdf。同步修改config/submission.json中的github_url及submission/纸质提交材料.md封面。

也可在已安装requirements的环境中修改config/submission.json后运行 `python scripts/build_submission.py`，自动更新DOCX与Markdown，再导出PDF。只有封面修改时无需重跑回归。封面日期统一读取config/submission.json，目前设为2026年8月26日；论文生成脚本也读取该配置。分析运行记录与文献核查日期独立保留。

## 3 推送完整历史
在终端逐行运行。第三行把地址替换为自己的仓库地址：

```bash
cd '/Volumes/HP/面向AI时代的经济学研究工具和方法/825200520邓鸿琪/did-homework'
git status
git remote add origin https://github.com/你的用户名/did-homework-denghongqi.git
git add config/submission.json submission/
git diff --cached --stat
git commit -m "docs: fill verified repository link for submission"
git push -u origin main
git push origin --all
```

如已存在origin，先 `git remote -v` 核对；需要更正时用 `git remote set-url origin 实际地址`，不要重复add。如果Git要求登录，使用GitHub Desktop登录后添加这个“现有本地仓库”，或按GitHub提示使用个人访问令牌/凭据管理器。不要把密码或令牌写入项目文件或发给AI。这里不需要强制推送。

## 4 核对与提交
打开仓库网页，确认main分支有paper/main.pdf、submission/纸质提交材料.pdf、.claude目录及output结果；在分支下拉中能看到5个task分支，提交历史中有多次提交及合并。教师通常只需仓库网页链接，不是.git克隆地址。

最后复核署名材料及合成数据边界，打印纸质提交材料PDF，按课程渠道提交实际仓库链接。当前提供的压缩包包含.git，可作本地备份；不要以“上传一个ZIP”替代Git推送完整历史。
