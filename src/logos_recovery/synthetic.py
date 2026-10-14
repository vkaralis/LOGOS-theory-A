"""Independent toy ANC panel; no source observations or fitted coefficients."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

SEED = 20261012
COLUMNS = ['pre_gap_ANC', 'restart_dose_mgm2', 'gap_days', 'restart_time']

def generate(seed=SEED, subjects=48):
    if subjects < 8:
        raise ValueError('At least eight synthetic subjects are required.')
    rng = np.random.default_rng(seed)
    rows = []
    for subject in range(subjects):
        offset = rng.normal(0, .12)
        for episode in range(3):
            pre = rng.uniform(.35, 1.4)
            gap = rng.uniform(2, 12)
            restart = pre + rng.uniform(.15, .85) * (1 - np.exp(-gap/5))
            dose = rng.uniform(30, 90)
            time = episode * 30 + rng.uniform(10, 20)
            # Chosen toy equation, deliberately unrelated to source patient fits.
            nadir = max(.05, .2 + .65*restart - .002*dose + .01*gap + offset + rng.normal(0, .08))
            rows.append(dict(subject=f'SYN-{subject+1:03d}', episode=episode+1,
                pre_gap_ANC=pre, pre_restart_ANC=restart, restart_dose_mgm2=dose,
                gap_days=gap, restart_time=time, minimum_ANC=nadir,
                n_visits=int(rng.integers(1,5)), is_synthetic=True))
    return pd.DataFrame(rows)

def evaluate(panel):
    """Hold out whole subjects; all regressions train on remaining subjects."""
    results=[]
    for label, data in [('all',panel), ('two_or_more_visits',panel[panel.n_visits>=2])]:
        z=data.copy()
        for subject in z.subject.unique():
            train=z[z.subject!=subject]; test=z[z.subject==subject]
            for name, cols in [('calendar',COLUMNS), ('state',COLUMNS+['pre_restart_ANC'])]:
                x=np.column_stack([np.ones(len(train)),train[cols].to_numpy()])
                if np.linalg.matrix_rank(x)<x.shape[1]:
                    raise ValueError('Synthetic training design is rank deficient.')
                b=np.linalg.lstsq(x,train.minimum_ANC,rcond=None)[0]
                z.loc[test.index,'pred_'+name]=np.column_stack([np.ones(len(test)),test[cols].to_numpy()])@b
        for name in ['calendar','state']:
            z['loss_'+name]=(z.minimum_ANC-z['pred_'+name])**2
        losses=z.groupby('subject')[['loss_calendar','loss_state']].mean()
        results.append(dict(subset=label,subjects=len(losses),episodes=len(z),
            rmse_calendar=float(np.sqrt(losses.loss_calendar.mean())),
            rmse_state=float(np.sqrt(losses.loss_state.mean())),is_synthetic=True))
    return pd.DataFrame(results)

def run(output):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    panel=generate();panel.to_csv(output/'synthetic_restart_panel.csv',index=False,float_format='%.12g')
    evaluate(panel).to_csv(output/'synthetic_prediction_demo.csv',index=False,float_format='%.12g')
    (output/'synthetic_metadata.json').write_text(json.dumps(dict(seed=SEED,subjects=48,
        episodes=144,source='Independent random toy generation; no real records or source fitted coefficients.',
        limitations='Demonstrates software execution only. No clinical validation or evidence of treatment benefit.'),indent=2)+'\n')
