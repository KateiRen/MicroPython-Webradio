import vs10xx
from machine import SPI
import usocket as socket

webradios = [["Das Ding","swr-dasding-live.cast.addradio.de", "/swr/dasding/live/mp3/128/stream.mp3", 80],
             ["Bayern 3","br-br3-live.cast.addradio.de","/br/br3/live/mp3/128/stream.mp3",80],
             ["FM4","mp3stream1.apasf.apa.at","/listen.pls", 8000],
             ["egofm","egofm-live.cast.addradio.de","/egofm/live/mp3/high/stream.mp3",80],
             ["Kosmos","radiostreaming.ert.gr","/ert-kosmos",80],
             ["egofm","egofm-ais-edge-400b-dus-dtag-cdn.cast.addradio.de","/egofm/live/mp3/high/stream.mp3?_art=dj0yJmlwPTkxLjQ5LjM2LjE1NiZpZD1pY3NjeGwtd2pub25jbm1iJnQ9MTYyNDA5ODA3MSZzPTc4NjZmMjljI2E5NDQ2ODczZWExYjY5ZDY1ZTlhOTEyNjFiYTBjZWEw",80]]

# FM4 refusing connection, not working yet

station = 3

spi = SPI(1, vs10xx.SPI_BAUDRATE) # SPI bus id=1 pinout: SCK = 14, MOSI = 13, MISO = 12

player = vs10xx.Player(
    spi,
    xResetPin = 21,
    dReqPin = 22,
    xDCSPin = 23,
    xCSPin = 25,
    CSPin = None
)

print("VS10xx Player set up.")
player.setVolume(0.8) # the range is 0 to 1.0

class Streamer:
    def __init__(self, stations, station):
        self.name = stations[station][0]
        self.host = stations[station][1]
        self.path = stations[station][2]
        self.port = stations[station][3]
        
    def try2connect(self):
        print("Station Name: " + self.name)
        print("Station Host: " + self.host)
        print("Station Path: " + self.path)
        print("Station Port: " + str(self.port))
        s = socket.socket()
        addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        # print(addr)
        s.connect(addr)
        s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (self.path, self.host), 'utf8'))
        buf = s.recv(1000)
        s.close()
        # print(buf)
        # print(buf[9:15])
        if buf[9:15] == b'200 OK':
            print("\nSeems OK to start streaming")
            return True
        elif buf[9:18] == b'302 Found':
            print("\n302 Found, need to extract redirect address first...")
            start = str(buf).find("Location: ") + 10 # "Location: " mit überspringen
            redirect = str(buf)[start:-9] # \r\n\r\n am Ende abschneiden
            # print(redirect)
            self.host = redirect.split("/")[2]
            self.path = redirect[len(self.host)+7:]
            print("Updated Station Host: " + self.host)
            print("Updated Station Path: " + self.path)
            return True
        else:
            return False

    def connect(self):
        self.s = socket.socket()
        addr = socket.getaddrinfo(self.host, self.port)[0][-1]
        # print(addr)
        self.s.connect(addr)
        self.s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (self.path, self.host), 'utf8'))
        buf = self.s.recv(32)
        if buf[9:15] == b'200 OK':
            print("\nSeems OK to start streaming")
            # optionally advance to the radio stream start code - but the module takes it without noise
            return True
        else:
            return False
    
    def stream(self):
        return self.s.recv(32)

    def close(self):
        self.s.close()

radio = Streamer(webradios, station)

if radio.try2connect(): # check for successful initial connection and fetch CDN redirect, if any
    if radio.connect():
        buf = radio.stream()
        while buf:
            player.writeData(buf)
            buf = radio.stream()
        radio.close()

