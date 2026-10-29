"""Remove duplicated process/limitation prose while preserving substantive limits."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'paper/main.tex'
s=p.read_text(encoding='utf-8')
i=s.index(r'\subsection{Assumption audit and threats to validity}')
j=s.index(r'\section{Related Work}',i)
s=s[:i]+r'''\subsection{Assumption audit and threats to validity}
\textbf{Internal validity.} The primary arithmetic defect is preserved, and
fresh-seed correction remains exploratory. The designer authored labels,
templates and planted mutations; these are not independent observations of
semantic safety. Regression tests check configuration identity, not arbitrary
plugin correctness. Original synthesis counts remain unavailable.

\textbf{External validity.} No real base LLM, pretrained guard, official defense,
external benchmark, completed development task or practitioner workflow was
evaluated. Inference load, real token/GPU cost, long sessions and temporal drift
are untested. Local CPU results and modeled units cannot establish deployment
performance or savings.

\textbf{Construct validity.} The distinct denominators in Definition~VIII must
not be interchanged. Benign acceptance is not task completion; structured
quarantine is not semantic noninterference. Trusted context identity does not
establish stationarity, and complete dependency tracking remains a host premise.

\textbf{Conclusion validity.} Seeds sample one authored law, not independent
developers or tasks. Conservative correction can produce infeasibility.
Pairwise correlation cannot establish the needed joint structure. Numeric
lint checks empirical source provenance, not every PDF glyph; notation lint
is a registry check, not a semantic proof. These limitations qualify every
statistical and formal conclusion.

'''+s[j:]
i=s.index('The main lesson is a specification discipline:')
j=s.index('Future evaluation must use real proposal-generating LLMs',i)
s=s[:i]+'''A verdict is usable only under its stated premises. The canonical example
exposes invalid composition; its stronger control shows that ordinary mediation
already protects the hard property. Route sums prevent a separate probability
error: importing veto intersections into early acceptance. These are established
principles made executable, not newly discovered safety laws.

Primary infeasibility demonstrates correct denial without useful service.
Exploratory correction restores some utility but leaves implicit unsafe actions
and fails under the designed shift. Equal checked-control decisions show that
certification does not repair an unchanged detector. Distinctive practical
value therefore remains a research question.

'''+s[j:]
s=s.replace('the primary low-risk point denies all benign tasks. Equal points overlap.\nThese plots compare configurations, not external model Pareto frontiers.',
'''the primary low-risk point denies all benign tasks. Coincident points are
grouped; u labels benign acceptance. Both panels share the risk scale. These
are local configurations, not external-model Pareto frontiers.''')
s=s.replace(r'\begin{definition}[Residual risk, cost and latency]',r'\begin{definition}[Residual risk, cost and latency]\label{def:metrics}')
s=s.replace(r'Definition~VIII',r'Definition~\ref{def:metrics}')
p.write_text(s,encoding='utf-8',newline='\n')
print('Compacted repeated limitations; definitions and observations retained.')
