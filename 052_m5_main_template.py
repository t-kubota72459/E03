from machine import Pin, I2C
import time

from display import Display
from huskylens import HuskyLens


# ========================================
# ピン設定
# ========================================

HOLD_PIN = 4

BUTTON_PIN = 37
RELAY_PIN = 32

HUSKY_SDA = 25
HUSKY_SCL = 26


# ========================================
# 初期化
# ========================================

# M5StickC PLUS2 の電源保持
hold = Pin(HOLD_PIN, Pin.OUT)
hold.value(1)

# Button A
button = Pin(BUTTON_PIN, Pin.IN)

# Relay Unit
relay = Pin(RELAY_PIN, Pin.OUT)
relay.value(0)

# LCD
lcd = Display()

# HUSKYLENS
i2c = I2C(
    0,
    sda=Pin(HUSKY_SDA),
    scl=Pin(HUSKY_SCL),
    freq=100000
)

husky = HuskyLens(i2c)


# ========================================
# LCD表示
# ========================================

def show_message(message):
    lcd.clear()
    lcd.text2x(message, 10, 20)
    lcd.show()


# ========================================
# ワーク判定
# ========================================

def inspect_work():

    object_id = husky.get_id()

    print("ID =", object_id)

    # TODO:
    # ID1 / ID2 のときは OK
    # ID3 / ID4 のときは NG
    # それ以外は RETRY
    #
    # show_message("...")
    # relay.value(...)

    if object_id in (1, 2):
        # TODO: OK の表示とRelay制御
        pass

    elif object_id in (3, 4):
        # TODO: NG の表示とRelay制御
        pass

    else:
        # TODO: RETRY の表示
        # 判定できない場合は安全側としてRelay ON
        pass


# ========================================
# メイン処理
# ========================================

show_message("READY")

try:

    while True:

        # Button A は押すと 0
        if button.value() == 0:

            inspect_work()

            # 押しっぱなしで何度も判定しないよう、
            # ボタンを離すまで待つ
            while button.value() == 0:
                time.sleep_ms(10)

        time.sleep_ms(10)

finally:

    # Thonnyで停止したときはRelayをOFF
    relay.value(0)
