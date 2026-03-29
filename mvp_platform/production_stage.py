from __future__ import annotations

from pathlib import Path

from . import agent_runtime, store

def run(project_id: str) -> None:
    state = store.load_state(project_id)
    if state["status"] not in ["approved_for_demo", "demo_uploaded", "qa_done", "criteria_ready"]:
        raise ValueError(f"当前状态 {state['status']} 不允许运行自动化剪辑 Agent")

    state["status"] = "running_production"
    store.save_state(project_id, state)

    project_dir = store.project_dir(project_id)
    result = agent_runtime.run_production_agent(project_dir)

    state = store.load_state(project_id)
    
    if result.success:
        state["status"] = "demo_uploaded"
        state["history"].append({
            "at": store.now_iso(),
            "status": "production_done",
            "note": "自动化剪辑 Agent 完成处理并生成了样片。"
        })
    else:
        state["status"] = "demo_uploaded"  # Allow re-run or manual fallback
        state["history"].append({
            "at": store.now_iso(),
            "status": "production_error",
            "note": f"自动化剪辑过程发现错误: {result.error}"
        })
        
    # 保存大模型的原始交互日志以供排查
    log_name = f"production/agent-log-{store.now_iso().replace(':', '-')}.txt"
    store.write_text(project_id, log_name, f"=== ERROR ===\n{result.error}\n\n=== OUTPUT ===\n{result.output}\n")

    store.save_state(project_id, state)
