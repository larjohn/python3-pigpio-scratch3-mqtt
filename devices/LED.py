import pigpio as pigpio

# TODO: lookup table for brightness - not linear


class LED:
    pinMap = []
    pi: pigpio.pi = None

    def __init__(self, pi, pin_map):
        self.pinMap = pin_map
        self.pi = pi

    def on(self):
        self.pi.write(self.pinMap["ANODE"], 1)

    def off(self):
        self.pi.write(self.pinMap["ANODE"], 0)

    def power(self, level):
        self.pi.set_PWM_dutycycle(self.pinMap["ANODE"], level * 255/100)

