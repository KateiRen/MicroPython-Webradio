import vs10xx
from machine import SPI
import usocket as socket

webradios = [["Das Ding","swr-dasding-live.cast.addradio.de", "/swr/dasding/live/mp3/128/stream.mp3", 80],
             ["Bayern 3","br-br3-live.cast.addradio.de","/br/br3/live/mp3/128/stream.mp3",80],
             ["FM4","mp3stream1.apasf.apa.at","/listen.pls", 8000],
             ["egofm","egofm-live.cast.addradio.de","/egofm/live/mp3/high/stream.mp3",80],
             ["Kosmos","radiostreaming.ert.gr","/ert-kosmos",80],
             ["egofm","egofm-ais-edge-400b-dus-dtag-cdn.cast.addradio.de","/egofm/live/mp3/high/stream.mp3?_art=dj0yJmlwPTkxLjQ5LjM2LjE1NiZpZD1pY3NjeGwtd2pub25jbm1iJnQ9MTYyNDA5ODA3MSZzPTc4NjZmMjljI2E5NDQ2ODczZWExYjY5ZDY1ZTlhOTEyNjFiYTBjZWEw",80]]


station = 2

spi = SPI(1, vs10xx.SPI_BAUDRATE) # SPI bus id=1 pinout: SCK = 14, MOSI = 13, MISO = 12

player = vs10xx.Player(
    spi,
    xResetPin = 21,
    dReqPin = 22,
    xDCSPin = 23,
    xCSPin = 25,
    CSPin = None
)

print("Player set up")
player.setVolume(0.8) # the range is 0 to 1.0

s = ""
buf = ""

def connectAndTry():
    print("Station Name: " +webradios[station][0])
    print("Station Host: " + webradios[station][1])
    print("Station Path: " + webradios[station][2])
    print("Station Port: " + str(webradios[station][3]))

    global s, buf
    s = socket.socket()
    addr = socket.getaddrinfo(webradios[station][1], webradios[station][3])[0][-1]
    print(addr)
    s.connect(addr)
    s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (webradios[station][2], webradios[station][1]), 'utf8'))

    buf = s.recv(1000)
    print(buf)
    print(buf[9:15])
    if buf[9:15] == b'200 OK':
        print("OK start streaming")
        # optionally skip ahead until mp3 stream is reached
        return "OK"
    elif buf[9:18] == b'302 Found':
        s.close()
        print("Need to extract redirect address first")
        start = str(buf).find("Location: ") + 10 # "Location: " mit überspringen
        redirect = str(buf)[start:-9] # \r\n\r\n am Ende abschneiden
        print(redirect)
        webradios[station][1] = redirect.split("/")[2]
        webradios[station][2] = redirect[len(webradios[station][1])+7:]
        print(webradios[station][1])
        print(webradios[station][2])
        return "Redirect"
    else:
        print("no valid signature found")
        print(buf)
        return "Fail"


if connectAndTry() == "OK":
    buf = s.recv(32)
elif connectAndTry() == "OK": # 2nd try, in the meantime the station host and path have been replaced with redirect data
    buf = s.recv(32)
else:
    buf = None

while buf:
    player.writeData(buf)
    buf = s.recv(32)

s.close()


# https://docs.micropython.org/en/latest/library/utime.html

# This code snippet is not optimized
# now = time.ticks_ms()
# scheduled_time = task.scheduled_time()
# if ticks_diff(scheduled_time, now) > 0:
#     print("Too early, let's nap")
#     sleep_ms(ticks_diff(scheduled_time, now))
#     task.run()
# elif ticks_diff(scheduled_time, now) == 0:
#     print("Right at time!")
#     task.run()
# elif ticks_diff(scheduled_time, now) < 0:
#     print("Oops, running late, tell task to run faster!")
#     task.run(run_faster=true)