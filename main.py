import vs10xx
from machine import SPI
import usocket as socket

webradios = [["Das Ding","swr-dasding-live.cast.addradio.de", "/swr/dasding/live/mp3/128/stream.mp3", 80],
             ["Bayern 3","br-br3-live.cast.addradio.de","/br/br3/live/mp3/128/stream.mp3",80],
             ["FM4","mp3stream1.apasf.apa.at","/", 8000],
             ["egofm","egofm-live.cast.addradio.de","/egofm/live/mp3/high/stream.mp3",80],
             ["Kosmos","radiostreaming.ert.gr","/ert-kosmos",80],
             ["egofm","egofm-ais-edge-400b-dus-dtag-cdn.cast.addradio.de","/egofm/live/mp3/high/stream.mp3?_art=dj0yJmlwPTkxLjQ5LjM2LjE1NiZpZD1pY3NjeGwtd2pub25jbm1iJnQ9MTYyNDA5ODA3MSZzPTc4NjZmMjljI2E5NDQ2ODczZWExYjY5ZDY1ZTlhOTEyNjFiYTBjZWEw",80]]



station = 3

print("Playing: "+webradios[station][0])
print(webradios[station][1])
print(webradios[station][2])
print(webradios[station][3])

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

    
addr = socket.getaddrinfo(webradios[station][1], webradios[station][3])[0][-1]
print(addr)
s = socket.socket()
s.connect(addr)

s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (webradios[station][2], webradios[station][1]), 'utf8'))
# print(s.recv(3200))
while True:
    buf = s.recv(32)
    if buf:
        #player.writeData(buf)
        
        print(buf)
    else:
        break

s.close()