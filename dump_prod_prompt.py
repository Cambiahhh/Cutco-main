import os
import sys
from pathlib import Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mvp_platform import store, agent_runtime, config
import textwrap

pid = '20260329-113613-e2e_test'
project_dir = store.project_dir(pid)

skill_context = agent_runtime._build_skill_context(config.VIDEO_PRODUCTION_DIR)
scripts_dir = config.BASE_DIR / "mvp_platform" / "scripts"

prompt = textwrap.dedent(f"""\
你是一个视频交付项目的自动化剪辑 Agent。请严格依据以下的 SKILL 文档中的指令执行任务。

===== 你的行为指南 =====
{skill_context}
===== 行为指南结束 =====

===== 当前任务 =====

项目目录: {project_dir}
验收标准: {project_dir / "criteria" / "acceptance-criteria.md"}
原片探测结果: {project_dir / "criteria" / "source_probe.json"}

待处理的原始视频可以在 {project_dir / "intake"} 下找到。
你的任务是将处理后的成片保存到 {project_dir / "production"} 目录下。

工具辅助脚本: {scripts_dir / "run_ffmpeg.py"}

你需要完成以下工作:
1. 仔细阅读验收标准（acceptance-criteria.md），提取时间修剪、配音文本、字幕要求等。
2. 阅读原片探测结果（source_probe.json），明确视频基础属性。
3. 使用 python 运行工具脚本 `{scripts_dir / "run_ffmpeg.py"} --help` 查看各个操作所需的参数。
4. 结合源视频，执行相应的视频操作，并在必要时组合（比如配音+字幕组合操作）。
5. 确保最终生成的视频或音频放在了 {project_dir / "production"} 目录中。
6. 你可以自由执行所需的 bash 命令，请清理好中间临时文件（但不要清除 intake 中的原片）。

开始执行。
""")

(project_dir / 'production_agent.txt').write_text(prompt, encoding='utf-8')
print("Dumped production prompt.")
