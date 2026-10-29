"""Fail closed on unregistered empirical literals in authored prose.

This source-level provenance check cannot prove glyph-level origin for every
PDF number. Structural counters, proof constants, citations and bibliography
metadata have different provenance and are explicitly outside empirical-literal
checking. Generated macro source hashes and definition coverage are checked.
"""
import hashlib
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]


def check_source(text):
    # Mathematical constants/theorem subscripts are justified by the written
    # proofs rather than experimental data. Remove math before prose checking.
    text=re.sub(r'(?s)\\\[.*?\\\]|\$.*?\$|\\begin\{(?:equation|align)\*?\}.*?\\end\{(?:equation|align)\*?\}', '',text)
    text=re.sub(r'(?s)\\begin\{verbatim\}.*?\\end\{verbatim\}','',text)
    errors=[]
    for index,line in enumerate(text.splitlines(),1):
        # Only structural setup may opt out, under these closed command names.
        if re.match(r'\s*\\(?:documentclass|usepackage|setcounter|setlength|includegraphics|bibliographystyle|bibliography|input|author|title)',line):continue
        line=re.sub(r'(?<!\\)%.*','',line)
        line=re.sub(r'\\(?:cite|ref|eqref|label|url|href|texttt)\{[^}]*\}','',line)
        if re.search(r'\d',line):errors.append((index,line.strip()))
    if errors:raise ValueError('Unregistered numeric literal in prose: '+repr(errors[:8]))


def main():
    text=(ROOT/'paper/main.tex').read_text(encoding='utf-8')
    check_source(text)
    generated=(ROOT/'paper/generated/macros.tex').read_text(encoding='utf-8')
    provenance=json.loads((ROOT/'paper/generated/macro_provenance.json').read_text())
    for key,row in provenance.items():
        assert hashlib.sha256((ROOT/row['source']).read_bytes()).hexdigest()==row['source_sha256']
        assert '\\newcommand{\\'+key+'}{'+row['rendered']+'}' in generated
    used=set(re.findall(r'\\(res[A-Za-z]+)',text+generated))
    defined=set(re.findall(r'\\newcommand\{\\(res[A-Za-z]+)\}',generated))
    assert used<=defined,used-defined
    # Mutation checks ensure common accidental result literals are rejected.
    for bad in ['Observed risk was 3.14 percent.','We tested 123 tasks.']:
        try:check_source(bad)
        except ValueError:pass
        else:raise AssertionError('numeric-literal guard failed')
    print(len(provenance),'empirical macro values have matching source hashes; prose literal mutation checks pass.')
    print('Scope: empirical source provenance. PDF page/theorem/citation numbers and mathematical constants are not result macros.')


if __name__=='__main__':main()
