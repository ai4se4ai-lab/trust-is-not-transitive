"""Portable Makefile backend; Windows can use `python scripts/tasks.py smoke`."""
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]


def run(*args,cwd=ROOT):
    subprocess.run(list(args),cwd=cwd,check=True)


def task(name):
    if name=='smoke':
        start=time.perf_counter()
        run(sys.executable,'-m','pytest','-q')
        run(sys.executable,'scripts/smoke.py')
        run(sys.executable,'formal/check.py')
        print(f'Smoke elapsed: {time.perf_counter()-start:.2f}s')
    elif name=='test':
        run(sys.executable,'-m','coverage','run','-m','pytest','-q')
        run(sys.executable,'-m','coverage','report')
    elif name=='formal':
        for script in ['formal/check.py','formal/sanity.py','scripts/check_notation.py','scripts/run_prism.py']:
            run(sys.executable,script)
    else:
        raise SystemExit('Unknown task: '+name)


if __name__=='__main__':
    task(sys.argv[1] if len(sys.argv)>1 else 'smoke')
