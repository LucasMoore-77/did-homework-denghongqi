# 由语义与数据共同确认的映射

AI先读课堂README、DGP和数据列，产生config/digital.json；辅助程序只接受已确认契约，不凭相关系数猜变量。

| 角色 | 确认字段 | 排除歧义的证据 |
|---|---|---|
| 结果 | log_tfp | 研究问题明确以TFP为对象；labor_productivity用于替代测量 |
| 处理 | digital | 企业内在2020年由0变1；treated时间不变，post对照组也变1；treated_post与digital完全相同，记为等价别名 |
| 个体 时间 | firm_id year | 联合唯一，360×9平衡面板 |
| 控制 | capital_intensity export_share soe | 课堂公式定义；后两项企业内不变，吸收而不单独解释 |

发现变量的工作由AI根据文档进行；通用脚本负责可执行验证。此处不宣称系统能从任意匿名数据自动识别因果语义。
