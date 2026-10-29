"""Extractability, cross-reference and page-bound checks; visual review remains required."""
import json
from pathlib import Path
import re
import fitz
ROOT=Path(__file__).resolve().parents[1]


def main():
    pdf=fitz.open(ROOT/'paper/main.pdf')
    text='\n'.join(page.get_text() for page in pdf)
    # No page cap is imposed for this manuscript; report length for inspection.
    print(len(pdf),'pages (no page limit enforced)')
    assert '??' not in text
    assert 'Trust Is Not Transitive' in text
    # PDF extraction inserts line/page breaks inside otherwise intact phrases.
    normalized=' '.join(text.lower().split())
    assert 'exploratory' in normalized and 'zero benign utility' in normalized
    log=(ROOT/'paper/main.log').read_text(encoding='utf-8',errors='replace')
    assert not re.search(r'Overfull \\[hv]box',log),'Overfull TeX boxes require layout repair'
    assert 'undefined references' not in log
    assert all(page.rect.width>600 and page.rect.height>750 for page in pdf)
    print(len(pdf),'extractable IEEEtran pages; no unresolved references or overfull boxes.')


if __name__=='__main__':main()
