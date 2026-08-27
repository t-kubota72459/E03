from machine import Pin, I2C
from time import sleep

from display import Display
from huskylens import HuskyLens

# Relay Unit
relay = Pin(32, Pin.OUT)

# LCD
lcd = Display()

# HUSKYLENS
sleep(1)
i2c = I2C(
    0,
    sda=Pin(25),
    scl=Pin(26),
    freq=100000
)
husky = HuskyLens(i2c)

while True:
    object_id = husky.get_id()

    # 課題1
    # HUSKYLENSが返したIDをprintしてみよう


    # 課題2
    # ID=1 のとき "OK"
    # ID=2,3,4 のとき "NG"
    # と表示するプログラムを書こう


    # 課題3
    # OKなら Relay OFF
    # NGなら Relay ON
    # にしよう


    # 課題4
    # LCDにも判定結果を表示しよう


    sleep(0.5)