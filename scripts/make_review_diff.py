"""Build actual latexdiff PDFs with Perl/Algorithm::Diff installed."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_paper import build


def main(round_number):
    directory=ROOT/'reviews'/f'round{round_number}'
    executable=shutil.which('latexdiff')
    if not executable:raise RuntimeError('latexdiff not installed')
    environment=os.environ.copy()
    git_perl=Path('C:/Users/babaei/AppData/Local/Programs/Git/usr/bin/perl.exe')
    if os.name=='nt' and git_perl.exists():
        environment['PATH']=str(git_perl.parent)+os.pathsep+environment['PATH']
        modules=(ROOT/'.tools/perl5').as_posix()
        environment['PERL5LIB']='/'+modules[0].lower()+modules[2:]
    result=subprocess.run([executable,'--encoding=utf8',str(directory/'before_main.tex.txt'),str(ROOT/'paper/main.tex')],
                          capture_output=True,text=True,encoding='utf-8',errors='replace',env=environment,timeout=120)
    if result.returncode:raise RuntimeError(result.stderr)
    source=directory/'changes.diff.tex'
    source.write_text(result.stdout,encoding='utf-8')
    build(str(source))
    shutil.copy2(ROOT/'paper/changes.diff.pdf',directory/'changes.diff.pdf')
    print('Actual latexdiff PDF:',directory/'changes.diff.pdf')


if __name__=='__main__':main(int(sys.argv[1]))
