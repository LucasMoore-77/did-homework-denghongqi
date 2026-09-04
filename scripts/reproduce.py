from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
steps=[['scripts/analyze_did.py'],['scripts/run_robustness.py'],['scripts/summarize_results.py'],['.claude/skills/robustness-check/scripts/placebo.py','config/digital.json','--root','.','--out','output/skill_r2'],['scripts/migration_demo.py'],['scripts/test_agent_inputs.py','--output','output/iterations/agent_v2_tests.json'],['scripts/verify_results.py'],['scripts/evaluate.py','--root','.']]
for args in steps:
    print('Running',args[0],flush=True);subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
print('Analysis complete. Historical pre-revision evidence retained. Compile paper separately.')
