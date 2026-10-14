"""Recovery-window figures and distinct deterministic candidate verification."""
from pathlib import Path
import argparse,json
import numpy as np,pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import brentq
from . import models
from .plotting import savefig,write,BLUE,ORANGE,GRAY

CANDIDATES = [('A-PER-REFINED',1.679033),('A-PER-RERUN',1.6790274114219867),
              ('A-AMP-5',1.679036617960),('A-CAP-EXT',1.679903)]

def run(out):
    out=Path(out); records=[]
    for name,period in CANDIDATES:
        result,trace=models.periodic(period,.2)
        independent,_=models.periodic(period,.2,method='Radau',rtol=2e-12)
        error=max(abs(result[k]-independent[k]) for k in ['J','peak_Z'])
        if error>1e-8:raise RuntimeError(f'Cross-solver disagreement: {name}')
        result.update(run_id=name,initial_periodic_state={k:float(trace[k].iloc[0]) for k in ['C','R','Z']},cross_solver_error=error)
        records.append(result);write(trace,out,name+'_trace')
    (out/'candidate_verification.json').write_text(json.dumps(records,indent=2)+'\n')
    v,trace=models.periodic(1.679033,.2)
    fig,axes=plt.subplots(2,2,figsize=(10,7),layout='constrained')
    for ax,col in zip(axes.ravel(),['C','R','Z','D_relative']):
        ax.plot(trace.time,trace[col],color=BLUE);ax.axvspan(.2*v['T'],v['T'],color=ORANGE,alpha=.12)
        ax.set(xlabel='Normalized time',ylabel=col)
    axes[0,0].step(trace.time,trace.u,label='Administration',color=GRAY,where='post');axes[0,0].legend()
    savefig(fig,out,'recovery_cycle')
    w=np.linspace(0,6,601);R=1-.8*np.exp(-w);D=np.exp(.4*w);V=.8*(-np.expm1(-w))-.15*np.expm1(.4*w)
    star=np.log(.8/(.15*.4))/1.4;end=brentq(lambda x:.8*(-np.expm1(-x))-.15*np.expm1(.4*x),star,6)
    periods=np.geomspace(.2,30,150);jj,zz=models.screen(periods,.2,N=1024);ref=models.reference()[0]
    fig,axes=plt.subplots(1,3,figsize=(12,3.6),layout='constrained')
    axes[0].plot(w,V);axes[0].axhline(0,color=GRAY,ls='--');axes[0].axvline(star,color=ORANGE,ls=':');axes[0].set(xlabel='Drug-free wait',ylabel='Reduced V',title='Conditional continuation')
    axes[1].plot(w,R,label='Responsiveness');axes[1].plot(w,.15*(D-1),label='Weighted withdrawal cost');axes[1].legend();axes[1].set(xlabel='Drug-free wait')
    axes[2].plot(.8*periods,jj-ref);axes[2].axhline(0,color=GRAY,ls='--',label='Matched reference');axes[2].axhline(-ref,color=ORANGE,ls=':',label='Absolute J = 0');axes[2].set(xscale='log',xlabel='OFF duration at duty 0.2',ylabel='Full model ΔJ');axes[2].legend()
    savefig(fig,out,'recovery_window')
    rows=pd.DataFrame(dict(wait=w,R=R,D=D,V=V,marginal_recovery=.8*np.exp(-w),marginal_disease=.06*np.exp(.4*w)))
    write(rows,out,'reduced_wait_trace')
    info=json.loads((out/'A_imperfect_information.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(9,3.5),layout='constrained')
    responsiveness=np.linspace(.05,1,100)
    boundary=(1-responsiveness)/(.15*.4)
    axes[0].plot(responsiveness,boundary,color='black')
    axes[0].fill_between(responsiveness,0,boundary,alpha=.15,color=BLUE)
    axes[0].text(.18,2,'Continue pause');axes[0].text(.62,10,'Restart')
    axes[0].set(xlabel='Responsiveness R',ylabel='Disease burden D',ylim=(0,17))
    rates=np.array([.5,1.,2.]);best=np.log(.8*rates/.06)/(rates+.4);calendar=info['calendar_wait']
    common=.8*(-np.expm1(-rates*calendar))-.15*np.expm1(.4*calendar)
    ideal=.8*(-np.expm1(-rates*best))-.15*np.expm1(.4*best)
    ix=np.arange(3);axes[1].bar(ix-.18,common,width=.36,label='One calendar wait',color=GRAY)
    axes[1].bar(ix+.18,ideal,width=.36,label='Ideal rate information',color=BLUE)
    axes[1].set(xticks=ix,xticklabels=['r = 0.5','r = 1','r = 2'],ylabel='Reduced continuation V',
                title=f"Expected V: {common.mean():.6f} vs {ideal.mean():.6f}")
    axes[1].legend()
    savefig(fig,out,'restart_boundary_information')
    (out/'reduced_window.json').write_text(json.dumps(dict(optimal_wait=star,positive_window_end=end,max_value=float(.8*(-np.expm1(-star))-.15*np.expm1(.4*star))),indent=2)+'\n')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);run(ap.parse_args().output)
