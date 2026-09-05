"""Semantic tests of the constructive extension; not unaffiliated assurance."""
from decimal import Decimal, localcontext
from fractions import Fraction as F
import random
import unittest
import verify as V
import witness as W


def decimal_divergence(p, components):
    with localcontext() as ctx:
        ctx.prec = 80
        root = Decimal(3).sqrt()
        def decimal(f):
            return Decimal(f.numerator)/Decimal(f.denominator)
        q = [decimal(z.a)+decimal(z.b)*root for z in W.distribution(components)]
        d = sum(decimal(px)*(decimal(px)/qx).ln() for px,qx in zip(p,q) if px)
        c = -Decimal(3)/4*(2*root-3).ln()
        return d,c


class WitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle = W.Oracle()

    def check_target(self, p):
        components, trace = self.oracle.approximate(p)
        d,c = decimal_divergence(p,components)
        with localcontext() as ctx:
            ctx.prec = 80
            self.assertLessEqual(d,c+Decimal('1e-70'))  # Diagnostic only, not a proof decision.
        self.assertLessEqual(len(components),len(p)//4)
        return components,trace

    def test_all_supports_three_rational_weights_each(self):
        for mask in range(1,256):
            for seed in (1,2,3):
                weights = [F(((x+1)*seed)%11+1) if (mask >> x)&1 else F(0) for x in range(8)]
                self.check_target([x/sum(weights) for x in weights])

    def test_parity_and_worked_channel(self):
        for parity in (0,1):
            p = [F(1,4) if x.bit_count()%2 == parity else F(0) for x in range(8)]
            components,_ = self.check_target(p)
            d,c = decimal_divergence(p,components)
            self.assertLess(abs(d-c),Decimal('1e-70'))
        p = [F(x,16) for x in (3,1,0,4,0,4,3,1)]
        components,trace = self.check_target(p)
        self.assertEqual(trace[0]['local']['channels'],[{'bit':1,'source':0,'tau':'1/3'}])
        d,c = decimal_divergence(p,components)
        self.assertLess(d,c)

    def test_conditioning_lift_four_and_five_bits(self):
        generator = random.Random(20260905)
        for n in (4,5):
            for _ in range(24):
                weights = [F(generator.randrange(20)) for _ in range(1 << n)]
                self.check_target([x/sum(weights) for x in weights])
            p = [F(1,4) if x in (0,3,5,6) else F(0) for x in range(1 << n)]
            components, trace = self.check_target(p)
            self.assertEqual(len(trace),1)
            self.assertEqual(len(components),2)

    def test_invalid_targets_rejected(self):
        for values in ([F(1,7)]*7,[F(1,9)]*8,[-1,2,0,0,0,0,0,0]):
            with self.assertRaises(ValueError):
                self.oracle.approximate(values)

    def test_invalid_mixture_rejected(self):
        with self.assertRaises(ValueError):
            W.distribution([(V.Quad(1),(V.Quad(2),V.Quad(0),V.Quad(0)))])
        with self.assertRaises(ValueError):
            W.distribution([(V.Quad(F(1,2)),(V.Quad(0),)*3)])


if __name__ == '__main__':
    unittest.main(verbosity=2)
