from math import gcd


def analog_gain_to_reg(desired):
    analog_gain_settings = [
        [1, 0, 0],
        [1.03, 0, 1],
        [1.07, 0, 2],
        [1.1, 0, 3],
        [1.14, 0, 4],
        [1.19, 0, 5],
        [1.23, 0, 6],
        [1.28, 0, 7],
        [1.33, 0, 8],
        [1.39, 0, 9],
        [1.45, 0, 10],
        [1.52, 0, 11],
        [1.6, 0, 12],
        [1.68, 0, 13],
        [1.78, 0, 14],
        [1.88, 0, 15],
        [2, 1, 0],
        [2.13, 1, 2],
        [2.29, 1, 4],
        [2.46, 1, 6],
        [2.67, 1, 8],
        [2.91, 1, 10],
        [3.2, 1, 12],
        [3.56, 1, 14],
        [4, 2, 0],
        [4.57, 2, 4],
        [5.33, 2, 8],
        [6.4, 2, 12],
        [8, 3, 0]
    ]

    for (gain, coarse, fine) in analog_gain_settings:
        if gain > desired:
            return int(format(coarse, '02b') + format(fine, '04b'))


def digital_gain_to_reg(desired):
    base = int(desired)
    fraction = int((desired % 1.0) * 128)
    return int(format(base, '04b') + format(fraction, '07b'), base=2)


def optimal_pll_config(extclk, vco_target):
    vco_maximum = 768000000
    assert (vco_target < vco_maximum)
    vco_max = vco_target
    vco_min = 384000000

    div_min = 1
    div_max = 64

    mul_min = 32
    mul_max = 384

    for vco in range(vco_max, vco_min - 1, -1):
        i = gcd(extclk, vco)
        div = extclk / i
        mul = vco / i

        if mul_max >= mul >= mul_min and div <= div_max:
            break

    return {"pre_pll_clk_div": int(div), "pll_multiplier": int(mul)}
