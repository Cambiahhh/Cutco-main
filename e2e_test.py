import os
from pathlib import Path
from mvp_platform import store, criteria_stage, production_stage, qa_stage
import shutil

def run_e2e_test():
    print("=== 开始端到端自动化跑通测试 ===")
    
    # 1. 创建新项目
    source_video = Path(r"D:\Develop\claudecode\短剧\output\28集\28集-法语.mp4")
    if not source_video.exists():
        print(f"找不到测试视频: {source_video}")
        return
        
    project_state = store.create_project("E2E_Test", str(source_video))
    project_id = project_state["id"]
    print(f"✅ 项目已创建: {project_id}")
    
    # 将视频重命名并放入 intake 目录，模拟文件上传行为
    project_dir = store.project_dir(project_id)
    intake_dir = project_dir / "intake"
    shutil.copy(source_video, intake_dir / source_video.name)
    print(f"✅ 测试视频已复制到 intake")
    
    # 2. 运行 Criteria Stage (大模型第一阶段生成策划标准)
    print("\n⏳ [阶段 1] 正在运行 Criteria Agent...")
    print(">>> 提示: 将会弹出一个新的 codex 命令行窗口！")
    print(">>> 请观察它自动执行。当它执行完毕并等待输入时，请关闭弹窗或在弹窗输入 'exit' 并回车！")
    try:
        criteria_stage.run(project_id)
        state = store.load_state(project_id)
        if state["status"] == "criteria_ready":
            print("✅ Criteria Agent 运行成功！已生成验收标准")
        else:
            print(f"❌ Criteria Agent 运行失败，状态为: {state['status']}")
            return
    except Exception as e:
        print(f"❌ Criteria 错误: {e}")
        return
        
    # 3. 模拟用户点击“确认标准”
    print("\n⏳ 模拟用户确认策划标准...")
    store.confirm_criteria(project_id)
    criteria_stage.write_confirmed_pattern(project_id)
    print("✅ 标准已确认，进入待生产状态")
    
    # 4. 运行 Production Stage (大模型第二阶段使用 codex 和 OpenStoryline 生成视频)
    print("\n⏳ [阶段 2] 正在运行 Production Agent (调用 codex)...")
    print(">>> 提示: 将会弹出一个新的 codex 命令行窗口执行 OpenStoryline！")
    print(">>> 这可能需要较长时间。当它完成所有生成并等待输入时，请关闭该窗口！")
    try:
        production_stage.run(project_id)
        state = store.load_state(project_id)
        # Production stage 成功后状态是 demo_uploaded
        if state["status"] == "demo_uploaded":
            print("✅ Production Agent 运行成功！样片已生成")
        else:
            print(f"❌ Production Agent 运行失败，状态为: {state['status']}")
            # 打印出错详情
            for item in state.get("history", []):
                if item.get("status") == "production_error":
                    print(f"   详情: {item.get('note')}")
            return
    except Exception as e:
        print(f"❌ Production 错误: {e}")
        return
        
    # 5. 运行 QA Stage (大模型第三阶段分析成品)
    print("\n⏳ [阶段 3] 正在运行 QA Agent...")
    print(">>> 提示: 将会弹出最后一个 codex 命令行窗口！验证完毕后，请关闭窗口。")
    try:
        qa_stage.run(project_id)
        state = store.load_state(project_id)
        if state["status"] == "qa_done":
            print("✅ QA Agent 运行成功！质检报告已生成")
        else:
            print(f"❌ QA Agent 运行失败，状态为: {state['status']}")
            return
    except Exception as e:
        print(f"❌ QA 错误: {e}")
        return
        
    print("\n🎉 端到端流程测试圆满完成！")
    print(f"请检查目录 {project_dir.resolve()} 以查看完整产物。")

if __name__ == "__main__":
    run_e2e_test()
