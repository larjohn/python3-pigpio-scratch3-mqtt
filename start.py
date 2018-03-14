import time
import pigpio as pigpio
import paho.mqtt.client as mqtt
import json
from devices.LED import LED
from devices.MotorDriverTB6612FNG import MotorDriverTB6612FNG, MotorSelection, FNGMotor
from devices.TiltSwitch import TiltSwitch


RASPBERRY_PI_ADDRESS = "192.168.0.151"

pi = pigpio.pi(RASPBERRY_PI_ADDRESS)       # pi1 accesses the local Pi's GPIO


sensors = {}
actuators = {}

mqttc: mqtt.Client = mqtt.Client(transport='websockets')

def on_message(client, userdata, message):
    #print("message received ", str(message.payload.decode("utf-8")))
    #print("message topic=", message.topic)
    #print("message qos=", message.qos)
    #print("message retain flag=", message.retain)

    msg = json.loads(str(message.payload.decode("utf-8")))

    if msg["command"] == "LED":
        pin = int(msg["args"]["PIN"])
        power = int(msg["args"]["POWER"])
        led = LED(pi, {'ANODE': pin})
        led.power(power)
    if msg["command"] == "MOTOR":
        name = msg["args"]["MOTOR_NAME"]
        power = int(msg["args"]["POWER"])
        motor: FNGMotor = actuators[name]

        if power > 0:
            motor.forward(power)
        else:
            motor.reverse(abs(power))

    elif msg["command"] == "INIT":
        pinPWMA = int(msg["args"]["PWMA"])
        pinPWMB = int(msg["args"]["PWMB"])
        pinAIN1 = int(msg["args"]["AIN1"])
        pinAIN2 = int(msg["args"]["AIN2"])
        pinBIN1 = int(msg["args"]["BIN1"])
        pinBIN2 = int(msg["args"]["BIN2"])
        pinSTBY = int(msg["args"]["STBY"])
        pin_map = {
            'PWMA': pinPWMA,
            'PWMB': pinPWMB,
            'AIN1': pinAIN1,
            'AIN2': pinAIN2,
            'BIN1': pinBIN1,
            'BIN2': pinBIN2,
            'STBY': pinSTBY,
        }
        driver = MotorDriverTB6612FNG(pi, pin_map)
        actuators[msg["args"]["MOTORA_NAME"]] = driver.get_motor(MotorSelection.MotorA)
        actuators[msg["args"]["MOTORB_NAME"]] = driver.get_motor(MotorSelection.MotorB)

    elif msg["command"] == "SUBSCRIBE":
        device = msg["args"]["DEVICE"]
        if device == "TILT_SWITCH":
            sensors[msg["args"]["ALIAS"]] = TiltSwitch(pi, mqttc, int(msg["args"]["PIN"]))


mqttc.on_message = on_message
# Uncomment to enable debug messages
mqttc.connect(RASPBERRY_PI_ADDRESS, 9001, 60)
mqttc.subscribe("rpi/devices/actuators/#", 1)
mqttc.subscribe("rpi/subscription", 1)
mqttc.subscribe("rpi/initialization", 1)

mqttc.loop_forever()


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("exiting")

# FREQ = 5000 # The PWM cycles per second.
#
# PWM1 = 17
# PWM2 = 23
# PWM3 = 24
# PWM4 = 25
#
# GPIO = [PWM1, PWM2, PWM3, PWM4]
#
# _channels = len(GPIO)
#
# _dc = [0]*_channels
#
# _micros: float = 1000000/FREQ
#
# old_wid = None
#
#
# def set_dc(channel, dc):
#
#     global old_wid
#
#     if dc < 0:
#       dc = 0
#     elif dc > _micros:
#       dc = _micros
#
#     _dc[channel] = dc
#
#     for c in range(_channels):
#       d: int = _dc[c]
#       g = GPIO[c]
#       if d == 0:
#          pi.wave_add_generic([pigpio.pulse(0, 1<<g, int(_micros))])
#       elif d == _micros:
#          pi.wave_add_generic([pigpio.pulse(1<<g, 0, int(_micros))])
#       else:
#          pi.wave_add_generic(
#             [pigpio.pulse(1 << g, 0, int(d)), pigpio.pulse(0, 1 << g, int(int(_micros)-d))])
#
#     new_wid = pi.wave_create()
#
#     if old_wid is not None:
#
#       pi.wave_send_using_mode(new_wid, pigpio.WAVE_MODE_REPEAT_SYNC)
#
#       # Spin until the new wave has started.
#       while pi.wave_tx_at() != new_wid:
#          pass
#
#       # It is then safe to delete the old wave.
#       pi.wave_delete(old_wid)
#
#     else:
#
#       pi.wave_send_repeat(new_wid)
#
#     old_wid = new_wid
#
# if not pi.connected:
#    exit(0)
#
# # Need to explicity set wave GPIO to output mode.
#
# for g in GPIO:
#    pi.set_mode(g, pigpio.OUTPUT)
#
# for i in range(int(_micros)):
#
#    set_dc(0, i)
#    set_dc(1, i+(int(_micros)/4))
#    set_dc(2, (int(_micros)/4)-i)
#    set_dc(3, int(_micros)-i)
#
#    time.sleep(0.5)
#
# pi.wave_tx_stop()
#
# if old_wid is not None:
#    pi.wave_delete(old_wid)

