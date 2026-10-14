"""Constrained drug-free restart in the reduced continuation model."""
import math

def utility(wait, *, B=1., R0=.2, r=1., L=.15, D0=1., g=.4):
    if wait < 0 or not (B>0 and L>0 and D0>0 and r>0 and g>=0 and 0<=R0<=1):
        raise ValueError('Invalid wait or reduced-model parameters.')
    return B*(1-R0)*(-math.expm1(-r*wait))-L*D0*math.expm1(g*wait)

def constrained_wait(*, B=1., R0=.2, r=1., L=.15, D0=1., g=.4,
                     Z0=0., p=1., Zsafe=1., Dmax=math.inf, horizon=6.):
    utility(0,B=B,R0=R0,r=r,L=L,D0=D0,g=g)
    if not (Z0>=0 and p>0 and Zsafe>0 and Dmax>0 and horizon>=0):
        raise ValueError('Invalid safety constraint or horizon.')
    low=max(0.,math.log(Z0/Zsafe)/p) if Z0>0 else 0.
    high=min(horizon,math.log(Dmax/D0)/g) if g>0 else horizon
    if D0>Dmax or low>high:
        return dict(feasible=False,wait=None,value=None,positive_value=False)
    if g==0:
        optimum=high if R0<1 else low
    elif R0==1:
        optimum=low
    else:
        unconstrained=math.log(B*r*(1-R0)/(L*g*D0))/(r+g)
        optimum=min(high,max(low,unconstrained))
    value=utility(optimum,B=B,R0=R0,r=r,L=L,D0=D0,g=g)
    return dict(feasible=True,wait=optimum,value=value,positive_value=value>0,
                minimum_wait=low,maximum_wait=high)
