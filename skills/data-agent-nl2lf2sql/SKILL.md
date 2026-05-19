# Skill: data-agent-nl2lf2sql

## 用途
快速在新项目中复用「NL2LF2SQL」最小可运行工程骨架，包含：
- QueryObject / LogicForm 确定性主链路
- SemanticDB 配置驱动（指标版本+生效窗）
- 编译/执行/审计分层

## 适用场景
- 你要从 0 到 1 做 Data Agent POC
- 你要把现有 NL2SQL Demo 改造成可治理架构
- 你要快速搭建可回归测试的 pipeline

## 标准步骤（复用清单）
1. 建立目录：`src/`, `configs/`, `schemas/`, `tests/`。
2. 定义 `QueryObject` 与 `LogicForm` schema。
3. 实现 `SemanticDB.metric(name, as_of_date)`，支持版本命中。
4. 实现 `NLStandardizer -> DeterministicReasoner -> SQLCompiler -> Executor`。
5. 接入 `trace_id` 与审计落盘。
6. 先写 TDD：
   - determinism（同输入同输出）
   - metric version hit
   - role deny
   - replay contract
7. 运行：`python3 -m unittest discover -s tests -p 'test_*.py'`。

## 必要约束
- 不允许端到端模型直接产出最终 SQL（主链路）
- 默认拒绝权限（default deny）
- 任何服务输出都需契约校验

## 产出模板
- `schemas/logicform.schema.json`
- `configs/semanticdb.sample.json`
- `tests/test_pipeline.py`
