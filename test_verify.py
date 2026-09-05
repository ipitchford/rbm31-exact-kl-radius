"""Adversarial and cross-implementation checks; standard library only."""
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction as F
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import verify as V


class VerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.small = json.loads((Path(__file__).parent/"certificates"/"two.json").read_text())

    def test_logarithms_against_decimal(self):
        # Decimal's independent correctly-rounded ln is a diagnostic oracle.
        with localcontext() as ctx:
            ctx.prec = 110
            values = [F(1),F(2),F(1,2),F(1,3),F(7,3),F(10**80+1,3),
                      F(1,10**80),F(2**120-1,2**120),F(2**120+1,2**120)]
            values += [F(a,b) for a in range(1,30) for b in (3,7,19,31)]
            for x in values:
                lo,hi = V.log_interval(x)
                expected = (Decimal(x.numerator)/Decimal(x.denominator)).ln()
                self.assertLessEqual(Decimal(lo)/Decimal(V.SCALE),expected)
                self.assertGreaterEqual(Decimal(hi)/Decimal(V.SCALE),expected)
        self.assertEqual(V.log_interval(F(1)),(0,0))

    def test_quadratic_signs(self):
        with localcontext() as ctx:
            ctx.prec = 100
            root = Decimal(3).sqrt()
            for a in range(-10,11):
                for b in range(-10,11):
                    d = Decimal(a)+Decimal(b)*root
                    self.assertEqual(V.Quad(a,b).sign(),(d>0)-(d<0))
        self.assertEqual(V.lower_certificate()["status"],"PASS")

    def test_bad_lower_certificate_rejected(self):
        broken = list(V.STAR)
        broken[0] += F(1,1000)
        with patch.object(V,"STAR",tuple(broken)):
            with self.assertRaises(ValueError):
                V.lower_certificate()

    def test_all_supports_and_channel_reconstruction(self):
        self.assertEqual(V.support_certificate()["irreducible_supports"],50)
        count = 0
        for mask in range(1,256):
            for seed in (1,2,3):
                p = [F(((x+1)*seed)%11+1) if (mask>>x)&1 else F(0) for x in range(8)]
                p = [x/sum(p) for x in p]
                steps = 0
                while True:
                    if any(not any(p[x] for x in range(8) if x&bit) or
                           not any(p[x] for x in range(8) if not(x&bit)) for bit in (1,2,4)):
                        break
                    found = False
                    for bit in (1,2,4):
                        base = [x for x in range(8) if not(x&bit)]
                        for direction in (0,bit):
                            a = [x^direction for x in base]
                            b = [x^bit for x in a]
                            if all(not p[i] or p[j]>0 for i,j in zip(a,b)):
                                t = min(p[j]/p[i] for i,j in zip(a,b) if p[i])
                                q = p.copy()
                                for i,j in zip(a,b):
                                    q[i]=(1+t)*p[i]
                                    q[j]=p[j]-t*p[i]
                                    self.assertEqual(q[i]/(1+t),p[i])
                                    self.assertEqual(q[j]+t*q[i]/(1+t),p[j])
                                self.assertEqual(sum(q),1)
                                self.assertTrue(all(x>=0 for x in q))
                                self.assertLess(sum(x>0 for x in q),sum(x>0 for x in p))
                                self.assertTrue(all(not q[i] or p[i] for i in range(8)))
                                p=q
                                steps += 1
                                found=True
                                break
                        if found:
                            break
                    if not found:
                        self.assertIn(V.orbit([i for i in range(8) if p[i]]),V.SUPPORTS)
                        break
                self.assertLessEqual(steps,7)
                count += 1
        self.assertEqual(count,765)

    def test_positive_small_cover(self):
        self.assertEqual(V.verify_cover(deepcopy(self.small))["status"],"PASS")

    def test_missing_branch_rejected(self):
        d=deepcopy(self.small)
        d["leaves"].pop()
        with self.assertRaises(ValueError):
            V.verify_cover(d)

    def test_duplicate_and_orphan_rejected(self):
        d=deepcopy(self.small)
        d["leaves"].append(deepcopy(d["leaves"][0]))
        with self.assertRaises(ValueError):
            V.verify_cover(d)
        d=deepcopy(self.small)
        orphan=deepcopy(d["leaves"][0])
        orphan["path"]="999:"
        d["leaves"].append(orphan)
        with self.assertRaises(ValueError):
            V.verify_cover(d)

    def test_bad_split_rejected(self):
        d=deepcopy(self.small)
        d["splits"][0]["edge"]=[0,0]
        with self.assertRaises(ValueError):
            V.verify_cover(d)

    def test_invalid_mixture_rejected(self):
        with self.assertRaises(ValueError):
            V.witness_logs({"kind":"mixture","denominator":10,"numerators":[11,0,0,0,1,1,1]})
        with self.assertRaises(ValueError):
            V.witness_logs({"kind":"trusted_q","probabilities":[F(1,8)]*8})

    def test_bad_support_witness_rejected(self):
        d=deepcopy(self.small)
        for leaf in d["leaves"]:
            leaf["witness"]={"kind":"mixture","denominator":1,"numerators":[1,0,0,0,0,0,0]}
        with self.assertRaises(ValueError):
            V.verify_cover(d)

    def test_false_equality_not_accepted(self):
        p=tuple(F(1,4) if x in (0,1,6,7) else F(0) for x in range(8))
        w={"kind":"star","atom":0}
        self.assertFalse(V.exact_parity_equality(p,w))
        with self.assertRaises(ValueError):
            V.vertex_slack(p,w,V.witness_logs(w))
        parity=tuple(F(1,4) if x.bit_count()%2==0 else F(0) for x in range(8))
        wrong={"kind":"star","atom":1}
        with self.assertRaises(ValueError):
            V.vertex_slack(parity,wrong,V.witness_logs(wrong))

    def test_search_scores_are_not_trusted(self):
        d=deepcopy(self.small)
        d["complete"]=False
        d["pending"]=1000000
        for leaf in d["leaves"]:
            leaf["score"]=-999999999999
        self.assertEqual(V.verify_cover(d)["status"],"PASS")

    def test_nonpositive_logs_rejected(self):
        for x in (F(0),F(-1)):
            with self.assertRaises(ValueError):
                V.log_interval(x)


if __name__=="__main__":
    unittest.main(verbosity=2)
