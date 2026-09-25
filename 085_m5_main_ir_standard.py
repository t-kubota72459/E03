# 第8回 最終検収用 標準 main.py
# 071_m5_main_ir_standard.py を基に、
# 推定ID・JUDGE・検査回数（KENSA COUNT）を表示する版
#
# IRセンサ : GPIO33（負論理）
# Relay    : GPIO32
# HUSKYLENS: I2C SDA=GPIO25 / SCL=GPIO26
#
# KENSA COUNT:
# IRセンサがワークを検出し、inspect_work() を実行した累積回数。
# 20個のワークを流したとき、きれいに1回ずつ検出できれば COUNT=20 になる。

from machine import Pin, I2C
import time

from display import Display
from huskylens import HuskyLens

IR_PIN = 33
RELAY_PIN = 32
HUSKY_SDA = 25
HUSKY_SCL = 26

# IRセンサ：アルミベースなし=1、検出=0
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


def show_ready(kensa_count):
    lcd.clear()

    lcd.text2x("READY", 10, 20)

    lcd.text("KENSA COUNT :", 10, 70)
    lcd.text2x(str(kensa_count), 10, 85)

    lcd.show()


def show_result(suitei_id, judge, kensa_count):
    # 未認識時は推定IDを --- と表示する
    if suitei_id is None:
        id_text = "---"
    else:
        id_text = str(suitei_id)

    # 今回の結果だけを見やすく表示する
    lcd.clear()

    lcd.text("SUITEI ID :", 10, 20)
    lcd.text2x(id_text, 10, 35)

    lcd.text("JUDGE :", 10, 75)
    lcd.text2x(judge, 10, 90)

    lcd.text("KENSA COUNT :", 10, 135)
    lcd.text2x(str(kensa_count), 10, 150)

    lcd.show()


def inspect_work(kensa_count):
    suitei_id = husky.get_id()

    if suitei_id in (1, 2):
        judge = "OK"
        relay.value(0)

    elif suitei_id in (3, 4):
        judge = "NG"
        relay.value(1)

    else:
        # 未認識・不明IDはOKにしない
        judge = "RETRY"
        relay.value(1)

    print(
        "SUITEI ID =", suitei_id,
        "JUDGE =", judge,
        "KENSA COUNT =", kensa_count
    )

    show_result(suitei_id, judge, kensa_count)


kensa_count = 0

print("S8 FINAL STANDARD")
show_ready(kensa_count)

try:
    while True:
        # IRセンサは負論理：ワーク検出=0
        if ir_sensor.value() == 0:

            # IRセンサが新しくワークを検出した回数を数える
            kensa_count += 1

            inspect_work(kensa_count)

            # 同じ検出状態のまま再判定しないよう、
            # アルミベースがセンサ前を通過するまで待つ
            while ir_sensor.value() == 0:
                time.sleep_ms(10)

        time.sleep_ms(10)

finally:
    relay.value(0)
