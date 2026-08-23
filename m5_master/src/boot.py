# This file is executed on every boot (including wake-boot from deepsleep)
from machine import Pin

# M5StickC PLUS2 power hold
hold = Pin(4, Pin.OUT)
hold.value(1)

#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()