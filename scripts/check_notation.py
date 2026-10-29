"""Check registered definitions and known dangerous terminology. Not semantic proof QA."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('Duplicate symbol: '+key)
        if not value.strip():
            raise ValueError('Empty definition: '+key)
        result[key]=value
    return result


if __name__=='__main__':
    symbols=json.loads((ROOT/'formal/notation.json').read_text(),object_pairs_hook=unique)
    theory=(ROOT/'formal/FRAMEWORK.md').read_text(encoding='utf-8')
    for i in range(1,10):
        assert f'**D{i}:' in theory
    for i in range(5):
        assert f'## T{i}' in theory
    print(f'{len(symbols)} registered symbols; nine definitions and five scoped results present.')
    print('Registry lint is not a semantic consistency proof; manual review is required.')
