# data-agent-nl2lf2sql - 使用与精进指南

## 这个 Skill 解决什么
用于快速搭建 NL2LF2SQL 核心主链路，避免直接 NL2SQL 的不稳定问题。

## 推荐使用顺序
1. 先按 `SKILL.md` 建立最小目录和数据结构。
2. 优先打通确定性链路：`NL -> QueryObject -> LogicForm -> SQL`。
3. 立刻补 TDD（determinism、权限、口径版本）。

## 精进路线（下一阶段）
- P1：把 `RuleBasedNLAdapter` 换成外部 NL 服务适配器。
- P2：引入更完整 LogicForm 语法（TopN 后计算、嵌套查询）。
- P3：加入执行计划检查和 SQL 安全规则（只读白名单）。
- P4：引入数据域插件化（每业务域独立语义包）。

## 验收建议
- 每次迭代必须保留“同输入同输出”回归。
- 任何口径变更必须新增对应版本命中测试。
