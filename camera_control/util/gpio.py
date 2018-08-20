from subprocess import check_output


class GPIO:
    def __init__(self, address):
        self.addr = address

    def set(self, value=0xdeadbeef):
        cmd = "devmem2 0x%x w" % self.addr
        if value != 0xdeadbeef:
            cmd += " 0x%x" % value

        check_output(cmd, shell=True)
