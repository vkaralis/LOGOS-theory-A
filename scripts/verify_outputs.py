"""Check regenerated tables, extensions and phase classifications."""
from pathlib import Path
import argparse,json,re
import xml.etree.ElementTree as ET
from PIL import Image
import pandas as pd

ap=argparse.ArgumentParser();ap.add_argument('results',type=Path);a=ap.parse_args();out=a.results
checks=[]
def check(label,got,expected,tolerance=0):
    error=abs(got-expected);checks.append(dict(check=label,error=float(error),tolerance=tolerance,passed=bool(error<=tolerance)))
def load(name):return json.loads((out/name).read_text())
s=load('model_summary.json');check('fixed cycle J',s['fixed_candidate']['J'],.080905389814,1e-8)
check('fixed cycle peak',s['fixed_candidate']['peak_Z'],.188070550584,1e-8)
check('alternative gate',s['alternative_gate']['J'],.078853,1e-6)
check('absorption',s['finite_absorption']['J'],.078428,1e-6)
check('reduced wait',s['reduced']['rate1_optimal_wait'],1.850191,1e-6)
check('reduced window endpoint',s['reduced']['rate1_positive_window_end'],4.593169,1e-6)
constant=load('A_constant_family.json');check('stationary upper bound',constant['constant_global_upper_bound'],.073717,1e-6)
finite=load('A_finite_constant_family.json');check('finite upper bound',finite['constant_upper_bound'],.050307,1e-6)
check('finite witness',finite['cycle']['J'],.0552361206,1e-8)
rob=load('A_robustness.json')['summary']
for key,val in [('fixed_feasible',25),('fixed_feasible_strict',22),('selected_feasible',29),('selected_strict',24)]:check(key,rob[key],val)
phase=pd.read_csv(out/'tables/S10_canonical_phase_map.csv')
for cap,label,count in [(.5,'Objective gain',425),(.5,'Reference retained',15),(.22,'Feasibility restoration',242),(.22,'No sampled safe candidate',198)]:
    check(f'phase {cap} {label}',len(phase[(phase.cap==cap)&(phase.label==label)]),count)
for cap,count in [(.5,200),(.22,101)]:check(f'nonpositive {cap}',len(phase[(phase.cap==cap)&phase.nonpositive]),count)
noise=load('A_imperfect_information.json')['noise_results']
for row,value in zip(noise,[.490431,.489290,.486820,.484234,.482958]):check(f"information SD {row['log_rate_measurement_SD']}",row['expected_value'],value,1e-6)
for filename in ['A_extension_verification.json','A_finite_constant_family.json']:
    if not load(filename)['all_passed']:raise SystemExit(f'Failed internal checks: {filename}')
if len(load('candidate_verification.json'))!=4:raise SystemExit('Missing candidate identities')
figure_names = ['F05_canonical_cycle', 'F06_canonical_gain_and_finite',
    'F07_reduced_restart_information', 'F08_palbociclib_matched_budget',
    'F09_canonical_phase_map', 'F10_canonical_controls', 'recovery_cycle',
    'recovery_window', 'restart_boundary_information']
for name in figure_names:
    base = out/'figures'/name
    with Image.open(base.with_suffix('.png')) as im:
        if any(key.lower() in {'software','author','creator','creation time','comment'}
               for key in im.info):
            raise SystemExit(f'Unexpected PNG metadata: {name}')
    svg = ET.parse(base.with_suffix('.svg'))
    if any(node.tag.rsplit('}',1)[-1]=='metadata' for node in svg.iter()):
        raise SystemExit(f'Unexpected SVG metadata: {name}')
    pdf = base.with_suffix('.pdf').read_bytes()
    if re.search(rb'/(?:Creator|Producer|CreationDate|ModDate|Author|Title|Subject|Keywords)\b', pdf):
        raise SystemExit(f'Unexpected PDF metadata: {name}')
print(f'All {len(figure_names)*3} figures verified without attribution or date metadata.')
report=dict(all_passed=all(x['passed'] for x in checks),checks=checks)
(out/'release_verification.json').write_text(json.dumps(report,indent=2)+'\n')
if not report['all_passed']:raise SystemExit([x for x in checks if not x['passed']])
print(f'All {len(checks)} release benchmark checks passed.')
