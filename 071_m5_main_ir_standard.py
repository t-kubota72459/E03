# 第7回 1st turn 標準 main.py
# 052_m5_main_template.py の Button A トリガーを
# IRセンサ（GPIO33、負論理）へ置き換えた基本版

from machine import Pin, I2C
import time

from display import Display
from huskylens import HuskyLens

IR_PIN = 33
RELAY_PIN = 32
HUSKY_SDA = 25
HUSKY_SCL = 26

# IRセンサ：真鍮ベースなし=1、検出=0
ir_sensor = Pin(IR_PIN, Pin.IN)

# Relay：0=OFF、1=ON
relay = Pin(RELAY_PIN, Pin.OUT)
relay.value(0)

lcd = Display()

i2c = I2C(
    0,
    sda=Pin(HUSKY_SDA),
    scl=Pin(HUSKY_SCL),
    freq=100000
)

husky = HuskyLens(i2c)


def show_message(message):
    lcd.clear()
    lcd.text2x(message, 10, 20)
    lcd.show()


def inspect_work():
    object_id = husky.get_id()
    print("ID =", object_id)

    if object_id in (1, 2):
        show_message("OK")
        relay.value(0)

    elif object_id in (3, 4):
        show_message("NG")
        relay.value(1)

    else:
        # 未認識・不明IDはOKにしない
        show_message("RETRY")
        relay.value(1)


print("S7 IR STANDARD")
show_message("READY")

try:
    while True:
        # IRセンサは負論理：ワーク検出=0
        if ir_sensor.value() == 0:
            inspect_work()

            # 同じワークを再判定しないよう、
            # 真鍮ベースがセンサ前を通過するまで待つ
            while ir_sensor.value() == 0:
                time.sleep_ms(10)

        time.sleep_ms(10)

finally:
    relay.value(0)
