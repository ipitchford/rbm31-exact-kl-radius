"""Scout for a finite convex-cover certificate. Not itself a proof checker."""
import argparse
import itertools
import json
import time
from pathlib import Path

import numpy as np
from scipy.special import xlogy
from scout import BITS, TARGET, product


def parity_projection(atom):
    s = np.sqrt(3.)
    a, b = (2-s)/4, (2*s-3)/4
    base = np.array([.25, a, a, b, a, b, b, 3*a])
    return base[np.arange(8) ^ atom]


STARS = np.array([parity_projection(x) for x in range(8)])
DENO = 2**40


def rational_candidates(p):
    """Round parameters, never tensor entries, preserving membership."""
    result = []
    def add(weight, u, v):
        ints = [int(round(np.clip(x,0,1)*DENO)) for x in [weight,*u,*v]]
        vals = np.array(ints,dtype=float)/DENO
        a,rest = vals[0],vals[1:]
        q = a*product(rest[:3])+(1-a)*product(rest[3:])
        result.append((q,{"kind":"mixture","denominator":DENO,"numerators":ints}))
    m = p @ BITS
    add(1,m,m)
    for atom in range(8):
        flipped = p[np.arange(8)^atom]
        m = flipped @ BITS
        c = float(m.sum()-1+flipped[0])
        s2 = float(m[0]*m[1]+m[0]*m[2]+m[1]*m[2])
        s3 = float(np.prod(m))
        rs = np.roots([c,-s2,s3]) if abs(c)>1e-14 else ([s3/s2] if abs(s2)>1e-14 else [])
        for beta in rs:
            if abs(np.imag(beta))>1e-10:
                continue
            beta = float(np.real(beta))
            if beta<=0 or beta>1+1e-10 or beta<max(m)-1e-10:
                continue
            beta = min(1.,beta)
            t = np.clip(m/beta,0,1)
            t = np.where(BITS[atom],1-t,t)
            add(beta,t,BITS[atom])
    for i in range(3):
        mask = BITS[:,i]==0
        a = p[mask].sum()
        u = p[mask]@BITS[mask]/a if a else np.zeros(3)
        v = p[~mask]@BITS[~mask]/(1-a) if a<1 else np.zeros(3)
        add(a,u,v)
    return result


def roots(support):
    """Cone ordered parity simplices from the optional extra vertex."""
    eye = np.eye(8)
    if support == (0,3,5,6):
        return [np.array([eye[list(order[:k])].mean(axis=0) for k in range(1,5)])
                for order in itertools.permutations(support)]
    if support == (0,1,2,4,7):
        return [np.array([eye[0]] + [eye[list(order[:k])].mean(axis=0) for k in range(1,5)])
                for order in itertools.permutations((1,2,4,7))]
    return [eye[list(support)]]


def max_scores(vertices, qs):
    entropy_part = np.sum(xlogy(vertices, vertices),axis=1)
    # q=0 with positive p gives infinity; 0 log 0 contributes zero.
    scores = np.array([entropy_part - np.sum(xlogy(vertices,q),axis=1) for q in qs])
    return np.max(scores,axis=1)


def best_fit(vertices):
    star_scores = max_scores(vertices,STARS)
    j = np.argmin(star_scores)
    equality_ok = True
    if star_scores[j] > TARGET-1e-10:
        parity = np.array([.25 if (x.bit_count()-int(j).bit_count())%2==0 else 0 for x in range(8)])
        for v in vertices:
            score = np.sum(xlogy(v,v)-xlogy(v,STARS[j]))
            if score > TARGET-1e-10 and not np.array_equal(v,parity):
                equality_ok = False
    if star_scores[j] <= TARGET + 2e-14 and equality_ok:
        return float(star_scores[j]), {"kind":"star","atom":int(j)}
    center = vertices.mean(axis=0)
    candidates = rational_candidates(center)
    qs = [q for q,_ in candidates]
    scores = max_scores(vertices,qs)
    k = np.argmin(scores)
    return float(scores[k]), candidates[k][1]


def cover(support, max_nodes=100000, output=None):
    pending = [(r, 0, str(j)+":") for j,r in enumerate(roots(support))]
    leaves = []
    splits = []
    seen, max_depth = 0, 0
    start = time.monotonic()
    while pending and seen < max_nodes:
        vertices, depth, address = pending.pop()
        seen += 1
        max_depth = max(max_depth,depth)
        score, witness = best_fit(vertices)
        if score <= TARGET + (2e-14 if witness["kind"]=="star" else -1e-8):
            leaves.append({"path":address,"score":score,"witness":witness})
        else:
            dist = np.sum((vertices[:,None,:]-vertices[None,:,:])**2,axis=2)
            i,j = np.unravel_index(dist.argmax(),dist.shape)
            mid = (vertices[i]+vertices[j])/2
            a,b = vertices.copy(),vertices.copy()
            a[i],b[j] = mid,mid
            splits.append({"path":address,"edge":[int(i),int(j)]})
            pending.append((a,depth+1,address+"0"))
            pending.append((b,depth+1,address+"1"))
        if seen % 2000 == 0:
            print(json.dumps({"support":support,"seen":seen,"pending":len(pending),
                "leaves":len(leaves),"depth":max_depth,"seconds":time.monotonic()-start}),flush=True)
    report = {"kind":"UNVERIFIED floating-point cover scout", "support":support,
              "complete":not pending,"nodes":seen,"depth":max_depth,"seconds":time.monotonic()-start,
              "leaves":leaves,"splits":splits,"pending":len(pending)}
    if output:
        output.write_text(json.dumps(report,separators=(",",":"))+"\n")
    print(json.dumps({k:v for k,v in report.items() if k not in ("leaves","splits")}),flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("support",help="Comma separated cube vertex indices")
    ap.add_argument("--max-nodes",type=int,default=100000)
    ap.add_argument("--out",type=Path)
    args = ap.parse_args()
    cover(tuple(map(int,args.support.split(","))),args.max_nodes,args.out)
