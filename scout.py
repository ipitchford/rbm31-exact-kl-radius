"""Numerical research scouts, explicitly not proof certificates."""
import argparse
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize, differential_evolution
from scipy.special import xlogy, logsumexp, softmax

BITS = np.array(list(itertools.product([0, 1], repeat=3)))
TARGET = -.75 * np.log(2 * np.sqrt(3) - 3)


def kl(p, q):
    active = p > 0
    if np.any(q[active] <= 0):
        return np.inf
    return float(np.sum(xlogy(p[active], p[active] / q[active])))


def product(m):
    return np.prod(np.where(BITS, m, 1 - m), axis=1)


def atom_fits(p):
    """Interior atom fits from matched marginals; include product baseline."""
    fits = [product(p @ BITS)]
    for atom in range(8):
        flipped = p[np.arange(8) ^ atom]
        m = flipped @ BITS
        c = float(m.sum() - 1 + flipped[0])
        s2 = float(m[0]*m[1] + m[0]*m[2] + m[1]*m[2])
        s3 = float(np.prod(m))
        if abs(c) > 1e-14:
            roots = np.roots([c, -s2, s3])
        elif abs(s2) > 1e-14:
            roots = [s3/s2]
        else:
            roots = []
        for beta in roots:
            if abs(np.imag(beta)) > 1e-10:
                continue
            beta = float(np.real(beta))
            if beta > 1+1e-10 or beta < max(m)-1e-10 or beta <= 0:
                continue
            beta = min(1., beta)
            q = beta * product(np.clip(m/beta, 0, 1))
            q[0] += 1-beta
            if np.max(np.abs(q @ BITS - m)) > 1e-8:
                raise ValueError("Marginal mismatch")
            fits.append(q[np.arange(8) ^ atom])
    return fits


def conditional_fits(p):
    fits = []
    for i in range(3):
        q = np.zeros(8)
        for value in range(2):
            mask = BITS[:, i] == value
            mass = p[mask].sum()
            if mass:
                marginals = p[mask] @ BITS[mask] / mass
                q += mass * product(marginals)
        fits.append(q)
    return fits


def upper(p, family="atom"):
    fits = atom_fits(p)
    if family == "combined":
        fits += conditional_fits(p)
    return min(kl(p, q) for q in fits)


def cell_matrix():
    rows = []
    for a in range(8):
        for b in range(a+1, 8):
            lo, hi = a & b, a | b
            if lo == a or lo == b:
                continue
            row = np.zeros(8)
            row[lo] += 1
            row[hi] += 1
            row[a] -= 1
            row[b] -= 1
            rows.append(row)
    return np.array(rows)


CELL = cell_matrix()


def cell_distance(p):
    """Four convex log-coordinate minimizations, approximate only."""
    answers = []
    for flip in (0, 1, 2, 4):
        a = CELL[:, np.arange(8) ^ flip][:, :7]
        def obj(y):
            z = np.r_[y, 0.]
            return logsumexp(z) - p @ z
        def jac(y):
            return (softmax(np.r_[y, 0.]) - p)[:7]
        r = minimize(obj, np.zeros(7), jac=jac, method="SLSQP",
                     constraints=[{"type":"ineq", "fun":lambda y: a@y,
                                   "jac":lambda y:a}],
                     options={"ftol":1e-12, "maxiter":1000})
        q = softmax(np.r_[r.x, 0.])
        answers.append({"flip":flip,"distance":kl(p,q),"q":q.tolist(),
                        "success":bool(r.success),"residual":float(np.min(a@r.x))})
    return answers


def irreducible_supports():
    out = []
    for mask in range(1, 256):
        s = [x for x in range(8) if mask & (1 << x)]
        if all(any(x in s and (x ^ bit) not in s and not(x & bit) for x in range(8))
               and any(x in s and (x ^ bit) not in s and (x & bit) for x in range(8))
               for bit in (1,2,4)):
            out.append(s)
    return out


def orbit_key(s):
    images = []
    for perm in itertools.permutations(range(3)):
        for flip in range(8):
            image = []
            for x in s:
                b = BITS[x, perm]
                image.append(int(b @ np.array([4,2,1])) ^ flip)
            images.append(tuple(sorted(image)))
    return min(images)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=60)
    ap.add_argument("--family", choices=["atom","combined"], default="atom")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    supports = sorted(set(orbit_key(s) for s in irreducible_supports()), key=lambda x:(len(x),x))
    results = []
    for k,s in enumerate(supports):
        def decode(w):
            p = np.zeros(8)
            w = np.maximum(w, 1e-15)
            p[list(s)] = w/w.sum()
            return p
        res = differential_evolution(lambda w:-upper(decode(w),args.family),
              [(0,1)]*len(s),seed=4200+k,maxiter=args.rounds,popsize=10,
              tol=1e-8,polish=True)
        p = decode(res.x)
        record = {"support":s,"upper":upper(p,args.family),"p":p.tolist(),
                  "cells":cell_distance(p)}
        results.append(record)
        print(json.dumps(record),flush=True)
    report = {"kind":"numerical reconnaissance only", "target":TARGET,
              "family":args.family,"rounds":args.rounds,"results":results}
    if args.out:
        args.out.write_text(json.dumps(report,indent=2)+"\n")


if __name__ == "__main__":
    main()
