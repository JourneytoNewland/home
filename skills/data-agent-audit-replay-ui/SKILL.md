# Skill: data-agent-audit-replay-ui

## 用途
复用“问数 + 审计回放”双区控制台能力，快速给数据 Agent 增加可演示 UI。

## 适用场景
- 需要给分析师/管理员/审计员演示同一套能力
- 需要 trace_id 可视化追踪
- 需要回放过滤、排序、分页、详情查看

## 标准步骤（复用清单）
1. 提供 UI API：
   - `POST /query`
   - `GET /replay`（role/sort/limit/offset/trace_id）
2. 前端最小区块：
   - 问数区（角色+问题模板）
   - 回放区（过滤+列表+详情）
3. 增强体验：
   - SQL 一键复制
   - role 视图切换
   - 本地偏好持久化（localStorage）
4. 回放安全：
   - 非 admin SQL 脱敏
   - 非 admin 禁止关闭 actor scope
5. 增加 UI 合同测试：
   - 页面关键元素存在
   - 回放过滤参数生效

## 必要约束
- 回放服务必须返回标准 envelope：`code/message/items/total/limit/offset/next_offset`
- 非 admin 默认只见掩码 SQL

## 产出模板
- `ui/index.html`
- `ui/server.py`
- `tests/test_ui_server_tdd.py`
- `tests/test_ui_trace_filter_tdd.py`
