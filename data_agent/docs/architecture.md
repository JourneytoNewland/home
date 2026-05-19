# 架构设计（实施版）

## 1. 三层结构
1. NL 标准化层：做上下文补全、指代消解、口语归一。
2. LogicForm 层：确定性推理，输出唯一 LogicForm。
3. SQL 执行层：方言编译、权限校验、执行与审计。

## 2. 职责边界
- LLM：仅做语言理解，不做口径裁决、不直接生成 SQL。
- Deterministic Engine（Alisa）：仅做结构化推理与收敛。
- SemanticDB：承载语义治理（指标、对象、关系、权限、时间语义）。

## 3. 核心实体
- QueryObject：NL 标准化结果
- LogicForm：可执行语义中间表示
- CompiledQuery：带 trace_id 的 SQL 编译结果

## 4. 关键工程约束
- 同输入同输出（deterministic）
- 可追溯：request_id -> logicform -> sql
- 默认拒绝权限策略
