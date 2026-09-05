"""Standalone checker, separately implemented from discovery.

Python standard library, exact arithmetic; producer-coordinated implementation,
not independent-person verification.

No optimizer, numpy, scipy, floating-point logarithm, or discovery-code import.
The mathematical reduction and convexity argument are in PROOF.md.
"""
import argparse
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from itertools import permutations
import hashlib
import json
from math import isqrt
from pathlib import Path
import time


PRECISION = 128
SCALE = 1 << PRECISION
TERMS = 48
SUPPORTS = ((0,7),(0,3,5),(0,1,2,7),(0,3,5,6),(0,1,2,4,7),(0,1,2,5,6,7))
FILES = ("two","three","four","parity","five","six")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceiling(n, d):
    return -((-n)//d)


def log_unit(n, d):
    """Bounds for log(n/d), 1 <= n/d <= 2, in units of 2^-128.

    log u = 2 sum_{j>=0} y^(2j+1)/(2j+1), y=(u-1)/(u+1).
    Each product/division is rounded outwards with integer arithmetic.
    After N terms, the tail is <= 9/[4(2N+1)3^(2N+1)].
    """
    require(d <= n <= 2*d, "log range reduction")
    if n == d:
        return 0,0
    yn,yd = n-d,n+d
    lo,hi = yn*SCALE//yd,ceiling(yn*SCALE,yd)
    sqlo,sqhi = lo*lo//SCALE,ceiling(hi*hi,SCALE)
    plo,phi = lo,hi
    slo,shi = 0,0
    for j in range(TERMS):
        den = 2*j+1
        slo += plo//den
        shi += ceiling(phi,den)
        plo = plo*sqlo//SCALE
        phi = ceiling(phi*sqhi,SCALE)
    tail = ceiling(9*SCALE,4*(2*TERMS+1)*3**(2*TERMS+1))
    return 2*slo,2*shi+tail


LOG_TWO = log_unit(2,1)


@lru_cache(maxsize=None)
def log_interval(x):
    require(x>0,"log argument must be positive")
    n,d = x.numerator,x.denominator
    k = n.bit_length()-d.bit_length()
    if k>=0:
        d <<= k
    else:
        n <<= -k
    if n<d:
        n <<= 1
        k -= 1
    if n>=2*d:
        d <<= 1
        k += 1
    lo,hi = log_unit(n,d)
    if k>=0:
        return lo+k*LOG_TWO[0],hi+k*LOG_TWO[1]
    return lo+k*LOG_TWO[1],hi+k*LOG_TWO[0]


@dataclass(frozen=True)
class Quad:
    """Exact elements a+b*sqrt(3)."""
    a: F = F(0)
    b: F = F(0)

    def __post_init__(self):
        object.__setattr__(self,"a",F(self.a))
        object.__setattr__(self,"b",F(self.b))

    def __add__(self,other):
        other = other if isinstance(other,Quad) else Quad(other)
        return Quad(self.a+other.a,self.b+other.b)
    __radd__ = __add__

    def __neg__(self):
        return Quad(-self.a,-self.b)

    def __sub__(self,other):
        return self + (-other if isinstance(other,Quad) else Quad(-other))

    def __rsub__(self,other):
        return -self+other

    def __mul__(self,other):
        other = other if isinstance(other,Quad) else Quad(other)
        return Quad(self.a*other.a+3*self.b*other.b,self.a*other.b+self.b*other.a)
    __rmul__ = __mul__

    def __pow__(self,n):
        require(type(n) is int and n>=0,"quadratic power")
        out = Quad(1)
        for _ in range(n):
            out = out*self
        return out

    def sign(self):
        a,b = self.a,self.b
        if b==0:
            return (a>0)-(a<0)
        if a>=0 and b>=0:
            return 1
        if a<=0 and b<=0:
            return -1
        diff = a*a-3*b*b
        return ((diff>0)-(diff<0)) if a>0 else ((diff<0)-(diff>0))

    def interval(self):
        if self.b>=0:
            return self.a+self.b*SQRT_LO,self.a+self.b*SQRT_HI
        return self.a+self.b*SQRT_HI,self.a+self.b*SQRT_LO


SQRT_FLOOR = isqrt(3*SCALE*SCALE)
require(SQRT_FLOOR**2 < 3*SCALE*SCALE < (SQRT_FLOOR+1)**2,"sqrt enclosure")
SQRT_LO,SQRT_HI = F(SQRT_FLOOR,SCALE),F(SQRT_FLOOR+1,SCALE)
STAR = (Quad(F(1,4)),Quad(F(1,2),F(-1,4)),Quad(F(1,2),F(-1,4)),
        Quad(F(-3,4),F(1,2)),Quad(F(1,2),F(-1,4)),Quad(F(-3,4),F(1,2)),
        Quad(F(-3,4),F(1,2)),Quad(F(3,2),F(-3,4)))
R_LO,R_HI = (Quad(-3,2)).interval()
C_LO = F(-3,4)*log_interval(R_HI)[1]
C_HI = F(-3,4)*log_interval(R_LO)[0]


@lru_cache(maxsize=None)
def star_logs(atom):
    out = []
    for x in range(8):
        lo,hi = STAR[x^atom].interval()
        out.append((log_interval(lo)[0],log_interval(hi)[1]))
    return tuple(out)


def lower_certificate():
    alpha = Quad(F(1,2),F(-1,6))
    beta = 1-alpha
    t = Quad(F(3,2),F(-1,2))
    for z in (alpha,beta,t,1-t):
        require(z.sign()>0,"positive mixture parameters")
    q = tuple(beta*t**x.bit_count()*(1-t)**(3-x.bit_count())+(alpha if x==0 else 0)
              for x in range(8))
    require(q==STAR and sum(q)==Quad(1),"exact star decomposition")
    pairs = [(a,b) for a in range(8) for b in range(a+1,8)
             if (a&b) not in (a,b)]
    require(len(pairs)==9,"nine supermodular inequalities")
    active = []
    for a,b in pairs:
        det = q[a&b]*q[a|b]-q[a]*q[b]
        require(det.sign()>=0,"star supermodularity")
        if det==Quad(0):
            row = [0]*8
            row[a&b] += 1
            row[a|b] += 1
            row[a] -= 1
            row[b] -= 1
            active.append(row)
    require(len(active)==3,"three active square faces")
    p = [F(1,4) if x.bit_count()%2==0 else F(0) for x in range(8)]
    multiplier = Quad(F(1,2),F(-1,4))
    require(multiplier.sign()>0,"positive KKT multiplier")
    for x in range(8):
        require(q[x]-p[x]==multiplier*sum(row[x] for row in active),"exact KKT identity")
    require(4*q[3]==Quad(-3,2),"exact objective constant")
    even_flips = (0,3,5,6)
    require({min(x,x^7) for x in even_flips}=={0,1,2,3},"four orientation classes")
    return {"status":"PASS","active_faces":3,"orientations":4}


def transform(s,perm,flip):
    return tuple(sorted(sum(((x>>old)&1)<<new for new,old in enumerate(perm))^flip for x in s))


def orbit(s):
    return min(transform(s,p,f) for p in permutations(range(3)) for f in range(8))


def support_certificate():
    irreducible = []
    for mask in range(1,256):
        s = tuple(x for x in range(8) if (mask>>x)&1)
        comparable = False
        for bit in (1,2,4):
            a = {x for x in s if not(x&bit)}
            b = {x^bit for x in s if x&bit}
            if a<=b or b<=a:
                comparable = True
        if not comparable:
            irreducible.append(s)
    representatives = sorted({orbit(s) for s in irreducible},key=lambda s:(len(s),s))
    require(tuple(representatives)==SUPPORTS,"complete support orbit classification")
    require(len(irreducible)==50,"irreducible support count")
    counts = {str(s):sum(orbit(t)==s for t in irreducible) for s in SUPPORTS}
    return {"status":"PASS","nonempty_supports":255,"irreducible_supports":50,"orbits":counts}


def unit(x):
    return tuple(F(int(i==x)) for i in range(8))


def average(points):
    return tuple(sum(p[x] for p in points)/len(points) for x in range(8))


def root_simplices(support):
    if support==(0,3,5,6):
        return [tuple(average([unit(x) for x in order[:k]]) for k in range(1,5))
                for order in permutations(support)]
    if support==(0,1,2,4,7):
        return [tuple([unit(0)]+[average([unit(x) for x in order[:k]]) for k in range(1,5)])
                for order in permutations((1,2,4,7))]
    return [tuple(unit(x) for x in support)]


@lru_cache(maxsize=None)
def negative_entropy_bounds(p):
    lo,hi = F(0),F(0)
    for px in p:
        if px:
            l,h = log_interval(px)
            lo += px*l
            hi += px*h
    return lo,hi


def witness_logs(w):
    if w.get("kind")=="star":
        require(type(w.get("atom")) is int and 0<=w["atom"]<8,"star atom index")
        return star_logs(w["atom"])
    require(w.get("kind")=="mixture","recognized model witness")
    den = w.get("denominator")
    ns = w.get("numerators")
    require(type(den) is int and den>0,"positive mixture denominator")
    require(type(ns) is list and len(ns)==7,"seven mixture parameters")
    require(all(type(n) is int and 0<=n<=den for n in ns),"mixture parameters in [0,1]")
    a = F(ns[0],den)
    u,v = [F(n,den) for n in ns[1:4]],[F(n,den) for n in ns[4:7]]
    q = []
    for x in range(8):
        pu,pv = F(1),F(1)
        for i,bit in enumerate((4,2,1)):
            pu *= u[i] if x&bit else 1-u[i]
            pv *= v[i] if x&bit else 1-v[i]
        q.append(a*pu+(1-a)*pv)
    require(sum(q)==1 and all(y>=0 for y in q),"normalized nonnegative mixture")
    return tuple(log_interval(y) if y else None for y in q)


def exact_parity_equality(p,w):
    if w.get("kind")!="star":
        return False
    parity = w["atom"].bit_count()%2
    return all(p[x]==(F(1,4) if x.bit_count()%2==parity else 0) for x in range(8))


def vertex_slack(p,w,logs):
    require(sum(p)==1 and all(x>=0 for x in p),"probability simplex vertex")
    if exact_parity_equality(p,w):
        return None
    upper = negative_entropy_bounds(p)[1]
    for x,px in enumerate(p):
        if px:
            require(logs[x] is not None,"witness covers target support")
            upper -= px*logs[x][0]
    slack = C_LO-upper
    require(slack>0,f"uncertified vertex inequality: slack={slack/SCALE}")
    return slack


def verify_cover(data):
    require(data.get("format")=="rbm31-convex-cover-v1","certificate format")
    support = tuple(data["support"])
    require(support in SUPPORTS,"recognized support")
    nodes = {}
    for typ in ("splits","leaves"):
        for record in data[typ]:
            path = record["path"]
            require(type(path) is str and path not in nodes,"unique node address")
            nodes[path] = (typ,record)
    pending = [(str(i)+":",s) for i,s in enumerate(root_simplices(support))]
    visited = set()
    leaf_count,vertex_count,equalities = 0,0,0
    minimum = None
    while pending:
        path,vertices = pending.pop()
        require(path in nodes,"coverage: every child must exist")
        require(path not in visited,"coverage: node not revisited")
        visited.add(path)
        typ,rec = nodes[path]
        if typ=="splits":
            edge = rec["edge"]
            require(type(edge) is list and len(edge)==2,"split edge pair")
            i,j = edge
            require(type(i) is int and type(j) is int and 0<=i<len(vertices) and
                    0<=j<len(vertices) and i!=j,"valid split endpoints")
            midpoint = average([vertices[i],vertices[j]])
            a,b = list(vertices),list(vertices)
            a[i],b[j] = midpoint,midpoint
            pending.append((path+"0",tuple(a)))
            pending.append((path+"1",tuple(b)))
        else:
            leaf_count += 1
            w = rec["witness"]
            logs = witness_logs(w)
            for p in vertices:
                vertex_count += 1
                slack = vertex_slack(p,w,logs)
                if slack is None:
                    equalities += 1
                elif minimum is None or slack<minimum:
                    minimum = slack
    require(visited==set(nodes),"no orphan or unreachable certificate nodes")
    return {"support":support,"status":"PASS","leaves":leaf_count,"nodes":len(nodes),
            "roots":len(root_simplices(support)),
            "maximum_depth":max(len(address.split(":")[1]) for address in nodes),
            "vertex_checks":vertex_count,"exact_parity_equalities":equalities,
            "strict_slack_lower_bound":str(minimum/SCALE),
            "strict_slack_decimal_for_display":float(minimum/SCALE)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--directory",type=Path,default=Path(__file__).resolve().parent)
    ap.add_argument("--out",type=Path)
    args = ap.parse_args()
    start = time.monotonic()
    report = {"kind":"exact standard-library certificate replay","lower_bound":lower_certificate(),
              "support_reduction":support_certificate(),"covers":[],"sha256":{}}
    for support,name in zip(SUPPORTS,FILES):
        path = args.directory/"certificates"/f"{name}.json"
        raw = path.read_bytes()
        data = json.loads(raw)
        require(tuple(data["support"])==support,"all six required covers in prescribed order")
        result = verify_cover(data)
        report["covers"].append(result)
        report["sha256"][path.name] = hashlib.sha256(raw).hexdigest()
        print(json.dumps(result),flush=True)
    report["status"] = "PASS"
    report["precision_bits"] = PRECISION
    report["log_series_terms"] = TERMS
    report["seconds"] = time.monotonic()-start
    report["total_leaves"] = sum(x["leaves"] for x in report["covers"])
    report["total_vertex_checks"] = sum(x["vertex_checks"] for x in report["covers"])
    report["total_roots"] = sum(x["roots"] for x in report["covers"])
    report["maximum_depth"] = max(x["maximum_depth"] for x in report["covers"])
    if args.out:
        args.out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k not in ("covers","sha256")}),flush=True)


if __name__=="__main__":
    main()
