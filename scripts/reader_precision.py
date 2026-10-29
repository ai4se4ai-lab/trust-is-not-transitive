"""One-time optional precision edits following the successful reader reassessment."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'paper/main.tex'
s=p.read_text(encoding='utf-8')
changes=[
('A valid $T_b$ verdict is insufficient evidence for a raw $T_j$ verdict:\ntheir judge-interface premises differ.',
 "A guarantee valid for $T_b$'s structured interface cannot be reused for raw\n$T_j$: the input premise differs."),
('The closed JSON DSL declares layers, scopes, required/provided evidence,',
 'The closed JSON domain-specific language (DSL) declares layers, scopes, evidence,'),
('raw\njudge interfaces that require quarantine','a raw\njudge view when its contract requires quarantine'),
('This is more conservative, but avoids hidden','This avoids hidden'),
(r'For trusted view $x\sim D_X$, let $r_0(x)$ be cheap-acceptance risk, $r_1(x)$'+'\n'+
 'escalation risk, $d(x)>0$ its extra cost, and $c_0(x)$ baseline cost. A',
 r'For $x\sim D_X$, let $r_0(x),r_1(x)$ be conditional probabilities of the same'+'\n'+
 'joint unsafe-acceptance event under cheap acceptance or escalation given $x$.\n'+
 'Let $d(x)>0$ be extra cost and $c_0(x)$ baseline cost. A'),
('its selected threshold. Raw and structured judges are scripted, not official',
 'its selected threshold. Rules-only accepts after hard pass; invalid delegation\n'+
 'adds a nominal scorer charge to judge-only despite equal verdicts. Cost units\n'+
 'are protocol charges, not call profiling. Judges are scripted, not official'),
('no candidate below the frozen risk budget. The runtime denies uncertified',
 'no candidate whose simultaneous upper-risk bound met the budget. It denies'),
('The present artifact does not justify a completed TSE effectiveness claim.',
 'The artifact does not establish real-agent safety or resource advantage.'),
('No remote publication or archival DOI was created. The historical primary',
 'The artifact is local; no archival release or DOI was created. Historical primary'),
]
for old,new in changes:
    assert old in s,old
    s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8',newline='\n')
print('Reader precision edits applied; no results changed.')
