import pigpio as pigpio
import paho.mqtt.client as mqtt


class TiltSwitch:

    mqttc: mqtt.Client = None
    gpio: int = None

    def on_tilt(self, gpio,  edge, tick):

        if edge == 1:
            self.mqttc.publish("rpi/devices/sensors/tilt/" + str(gpio), "true")
        else:
            self.mqttc.publish("rpi/devices/sensors/tilt/" + str(gpio), "false")

    def __init__(self, pi: pigpio.pi, mqttc: mqtt.Client, gpio):
        self.mqttc = mqttc
        self.gpio = gpio
        pi.callback(gpio, 1, self.on_tilt)
        pi.callback(gpio, 0, self.on_tilt)



