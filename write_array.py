#!/bin/env python3
from subprocess import check_output
from time import sleep
from sys import argv

i2c_bus = "0"
address = 0x18
ar0330_gpio_addr = 0x41200000

def gpio(addr, value=0xdeadbeef):
    cmd = "devmem2 0x%x w" % addr 
    if value != 0xdeadbeef:
        cmd += " 0x%x" % value

    check_output(cmd, shell=True)

ar0330_gpio = lambda value = 0xdeadbeef: gpio(ar0330_gpio_addr, value)

def i2ctransfer(cmd):
    output = check_output("i2ctransfer -y " + i2c_bus + " " + cmd, shell=True).decode("utf-8")

    if "error" in output:
        print("i2ctransfer errored: ", output)
        exit(-1)
    else:
        value = 0
        for (i, x) in enumerate(reversed(list(map(lambda x: int(x, 16), output.strip().split(' '))))):
            value += x * 256**i
            
        return value


def read(addr, count=2):
    addr_high = addr >> 8
    addr_low = addr & 0xff
    transfer_cmd = "w2@%d %d %d r%d" % (address, addr_high, addr_low, count)
    return i2ctransfer(transfer_cmd)

def write(addr, value, count=2):
    addr_high = addr >> 8
    addr_low = addr & 0xff
    write_value = []

    for v in range(1, count):
        write_value.append("0x%x" % (value & 0xff))
        value >>= 8

    values = " ".join(reversed(write_value))
    transfer_cmd = "w%d@%d %d %d %s" % (2 + count, address, addr_high, addr_low, values)
    

# init 

# toggle reset (active low)
ar0330_gpio(0x7)
sleep(.5)
ar0330_gpio(0x0)
sleep(.5)
ar0330_gpio(0x7)
sleep(.5)
# magic init
## write(0x3152, 0xa114)
## write(0x304a, 0x0070)

sleep_magic = 0xffff
def write_array(vals):
    for addr, value in vals:
        if addr == sleep_magic:
            sleep(float(value) / 2**16)
        else:
            write(addr, value)


# for i in range(0, 2**15):
#    write(0x301a, 2*i)
#    print("write: 0x%x, read:0x%x" % (2* i, read(0x301a)))

vals = []
for line in open(argv[1], "r"):
    if '#' in line:
        code, comment = line.strip().split('#')
    else:
        code = line.strip()

    if ',' in code:
        a, b = code.strip().split(',')
        if "REG_DL" in a:
            vals.append([sleep_magic, int(b, 16)])
        else:
            vals.append([int(a, 16), int(b, 16)])


write_array(vals)


while 1:
    print("reset", "0x%x" % read(0x301a))
    print("frame_count", "0x%x" % read(0x303a))
    print("frame_status", "0x%x" % read(0x303c))
    sleep(.1)
