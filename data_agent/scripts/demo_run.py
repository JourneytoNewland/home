import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data_agent.src.audit import AuditStore
from data_agent.src.executor import AuditLogger
from data_agent.src.identity import UserContext
from data_agent.src.pipeline import DataAgentPipeline
from data_agent.src.semanticdb import SemanticDB
from data_agent.src.service import AuditReplayService


def main():
    semantic_db = SemanticDB.from_file("data_agent/configs/semanticdb.sample.json")
    logger = AuditLogger(store=AuditStore())
    pipeline = DataAgentPipeline(semantic_db, audit_logger=logger)
    replay = AuditReplayService(logger)

    out1 = pipeline.run("今年销售额按省份", role="analyst")
    admin = UserContext(user_id="u_admin", roles=["analyst", "admin"], active_role="admin")
    out2 = pipeline.run("今年利润", role=None, user_context=admin)

    print("[query#1]", out1["trace_id"]) 
    print(out1["sql"])
    print("[query#2]", out2["trace_id"]) 
    print(out2["sql"])

    print("[replay/admin]")
    print(replay.replay_safe(actor="u_admin", actor_role="admin", scope_to_actor=False, limit=10))


if __name__ == "__main__":
    main()
