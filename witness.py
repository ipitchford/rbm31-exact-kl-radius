"""Certified feasible approximations, not a maximum-likelihood solver.

All input probabilities and channel decisions are rational. Returned mixture
parameters lie in Q(sqrt(3)). Internally parameters are least-significant-bit
first, so coordinate i is the bit (x >> i) & 1. The CLI states this convention.
The entire original six-cover certificate is verified before any target query.
"""
import argparse
from fractions import Fraction as F
from itertools import permutations
import json
from pathlib import Path

import verify as V


def probability(values):
    p = tuple(F(x) for x in values)
    V.require(len(p) >= 8 and len(p) & (len(p)-1) == 0, 'power-of-two target length at least eight')
    V.require(all(x >= 0 for x in p) and sum(p) == 1, 'normalized nonnegative target')
    return p


def distribution(components):
    n = len(components[0][1])
    V.require(sum(w for w, _ in components) == V.Quad(1), 'mixture weights sum to one')
    for weight, params in components:
        V.require(len(params) == n and weight.sign() >= 0, 'component arity and weight')
        V.require(all(t.sign() >= 0 and (1-t).sign() >= 0 for t in params), 'Bernoulli parameter range')
    q = []
    for x in range(1 << n):
        total = V.Quad(0)
        for weight, params in components:
            term = weight
            for i, t in enumerate(params):
                term *= t if (x >> i) & 1 else 1-t
            total += term
        q.append(total)
    V.require(sum(q) == V.Quad(1) and all(x.sign() >= 0 for x in q), 'normalized reconstructed model')
    return tuple(q)


def channel_table(p, bit, source, tau):
    """The forward channel in PROOF (7), accepting rational or quadratic tables."""
    q = list(p)
    a = [x for x in range(len(p)) if bool(x & bit) == bool(source)]
    for i in a:
        j = i ^ bit
        q[i] = p[i] * F(1, 1+tau)
        q[j] = p[j] + p[i] * (tau / (1+tau))
    return tuple(q)


def deterministic_components(p, fixed):
    """A fixed bit leaves a two-bit table, decomposed by conditioning a bit."""
    remaining = [i for i in range(3) if i != fixed]
    split, last = remaining
    fixed_value = next((x >> fixed) & 1 for x in range(8) if p[x])
    components = []
    for value in (0, 1):
        mass = sum(p[x] for x in range(8) if ((x >> split) & 1) == value)
        if not mass:
            continue
        params = [V.Quad(0)] * 3
        params[fixed] = V.Quad(fixed_value)
        params[split] = V.Quad(value)
        params[last] = V.Quad(sum(p[x] for x in range(8) if ((x >> split) & 1) == value and (x >> last) & 1) / mass)
        components.append((V.Quad(mass), tuple(params)))
    V.require(distribution(components) == tuple(V.Quad(x) for x in p), 'deterministic decomposition')
    return components


