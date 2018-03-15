import pigpio as pigpio


class DataAcquisitionPCF8591:

    pi: pigpio.pi = None
    address = 0x48
    handle = None

    def ___init___(self, pi):
        self.pi = pi
        self.handle = pi.i2c_open(1, self.address, 0)

    def read(self, chn):  # channel
        try:
            if chn == 0:
                self.pi.i2c_write_byte(self.handle, 0x40)
            if chn == 1:
                self.pi.i2c_write_byte(self.handle, 0x41)
            if chn == 2:
                self.pi.i2c_write_byte(self.handle, 0x42)
            if chn == 3:
                self.pi.i2c_write_byte(self.handle, 0x43)
            self.pi.i2c_read_byte(self.handle)  # dummy read to start conversion
        except Exception as e:
            print("Address: %s" % self.handle)
            print(e)
        return self.pi.i2c_read_byte(self.handle)

    def write(self, val):
        try:
            temp = val # move string value to temp
            temp = int(temp) # change string to integer
            # print temp to see on terminal else comment out
            self.pi.i2c_write_byte(self.handle, temp)
        except Exception as e:
            print("Error: Device address: 0x%2X" % self.address)
            print(e)
