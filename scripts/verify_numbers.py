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
    text=re.sub(r'(?s)\\\[.*?\\\]|\$.*?\$|\\begin\{(?:equation|align|gather)\*?\}.*?\\end\{(?:equation|align|gather)\*?\}', '',text)
    text=re.sub(r'(?s)\\begin\{verbatim\}.*?\\end\{verbatim\}','',text)
    # TikZ figures need layout constants (sizes, offsets, axis limits). Plotted
    # data must still come from result macros: plot coordinates may not
    # contain literal digits, and every figure is stripped only after this check.
    for picture in re.findall(r'(?s)\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}',text):
        for coordinates in re.findall(r'(?s)coordinates\s*\{(.*?)\};',picture):
            if re.search(r'\d',re.sub(r'\\res[A-Za-z]+\{?\}?','',coordinates)):
                raise ValueError('Literal data in plot coordinates: '+coordinates.strip()[:80])
    text=re.sub(r'(?s)\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}','',text)
    errors=[]
    for index,line in enumerate(text.splitlines(),1):
        # Only structural setup may opt out, under these closed command names.
        if re.match(r'\s*\\(?:documentclass|usepackage|setcounter|setlength|includegraphics|bibliographystyle|bibliography|input|author|title|begin\{tabular\}|pgfplotsset|usetikzlibrary|renewcommand\{\\arraystretch\})',line):continue
        line=re.sub(r'(?<!\\)%.*','',line)
        line=re.sub(r'\\(?:cite|ref|eqref|label|url|href|texttt|ver)\{[^}]*\}','',line)
        # Empirical results are decimals or percentages; both must come from
        # result macros. Integers (section numbers, RQ names, authored design
        # counts) are structural and may be typed in prose.
        if re.search(r'\d+\.\d+|\d\s*\\%|\d\s*percent',line):errors.append((index,line.strip()))
    if errors:raise ValueError('Unregistered numeric literal in prose: '+repr(errors[:8]))


def main():
    source=(ROOT/'paper/main.tex').read_text(encoding='utf-8')
    # The generated macro block is exempt from the prose check; everything
    # outside it is authored text.
    head,rest=source.split('% BEGIN GENERATED MACROS',1)
    generated,tail=rest.split('% END GENERATED MACROS',1)
    text=head+tail
    check_source(text)
    provenance=json.loads((ROOT/'paper/generated/macro_provenance.json').read_text())
    for key,row in provenance.items():
        assert hashlib.sha256((ROOT/row['source']).read_bytes()).hexdigest()==row['source_sha256']
        assert '\\newcommand{\\'+key+'}{'+row['rendered']+'}' in generated
    used=set(re.findall(r'\\(res[A-Za-z]+)',text+generated))
    defined=set(re.findall(r'\\newcommand\{\\(res[A-Za-z]+)\}',generated))
    assert used<=defined,used-defined
    # Mutation checks ensure common accidental result literals are rejected.
    for bad in ['Observed risk was 3.14 percent.','Risk fell to 29\\% of cases.',
                '\\begin{tikzpicture}\\addplot coordinates {(1,29.83)};\\end{tikzpicture}']:
        try:check_source(bad)
        except ValueError:pass
        else:raise AssertionError('numeric-literal guard failed')
    print(len(provenance),'empirical macro values have matching source hashes; prose literal mutation checks pass.')
    print('Scope: empirical source provenance. PDF page/theorem/citation numbers and mathematical constants are not result macros.')


if __name__=='__main__':main()
