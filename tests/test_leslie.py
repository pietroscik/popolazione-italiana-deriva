import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import halving as lotka
import leslie
from halving import halving_time as lotka_halving_time
from leslie import (
    asymptotic_halving,
    build_leslie_matrix,
    dominant_eigen,
    halving_time as traj_halving_time,
    simulate,
)


class TestLotka(unittest.TestCase):
    def test_tfr_italia_2024(self):
        t_half = lotka_halving_time(1.18, generation_length=32.7)
        self.assertAlmostEqual(t_half, 40.3, delta=0.2)

    def test_monotonia_in_tfr(self):
        self.assertGreater(lotka_halving_time(1.30), lotka_halving_time(0.85))

    def test_r0(self):
        self.assertAlmostEqual(lotka.net_reproduction_rate(1.18), 0.570, delta=0.001)
        self.assertLess(lotka.intrinsic_rate(1.18), 0)


class TestLeslie(unittest.TestCase):
    def test_lambda_coerente(self):
        fert = np.zeros(101)
        fert[15:50] = 1.18 / 35
        surv = np.linspace(0.9998, 0.5, 101)
        L = build_leslie_matrix(fert, surv)
        lam, stable = dominant_eigen(L)
        self.assertAlmostEqual(float(stable.sum()), 1.0, places=10)
        self.assertLess(lam, 1.0)
        self.assertAlmostEqual(asymptotic_halving(lam),
                                np.log(0.5) / np.log(lam))

    def test_sopravvivenza_pura(self):
        fert = np.zeros(101)
        surv = np.full(101, 0.99)
        surv[-1] = 0.0
        n0 = np.full(101, 1000.0)
        traj = simulate(n0, fert, surv, years=2)
        self.assertLess(traj[1], traj[0])
        self.assertGreater(traj[1] / traj[0], 0.95)
        self.assertAlmostEqual(traj[2] / traj[1], traj[1] / traj[0], delta=1e-3)

    def test_interpolazione_dimezzamento(self):
        traj = np.array([100.0, 60.0, 45.0])
        self.assertAlmostEqual(traj_halving_time(traj), 1.0 + 10.0 / 15.0)
        self.assertTrue(np.isnan(traj_halving_time(np.array([100.0, 90.0]))))


if __name__ == "__main__":
    unittest.main()
