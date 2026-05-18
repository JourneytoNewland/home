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
- `tests/test_pipeline.py`：一致性、权限、方言、执行、审计与多角色行为测试

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

## 下一步建议升级
- 接入真实 NL 服务（替换规则桩）。
- 指标版本变更审批流与回滚策略。
- 执行层接入真实 OLAP/OLTP 数据源连接池。
- 审计回放 API 服务化（鉴权 + 分页 + 时间窗）。
