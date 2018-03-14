import pigpio as pigpio
from enum import Enum


class MotorDirection(Enum):
    Forward = 1
    Reverse = -1


class MotorSelection(Enum):
    MotorA = 1
    MotorB = -1
    BipolarStepperMotor = 0


class TurnDirection(Enum):
    Left = 1
    Right = 2


class TurnAngle(Enum):
    Closed = 10
    Medium = 5
    Open = 2


class MotorDriverTB6612FNG:
    pinMap = []

    pinPWMA = None
    pinPWMB = None
    pinAIN1 = None
    pinAIN2 = None
    pinBIN1 = None
    pinBIN2 = None
    pinSTBY = None

    pi: pigpio.pi = None

    def __init__(self, pi, pin_map):
        self.pinMap = pin_map
        self.pi = pi
        self.pinPWMA = pin_map["PWMA"]
        self.pinPWMB = pin_map["PWMB"]
        self.pinAIN1 = pin_map["AIN1"]
        self.pinAIN2 = pin_map["AIN2"]
        self.pinBIN1 = pin_map["BIN1"]
        self.pinBIN2 = pin_map["BIN2"]
        self.pinSTBY = pin_map["STBY"]

    def move(self, motor_selection: MotorSelection, direction: MotorDirection, speed: float):
        self.release()
        if motor_selection == MotorSelection.MotorA:
            if direction == MotorDirection.Forward:
                self.on(self.pinAIN1)
                self.off(self.pinAIN2)
            else:
                self.off(self.pinAIN1)
                self.on(self.pinAIN2)

            self.pulse(self.pinPWMA, speed)

        if motor_selection == MotorSelection.MotorB:
            if direction == MotorDirection.Forward:
                self.on(self.pinBIN1)
                self.off(self.pinBIN2)
            else:
                self.off(self.pinBIN1)
                self.on(self.pinBIN2)

            self.pulse(self.pinPWMB, speed)

    def turn(self, turn_direction: TurnDirection, turn_angle: TurnAngle, motor_direction: MotorDirection, speed: float):
        if turn_direction == TurnDirection.Left:
            self.move(MotorSelection.MotorA, motor_direction, speed/turn_angle.value)
            self.move(MotorSelection.MotorB, motor_direction, speed)
        if turn_direction == TurnDirection.Right:
            self.move(MotorSelection.MotorB, motor_direction, speed/turn_angle.value)
            self.move(MotorSelection.MotorA, motor_direction, speed)

    def forward(self, speed):
        self.move(MotorSelection.MotorA, MotorDirection.Forward, speed)
        self.move(MotorSelection.MotorB, MotorDirection.Forward, speed)

    def reverse(self, speed):
        self.move(MotorSelection.MotorA, MotorDirection.Reverse, speed)
        self.move(MotorSelection.MotorB, MotorDirection.Reverse, speed)

    def brake(self):
        self.pi.write(self.pinSTBY, 0)

    def release(self):
        self.pi.write(self.pinSTBY, 0)

    def on(self, pin):
        self.pi.write(pin, 1)

    def off(self, pin):
        self.pi.write(pin, 0)

    def pulse(self, pin, level):
        self.pi.set_PWM_dutycycle(pin, level * 255/100)

    def get_motor(self, motor_selection: MotorSelection):
        return FNGMotor(self, motor_selection)


class FNGMotor:

    driver: MotorDriverTB6612FNG
    motor_selection: MotorSelection

    def __init__(self, driver: MotorDriverTB6612FNG, motor_selection: MotorSelection):
        self.driver = driver
        self.motor_selection = motor_selection

    def forward(self, speed):
        self.driver.move(self.motor_selection, MotorDirection.Forward, speed)

    def reverse(self, speed):
        self.driver.move(self.motor_selection, MotorDirection.Reverse, speed)
