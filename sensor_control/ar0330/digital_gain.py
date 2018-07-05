#!/bin/python3

from sys import argv
from pll import optimal_pll_config
from yaml import load
from subprocess import check_output

extclk = 24000000
i2c_bus = "1"
address = 0x10
ar0330_gpio_addr = 0x41200000

ar0330 = load(open("registers.yml"))

def write(register_name, value, cam = ar0330):
    register = cam[register_name]
    addr = register["address"]
    count = register["width"]
    addr_high = addr >> 8
    addr_low = addr & 0xff
    write_value = []

    for v in range(1, count + 1):
        write_value.append("0x%x" % (value & 0xff))
        value >>= 8

    values = " ".join(reversed(write_value))
    transfer_cmd = "w%d@%d %d %d %s" % (2 + count, address, addr_high, addr_low, values)
    return(i2ctransfer(transfer_cmd))

def i2ctransfer(cmd):
    output = check_output("i2ctransfer -y " + i2c_bus + " " + cmd, shell=True).decode("utf-8")

    if "error" in output:
        print("i2ctransfer errored: ", output)
        exit(-1)
    else:
        if output == '':
            return 0
        value = 0
        for (i, x) in enumerate(reversed(list(map(lambda x: int(x, 16), output.strip().split(' '))))):
            value += x * 256**i

        return value

def get_close(desired):
    for (gain, coarse, fine) in gain_settings:
        if gain > desired:
            return (gain, coarse, fine)

if __name__ == "__main__":
    desired_gain = float(argv[1])
    base = int(desired_gain)
    fraction = int((desired_gain % 1.0) * 128)
    write("global_gain",  int(format(base, '04b') + format(fraction, '07b'), base=2))
    print(desired_gain)

