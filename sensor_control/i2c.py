from subprocess import check_output


class I2c:
    def __init__(self, i2c_bus):
        self.i2c_bus = i2c_bus

    def transfer(self, cmd):
        output = check_output("i2c_transfer -y " + self.i2c_bus + " " + cmd, shell=True).decode("utf-8")

        if "error" in output:
            raise IOError("i2c_transfer errored: \n" + output)
        else:
            if output == '':
                return 0
            value = 0
            for (i, x) in enumerate(reversed(list(map(lambda x: int(x, 16), output.strip().split(' '))))):
                value += x * 256 ** i

            return value
