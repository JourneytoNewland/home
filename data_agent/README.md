# Data Agent（NL2LF2SQL）实施骨架

这是基于生产级路线的首版可执行实现骨架，目标是把“方案文档”推进到“可启动研发”的工程形态。

## 目录
- `docs/architecture.md`：架构与职责边界
- `docs/implementation-plan.md`：分阶段实施计划（与 PRD 对齐）
- `schemas/logicform.schema.json`：LogicForm JSON Schema V1
- `configs/semanticdb.sample.yaml|json`：语义层样例配置（指标/实体/关系/权限）
- `src/pipeline.py`：NL2LF2SQL 流水线最小可运行实现
- `src/semanticdb.py`：语义配置加载与查询
- `src/auth.py`：权限校验（默认拒绝）
- `src/compiler.py`：SQL 编译接口与默认实现
- `tests/test_pipeline.py`：一致性与权限行为测试

## 快速运行
```bash
python3 -m unittest discover -s data_agent/tests -p 'test_*.py'
```

## 当前实现边界
- 提供确定性管线框架与数据结构，不直接连接真实数据库。
- 支持配置驱动的指标表达式、角色行过滤、默认拒绝权限策略。
- 编译器已接口化，后续可扩展多方言实现（ClickHouse/MySQL/PostgreSQL）。
