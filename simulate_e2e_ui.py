import os
import sys
import shutil
import json
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mvp_platform import store

def generate_perfect_e2e_mock():
    source_video = Path(r"D:\Develop\claudecode\短剧\output\28集\28集-法语.mp4")
    if not source_video.exists():
        print(f"Source missing: {source_video}")
        return

    # 1. intake stage
    project_state = store.create_project("Perfect_E2E_Loop", str(source_video))
    pid = project_state["id"]
    pdir = store.project_dir(pid)
    shutil.copy(source_video, pdir / "intake" / source_video.name)
    print(f"Project created: {pid}")

    # 2. criteria generation stage (mocking output of the agent)
    state = store.load_state(pid)
    state["status"] = "criteria_ready"
    state["history"].append({"at": store.now_iso(), "status": "criteria_ready", "note": "自动化代理（Codex）已生成标准"})
    
    (pdir / "criteria" / "source_probe.json").write_text(json.dumps({
        "format": {"duration": "120.00"}, "streams": [{"codec_type": "video", "width": 1080, "height": 1920}]
    }), encoding="utf-8")
    
    (pdir / "criteria" / "acceptance-criteria.md").write_text("# 验收标准\n\n- [x] 分辨率：1080x1920\n- [x] 时间同步偏差：≤ 200ms\n- [x] 音轨要求：法语配音", encoding="utf-8")
    (pdir / "criteria" / "project-brief.md").write_text("# 项目概况\n\n法文短剧。主要进行自动配音及字幕适配处理。", encoding="utf-8")
    (pdir / "criteria" / "pending-items.md").write_text("无待确认项，符合硬性标准。", encoding="utf-8")
    store.save_state(pid, state)

    # 3. user confirms (moves to approved_for_demo)
    store.confirm_criteria(pid)
    state = store.load_state(pid)  # confirm_criteria updates it
    
    # 4. production stage (mocking output of the OpenStoryline codex agent)
    state["status"] = "demo_uploaded"
    state["history"].append({"at": store.now_iso(), "status": "demo_uploaded", "note": "自动化 Agent 已完成视频剪辑制作并输出视频"})
    
    production_output = pdir / "production" / "final_output.mp4"
    # Copy the original as a placeholder for the "produced" video, or we just write a dummy text file
    # We will copy original to indicate a valid MP4 produced
    shutil.copy(source_video, production_output)
    
    store.save_state(pid, state)

    # 5. QA stage
    state = store.load_state(pid)
    state["status"] = "qa_done"
    state["history"].append({"at": store.now_iso(), "status": "qa_done", "note": "QA 质检已完成，无红线阻断项，视频通过"})
    
    (pdir / "qa" / "qa-report.md").write_text("# 最终质检报告\n\n✅ 结果：**完全通过（Pass）**\n\n- 工程参数核对：合格\n- 声画同步：符合\n- 分辨率验证：1080x1920 (无裁剪损失)", encoding="utf-8")
    (pdir / "qa" / "engineering-report.json").write_text(json.dumps({"passed": True, "errors": []}), encoding="utf-8")
    
    store.save_state(pid, state)
    
    print(f"Perfect End-to-End Loop created for project: {pid}!\nPlease refresh UI to see the deliverables!")

if __name__ == "__main__":
    generate_perfect_e2e_mock()
