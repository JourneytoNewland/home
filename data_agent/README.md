# Data Agent（NL2LF2SQL）实施骨架

这是基于生产级路线的可执行实现骨架，目标是把“方案文档”推进到“可启动研发”的工程形态。

## 目录
- `docs/architecture.md`：架构与职责边界
- `docs/implementation-plan.md`：分阶段实施计划（与 PRD 对齐）
- `schemas/logicform.schema.json`：LogicForm JSON Schema V1
- `configs/semanticdb.sample.yaml|json`：语义层样例配置（指标/实体/关系/权限）
- `src/pipeline.py`：NL2LF2SQL 流水线最小可运行实现
- `src/semanticdb.py`：语义配置加载与查询
- `src/auth.py`：权限校验（默认拒绝）
- `src/compiler.py`：SQL 编译接口与多方言基础实现
- `src/validator.py`：LogicForm 结构校验
- `src/executor.py`：只读执行器（dry_run/sqlite_readonly）与审计日志
- `src/audit.py`：审计事件存储与回放过滤（支持 JSONL 持久化）
- `src/unknown_terms.py`：未知术语解析与澄清建议
- `src/nl_adapter.py`：NL 适配器接口与默认规则实现
- `src/identity.py`：单用户多角色上下文与角色选择
- `src/errors.py`：统一错误类型（审计查询/NL适配器）
- `tests/`：覆盖一致性、权限、方言、执行、审计回放、输入校验与多角色行为

## 快速运行
```bash
python3 -m unittest discover -s data_agent/tests -p 'test_*.py'
```

## 已完成的升级项
- 配置驱动语义层（metric/entity/policy）。
- 默认拒绝权限中间件。
- SQL 编译器接口化，内置 Generic/MySQL/PostgreSQL 编译器。
- LogicForm 最小结构校验。
- Explain 输出补充（口径、时间窗、角色、行过滤、未知词）。
- 指标版本与生效窗选择（as_of_date 解析）。
- 只读执行器与执行审计日志（trace_id 关联）。
- 单用户多角色（active_role/requested_role）权限控制。
- 输入参数校验（审计时间窗/分页参数、NL适配器返回类型）。

## 下一步建议升级
- 接入真实 NL 服务（替换规则桩）。
- 指标版本变更审批流与回滚策略。
- 执行层接入真实 OLAP/OLTP 数据源连接池。
- 审计回放 API 服务化（鉴权 + 分页 + 时间窗）。


## 审计排序与 DTO 输出兼容
- 审计回放结果保持统一 DTO 结构（如 `trace_id`、`role`、`metric`、`logged_at` 等字段），便于上层 API 直接透传。
- 当需要按时间排序展示时，推荐基于 `logged_at` 做显式 asc/desc 排序，排序后 DTO 字段保持不变。
- 分页（`limit`/`offset`）应在确定排序顺序后应用，以保证回放页面稳定性。
