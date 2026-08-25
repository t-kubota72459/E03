# 第5回 M5StickC PLUS2 外観検査 main.py テンプレート
#
# 目的:
#   HUSKYLENS が返した Class ID を M5StickC PLUS2 で判定し、
#   LCD と Relay Unit に出力する。
#
# 今回の対応:
#   ID1 / ID2 -> OK    -> Relay OFF
#   ID3 / ID4 -> NG    -> Relay ON
#   その他    -> RETRY -> Relay ON
#
# TODO の部分を完成させること。

from machine import Pin, I2C
import time

from display import Display
from huskylens import HuskyLens


# --------------------------------------------------
# 使用する GPIO
# --------------------------------------------------
BUTTON_PIN = 37
RELAY_PIN = 32
HUSKY_SDA = 25
HUSKY_SCL = 26


# --------------------------------------------------
# 入出力の準備
# --------------------------------------------------
button = Pin(BUTTON_PIN, Pin.IN)
relay = Pin(RELAY_PIN, Pin.OUT)

# 今回の方針：
# 検査結果がまだ分からない起動直後は安全側の ON にする。
relay.value(1)

lcd = Display()

i2c = I2C(
    0,
    sda=Pin(HUSKY_SDA),
    scl=Pin(HUSKY_SCL),
    freq=100000
)

husky = HuskyLens(i2c)


# --------------------------------------------------
# LCD にメッセージを表示する関数
# --------------------------------------------------
def show_message(message):
    lcd.clear()
    lcd.text2x(message, 10, 20)
    lcd.show()


# --------------------------------------------------
# ワークを1回検査する関数
# --------------------------------------------------
def inspect_work():
    # HUSKYLENS から Class ID を取得する
    object_id = husky.get_id()
    print("ID =", object_id)

    # ID1 / ID2 は OK
    if object_id in (1, 2):
        # TODO 1:
        # LCD に "OK" と表示する
        # Relay を OFF にする
        pass

    # ID3 / ID4 は NG
    elif object_id in (3, 4):
        # TODO 2:
        # LCD に "NG" と表示する
        # Relay を ON にする
        pass

    # その他 / 未認識は RETRY
    else:
        # TODO 3:
        # LCD に "RETRY" と表示する
        # 安全側として Relay を ON にする
        pass


# --------------------------------------------------
# メイン処理
# --------------------------------------------------
show_message("READY")

try:
    while True:
        # Button A は Active Low
        # 押すと 0 になる
        if button.value() == 0:
            inspect_work()

            # ボタンを離すまで待つ。
            # 1回押しただけで何度も検査されることを防ぐ。
            while button.value() == 0:
                time.sleep_ms(10)

        time.sleep_ms(10)

finally:
    # プログラム終了時も、結果不明として安全側へ倒す。
    relay.value(1)
