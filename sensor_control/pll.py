from fractions import gcd
#from sys import argv

def optimal_pll_config(extclk, vco_target):
    vco_maximum = 768000000  # chip max
    assert(vco_target < vco_maximum)
    vco_max = vco_target
#    vco_max = 588000000
    vco_min = 384000000
    
    div_min = 1
    div_max = 64
    
    mul_min = 32
    mul_max = 384
    
    for vco in range(vco_max, vco_min - 1, -1):
        i = gcd(extclk, vco)
        div = extclk / i
        mul = vco / i
    
        if mul <= mul_max and mul >= mul_min and div <= div_max:
            break

    return({"pre_pll_clk_div" : int(div), "pll_multiplier" : int(mul)})
