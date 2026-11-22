"""Modello asintotico di Lotka: dal TFR al tempo di dimezzamento."""

import math

SEX_RATIO_F = 0.488
SURVIVAL_TO_REPRODUCTION = 0.99


def net_reproduction_rate(tfr: float) -> float:
    return tfr * SEX_RATIO_F * SURVIVAL_TO_REPRODUCTION


def intrinsic_rate(tfr: float, generation_length: float = 32.7) -> float:
    return math.log(net_reproduction_rate(tfr)) / generation_length


def halving_time(tfr: float, generation_length: float = 32.7) -> float:
    return math.log(0.5) / intrinsic_rate(tfr, generation_length)


if __name__ == "__main__":
    for tfr in (1.30, 1.24, 1.18, 1.14, 0.85):
        t_half = halving_time(tfr)
        print(
            f"TFR={tfr:4.2f} | R0={net_reproduction_rate(tfr):.3f} | "
            f"r={intrinsic_rate(tfr) * 100:6.2f}%/y | t_half={t_half:5.1f} anni"
        )
