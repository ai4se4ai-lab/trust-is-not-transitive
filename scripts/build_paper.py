"""Compile IEEEtran with a single authored source and verified generated macros."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]


def build(source='main.tex',directory=None):
    directory=Path(directory) if directory else ROOT/'paper'
    engine=shutil.which('pdflatex')
    bibtex=shutil.which('bibtex')
    if not engine or not bibtex:raise RuntimeError('pdflatex and bibtex are required; install TeX Live or MiKTeX')
    base=Path(source).stem
    command=[engine,'-interaction=nonstopmode','-halt-on-error',source]
    logs=[]
    for args in [command,[bibtex,base],command,command]:
        result=subprocess.run(args,cwd=directory,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
        logs.append(result.stdout+result.stderr)
        if result.returncode:
            print(logs[-1][-7000:])
            raise RuntimeError('LaTeX build failed: '+str(args))
    log=(directory/(base+'.log')).read_text(encoding='utf-8',errors='replace')
    if 'undefined references' in log or 'Citation ' in log and 'undefined' in log:
        raise RuntimeError('Unresolved references after final pass')
    print('Built',directory/(base+'.pdf'))
    return log


if __name__=='__main__':build()
