"""Run deterministic model analyses and a clearly labeled synthetic example."""
import argparse, json, os, subprocess, sys
from pathlib import Path
from importlib.metadata import version

MODULES = ['logos_recovery.models','logos_recovery.extensions','logos_recovery.finite_bounds']

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,default=Path('results'))
    ap.add_argument('--verify-only',action='store_true',help='Cross-solver checks without the complete grid campaigns')
    args=ap.parse_args(); out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,LOGOS_OUTPUT=str(out),MPLCONFIGDIR=str(out/'.matplotlib'))
    for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:
        env[key]='1'
    cmd=[sys.executable,'-m',MODULES[0],'--output',str(out)]
    if args.verify_only:cmd+=['--verify-only']
    subprocess.run(cmd,check=True,env=env)
    if not args.verify_only:
        for module in MODULES[1:]:
            subprocess.run([sys.executable,'-m',module],check=True,env=env)
        subprocess.run([sys.executable,'-m','logos_recovery.presentation','--output',str(out)],check=True,env=env)
    from .synthetic import run
    run(out/'synthetic')
    (out/'environment.json').write_text(json.dumps({'python':sys.version,
        'packages':{x:version(x) for x in ['logos-recovery','numpy','scipy','pandas','matplotlib']},
        'mode':'verify-only' if args.verify_only else 'full'},indent=2)+'\n')
    print('Completed:',out)

if __name__=='__main__':main()
