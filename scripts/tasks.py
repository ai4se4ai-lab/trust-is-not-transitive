"""Portable Makefile backend; Windows can use `python scripts/tasks.py smoke`."""
from pathlib import Path
from datetime import datetime,timezone
import shutil
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
    elif name=='paper':
        run(sys.executable,'scripts/make_macros.py')
        run(sys.executable,'scripts/build_paper.py')
    elif name=='verify-results':
        run(sys.executable,'scripts/process_results.py','--verify')
        run(sys.executable,'scripts/validate_replay.py')
        run(sys.executable,'scripts/post_review_analysis.py','--verify')
        run(sys.executable,'scripts/manifest.py','--verify')
    elif name=='verify-paper':
        for script in ['scripts/verify_numbers.py','scripts/check_refs.py','scripts/check_notation.py','scripts/verify_pdf.py']:
            run(sys.executable,script)
    elif name=='all':
        raw=ROOT/'results/raw'
        if raw.exists():
            archive=ROOT/'results/archive'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            assert raw.resolve()==(ROOT/'results/raw').resolve()
            assert archive.resolve().is_relative_to((ROOT/'results/archive').resolve())
            archive.parent.mkdir(parents=True,exist_ok=True)
            shutil.move(str(raw),str(archive))
            print('Preserved prior raw observations at',archive,flush=True)
        raw.mkdir(parents=True,exist_ok=True)
        task('test')
        run(sys.executable,'-m','coverage','json','-o','results/raw/coverage_tests.json')
        task('formal')
        run(sys.executable,'experiments/run.py')
        run(sys.executable,'experiments/run.py','--exploratory-numeric')
        run(sys.executable,'experiments/policy_inventory.py')
        run(sys.executable,'scripts/process_results.py')
        run(sys.executable,'scripts/post_review_analysis.py')
        task('paper')
        run(sys.executable,'scripts/manifest.py')
        task('verify-results')
        task('verify-paper')
    else:
        raise SystemExit('Unknown task: '+name)


if __name__=='__main__':
    task(sys.argv[1] if len(sys.argv)>1 else 'smoke')
