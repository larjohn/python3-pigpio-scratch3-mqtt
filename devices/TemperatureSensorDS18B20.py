import pigpio as pigpio

class TemperatureSensorDS18B20:

    device_id = ""
    file_name = ""
    pi: pigpio.pi = None

    def __init__(self, pi):

        pi.exceptions = False
        c, files = pi.file_list("/sys/bus/w1/devices/28-*/w1_slave")
        pi.exceptions = True
        files = files.decode("utf-8").splitlines()
        self.pi = pi
        if c >= 0:

            for sensor in files:

                """
                Typical file name

                /sys/bus/w1/devices/28-000005d34cd2/w1_slave
                """
                self.file_name = sensor
                self.device_id = sensor.split("/")[5]  # Fifth field is the device Id.

    def get_temperature(self):
        h = self.pi.file_open(self.file_name, pigpio.FILE_READ)
        c, data = self.pi.file_read(h, 1000)  # 1000 is plenty to read full file.
        self.pi.file_close(h)

        """
        Typical file contents

        73 01 4b 46 7f ff 0d 10 41 : crc=41 YES
        73 01 4b 46 7f ff 0d 10 41 t=23187
        """
        data = data.decode("utf-8")
        if "YES" in data:
            (discard, sep, reading) = data.partition(' t=')
            t = float(reading) / 1000.0
            return t
        else:
            print("999.9")