class Oracle:
    def __init__(self, directory=None):
        directory = Path(directory) if directory else Path(__file__).resolve().parent
        V.lower_certificate()
        V.support_certificate()
        self.covers = {}
        for support, name in zip(V.SUPPORTS, V.FILES):
            data = json.loads((directory/'certificates'/f'{name}.json').read_text())
            V.require(tuple(data['support']) == support, 'required support file')
            V.verify_cover(data)
            self.covers[support] = {record['path']: (kind, record)
                                  for kind in ('splits', 'leaves') for record in data[kind]}

    def three_bits(self, values):
        p = probability(values)
        V.require(len(p) == 8, 'three-bit target')
        r, channels = p, []
        components = None
        while True:
            fixed = next((i for i in range(3) if not any(r[x] for x in range(8) if (x >> i) & 1)
                          or not any(r[x] for x in range(8) if not ((x >> i) & 1))), None)
            if fixed is not None:
                components = deterministic_components(r, fixed)
                break
            changed = False
            for bit in (1, 2, 4):
                for source in (0, 1):
                    indices = [x for x in range(8) if bool(x & bit) == bool(source)]
                    if all(not r[x] or r[x ^ bit] > 0 for x in indices):
                        tau = min(r[x ^ bit] / r[x] for x in indices if r[x])
                        reduced = list(r)
                        for x in indices:
                            reduced[x] = (1+tau)*r[x]
                            reduced[x ^ bit] = r[x ^ bit]-tau*r[x]
                        reduced = tuple(reduced)
                        V.require(channel_table(reduced, bit, source, tau) == r, 'exact channel reconstruction')
                        V.require(sum(x > 0 for x in reduced) < sum(x > 0 for x in r), 'strict support decrease')
                        channels.append((bit, source, tau))
                        r, changed = reduced, True
                        break
                if changed:
                    break
            if not changed:
                break
        V.require(len(channels) <= 7, 'termination bound')
        trace = {'channels': [{'bit': b, 'source': s, 'tau': str(t)} for b,s,t in channels],
                 'terminal_target': [str(x) for x in r]}
        if components is None:
            support = tuple(x for x in range(8) if r[x])
            representative = V.orbit(support)
            perm, flip = next((perm, flip) for perm in permutations(range(3)) for flip in range(8)
                              if V.transform(support, perm, flip) == representative)
            mapping = [sum(((x >> old) & 1) << new for new,old in enumerate(perm)) ^ flip for x in range(8)]
            target = [F(0)]*8
            for x,y in enumerate(mapping):
                target[y] = r[x]
            if representative in ((0,3,5,6), (0,1,2,4,7)):
                members = representative if len(representative) == 4 else (1,2,4,7)
                order = tuple(sorted(members, key=lambda x: (-target[x],x)))
                root = list(permutations(members)).index(order)
                lam = [k*(target[order[k-1]]-(target[order[k]] if k < 4 else 0)) for k in range(1,5)]
                if len(representative) == 5:
                    lam.insert(0, target[0])
            else:
                root, lam = 0, [target[x] for x in representative]
            vertices = list(V.root_simplices(representative)[root])
            address = f'{root}:'
            nodes = self.covers[representative]
            while nodes[address][0] == 'splits':
                i,j = nodes[address][1]['edge']
                midpoint = V.average([vertices[i], vertices[j]])
                if lam[i] <= lam[j]:
                    lam[j] -= lam[i]
                    lam[i] *= 2
                    vertices[i] = midpoint
                    address += '0'
                else:
                    lam[i] -= lam[j]
                    lam[j] *= 2
                    vertices[j] = midpoint
                    address += '1'
            V.require(all(t >= 0 for t in lam) and sum(lam) == 1, 'leaf barycentric coordinates')
            V.require(all(sum(lam[i]*vertices[i][x] for i in range(len(lam))) == target[x] for x in range(8)), 'exact target-to-leaf reconstruction')
            w = nodes[address][1]['witness']
            if w['kind'] == 'star':
                alpha, t = V.Quad(F(1,2), F(-1,6)), V.Quad(F(3,2), F(-1,2))
                atom = w['atom']
                components = [(alpha, tuple(V.Quad((atom >> i) & 1) for i in range(3))),
                              (1-alpha, tuple(1-t if (atom >> i) & 1 else t for i in range(3)))]
            else:
                pars = [V.Quad(F(n,w['denominator'])) for n in w['numerators']]
                components = [(pars[0], tuple(reversed(pars[1:4]))), (1-pars[0], tuple(reversed(pars[4:7])))]
            original = []
            for weight, pars in components:
                params = [None]*3
                for new,old in enumerate(perm):
                    params[old] = 1-pars[new] if (flip >> new) & 1 else pars[new]
                original.append((weight, tuple(params)))
            components = original
            trace.update(representative=list(representative), permutation=list(perm), flip=flip,
                         leaf=address, barycentric=[str(x) for x in lam], witness=w)
        else:
            trace['terminal_case'] = 'deterministic-coordinate, exact representation'
        for bit,source,tau in reversed(channels):
            transformed = []
            for weight,pars in components:
                params = list(pars)
                i = bit.bit_length()-1
                params[i] = params[i]*F(1,1+tau) if source else (tau+params[i])*F(1,1+tau)
                transformed.append((weight, tuple(params)))
            components = transformed
        distribution(components)
        return components, trace

    def approximate(self, values):
        """Condition on high bits; at most 2^(n-2) product components for n>=3."""
        p = probability(values)
        n = len(p).bit_length()-1
        components, traces = [], []
        for context in range(1 << (n-3)):
            block = p[8*context:8*(context+1)]
            mass = sum(block)
            if not mass:
                continue
            local, trace = self.three_bits([x/mass for x in block])
            for weight,pars in local:
                components.append((mass*weight, pars+tuple(V.Quad((context >> i) & 1) for i in range(n-3))))
            traces.append({'context': context, 'mass': str(mass), 'local': trace})
        V.require(len(components) <= 1 << (n-2), 'component budget')
        distribution(components)
        return components, traces


def encode_quad(q):
    return {'rational': str(q.a), 'sqrt3_coefficient': str(q.b)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('probabilities', nargs='+', help='exact fractions summing to one; binary-index order')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    components, trace = Oracle().approximate(args.probabilities)
    result = {'status': 'CERTIFIED_FEASIBLE_WITNESS_NOT_OPTIMAL_PROJECTION',
              'bound_nats': '-3/4 log(2 sqrt(3)-3)', 'parameter_order': 'least-significant-bit first',
              'components': [{'weight': encode_quad(w), 'bernoulli_parameters': [encode_quad(t) for t in ps]} for w,ps in components],
              'trace': trace}
    output = json.dumps(result, indent=2)+'\n'
    if args.out:
        args.out.write_text(output)
    print(output, end='')


if __name__ == '__main__':
    main()
