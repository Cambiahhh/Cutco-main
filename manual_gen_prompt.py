import os
import sys
from pathlib import Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mvp_platform import store, production_stage

pid = '20260329-113613-e2e_test'
pdir = store.project_dir(pid)
state = store.get_project(pid)
prompt = production_stage._generate_prompt(pdir, pid, state)
(pdir / 'production_agent.txt').write_text(prompt, encoding='utf-8')
print("Writing complete:")
print((pdir / 'production_agent.txt').resolve())
