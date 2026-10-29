"""F401-R145 Bayesian online normal-mean change point update.
RESEARCH ONLY. One observed completed native quote bar per update.
Direct lightweight source subset; full tested publisher plus full eight-cell
R143 masks and MQL5 header are in the separate hash-verified 102.8MB package.
"""
from math import exp,sqrt,erfc,pi
def update(p,mu,kappa,z,hazard=1/64,mu0=0.,k0=2.,sigma=1.):
    K=len(p);assert K==len(mu)==len(kappa) and K>=4
    assert 0<hazard<1 and sigma>0 and k0>0
    new=[0.]*K;means=mu[:];precs=kappa[:];var=sigma*sigma
    def dens(x,m,v):return exp(-0.5*(x-m)**2/v)/sqrt(2*pi*v)
    new[0]=hazard*dens(z,mu0,var*(1+1/k0))
    for r in range(K):
        j=min(r+1,K-1)
        new[j]+=p[r]*(1-hazard)*dens(z,mu[r],var*(1+1/kappa[r]))
    means[0]=(k0*mu0+z)/(k0+1);precs[0]=k0+1
    for r in range(1,K):
        precs[r]=kappa[r-1]+1
        means[r]=(kappa[r-1]*mu[r-1]+z)/precs[r]
    denom=sum(new)
    if denom<=1e-300:return ([1.]+[0.]*(K-1),means,precs,1.)
    normalized=[v/denom for v in new]
    return normalized,means,precs,normalized[0]
def signed_quote_predictive(p,mu,kappa,epsilon=.35,sigma=1.):
    bad=good=0.
    for w,m,k in zip(p,mu,kappa):
        sd=sigma*sqrt(1+1/k)
        bad+=w*.5*erfc((epsilon+m)/(sd*sqrt(2)))
        good+=w*.5*erfc((epsilon-m)/(sd*sqrt(2)))
    return bad,good,max(0.,1.-bad-good)
if __name__=="__main__":
    K=32;p=[1.]+[0.]*(K-1);mu=[0.]*K;k=[2.]*K
    for z in [.2,.1,-.4,.8]:
        p,mu,k,cp=update(p,mu,k,z)
    assert abs(sum(p)-1)<1e-12
    print(dict(change=cp,quote_next=signed_quote_predictive(p,mu,k)))
