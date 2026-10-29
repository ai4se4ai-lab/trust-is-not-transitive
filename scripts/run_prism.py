"""Run real PRISM when configured; compare every result to the independent model."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def run():
    home=Path(os.environ.get('PRISM_HOME',str(ROOT/'.tools/prism')))
    java=shutil.which('java') or next((str(p) for p in (ROOT/'.tools/java').glob('*/bin/java.exe')),None)
    if not java or not (home/'lib/prism.jar').exists():
        raise RuntimeError('Real PRISM unavailable. Set PRISM_HOME and JAVA_HOME/PATH; do not substitute a claimed run.')
    outputs=[]
    for checked in ['false','true']:
        for trace in range(3):
            command=[java,'-Xss4M','-Djava.library.path='+str(home/'lib'),'-cp',str(home/'lib/*'),
                     'prism.PrismCL',str(ROOT/'formal/cascade.pm'),str(ROOT/'formal/cascade.pctl'),
                     '-const',f'checked={checked},trace={trace}','-explicit']
            result=subprocess.run(command,capture_output=True,text=True,timeout=60)
            if result.returncode:
                raise RuntimeError(result.stdout+result.stderr)
            values=[float(v) for v in re.findall(r'Result: ([\d.Ee+-]+)',result.stdout)]
            expected=[float(checked=='false' and trace==2),float(trace==1 or (checked=='false' and trace==2))]
            assert values==expected,(values,expected)
            outputs.append({'checked':checked,'trace':trace,'results':values,'stdout':result.stdout,'stderr':result.stderr})
    record={'engine':'PRISM 4.11 explicit','jar_sha256':hashlib.sha256((home/'lib/prism.jar').read_bytes()).hexdigest(),
            'model_sha256':hashlib.sha256((ROOT/'formal/cascade.pm').read_bytes()).hexdigest(),'runs':outputs}
    out=ROOT/'results/raw/prism.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print('Real PRISM: all six cases and both reachability properties match the independent checker.')


if __name__=='__main__':
    run()
