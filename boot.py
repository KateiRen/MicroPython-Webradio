# This file is executed on every boot (including wake-boot from deepsleep)
import gc
import webrepl
import config # SSID etc. importieren

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(config.WLANSSID, config.WLANPW)
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

do_connect()
webrepl.start()
gc.collect()