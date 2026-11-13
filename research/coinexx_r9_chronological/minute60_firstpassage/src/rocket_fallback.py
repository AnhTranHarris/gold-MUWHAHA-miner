"""Standalone BSD-style MiniROCKET-inspired fixed convolution transform.

**NOT the aeon MiniRocket implementation**. Exact aeon package unavailable offline.
Uses canonical combinations C(9,3)=84 length-9, balanced (+2,-1) kernels,
dilations (1,2,4,8), and training-only fitted per-kernel convolution
quantile biases; positive proportion pooling (PPV). Binary sequence classifier
is trained separately. Replaces no official library, never reads future paths.
"""
from __future__ import annotations
from itertools import combinations
import numpy as np
from numba import njit,prange

KERNELS=np.full((84,9),-1,dtype=np.float32)
for i,idx in enumerate(combinations(range(9),3)):
    KERNELS[i,list(idx)]=2.
DILATIONS=np.array([1,2,4,8],dtype=np.int32)
CHANNELS=np.array([0,1,2,3,4],dtype=np.int32)
QUANTILES=np.array([0.25,0.50,0.75],dtype=np.float32)

@njit(cache=True,parallel=True)
def conv_pool(X,kernels,dilations,channels,bias):
    n,c,ln=X.shape
    combos=len(channels)*len(dilations)*len(kernels)
    out=np.empty((n,combos*bias.shape[1]),np.float32)
    for a in prange(n):
        b=0
        for q in range(len(channels)):
            ch=channels[q]
            for d in dilations:
                # Symmetric zero padding; don't use future QUOTES, just zeros
                pad=(8*d)//2
                for kernel in kernels:
                    pp=np.zeros(bias.shape[1],np.int32)
                    for t in range(ln):
                        acc=0.0
                        for j in range(9):
                            pos=t+(j*d)-pad
                            if 0<=pos<ln:
                                acc+=X[a,ch,pos]*kernel[j]
                        for v in range(bias.shape[1]):
                            if acc>bias[b,v]:pp[v]+=1
                    for v in range(bias.shape[1]):
                        out[a,b*bias.shape[1]+v]=pp[v]/ln
                    b+=1
    return out

@njit(cache=True)
def fit_bias(X,kernels,dilations,channels,quantiles):
    # training only; pick sample from training split prior to transform
    n,c,ln=X.shape
    combos=len(channels)*len(dilations)*len(kernels)
    result=np.zeros((combos,len(quantiles)),np.float32)
    jidx=0
    for q in range(len(channels)):
        ch=channels[q]
        for d in dilations:
            pad=(8*d)//2
            for kernel in kernels:
                pool=np.empty(n*ln,np.float32)
                where=0
                for a in range(n):
                    for t in range(ln):
                        acc=0.0
                        for j in range(9):
                            pos=t+(j*d)-pad
                            if 0<=pos<ln:acc+=X[a,ch,pos]*kernel[j]
                        pool[where]=acc;where+=1
                pool.sort()
                for x,qu in enumerate(quantiles):
                    idx=min(n*ln-1,max(0,int((n*ln-1)*qu)))
                    result[jidx,x]=pool[idx]
                jidx+=1
    return result

class FixedKernelPPV:
    def __init__(self,train_bias_cases=64):
        self.train_bias_cases=train_bias_cases
        self.bias_=None
    def fit(self,X):
        X=np.asarray(X,np.float32)
        if X.ndim!=3 or X.shape[1:]!=(5,120):raise ValueError('Expected (n,5,120)')
        if len(X)==0:raise ValueError('Need training data')
        ids=np.linspace(0,len(X)-1,min(self.train_bias_cases,len(X)),dtype=np.int64)
        self.bias_=fit_bias(X[ids],KERNELS,DILATIONS,CHANNELS,QUANTILES)
        return self
    def transform(self,X):
        if self.bias_ is None:raise ValueError('Fit training biases first')
        X=np.asarray(X,np.float32)
        if X.ndim!=3 or X.shape[1:]!=(5,120):raise ValueError('Expected (n,5,120)')
        return conv_pool(X,KERNELS,DILATIONS,CHANNELS,self.bias_)
