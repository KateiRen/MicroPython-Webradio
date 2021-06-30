import vs10xx
from machine import SPI
from machine import freq
import usocket as socket
from rotaryencoder import RotaryEncoder

stations = [["DASDING","swr-dasding-live.cast.addradio.de", "/swr/dasding/live/mp3/128/stream.mp3", 80],
             ["Bayern 3","br-br3-live.cast.addradio.de","/br/br3/live/mp3/128/stream.mp3",80],
             ["egofm","egofm-live.cast.addradio.de","/egofm/live/mp3/high/stream.mp3",80],
             ["egoFM V2", "mp3ad.egofm.c.nmdn.net", "/egofm_128/livestream.mp3?", 80],
             ["Antenne Bayern Rockantenne", "mp3channels.webradio.antenne.de", "/rockantenne", 80],
             ["Puls", "streams.br.de", "/puls_2.m3u", 80],
             ["Deutschlandfunk", "st01.sslstream.dlf.de", "/dlf/01/128/mp3/stream.mp3", 80],
             ["Freies Sender Kombinat HH", "stream.fsk-hh.org", "/fsk.ogg.m3u", 8000],
             ["MDR Jump", "mdr-jump-live.cast.addradio.de", "/mdr/jump/live/mp3/128/stream.mp3", 80],
             ["MDR Sputnik", "mdr-sputnik-live.cast.addradio.de", "/mdr/sputnik/live/mp3/128/stream.mp3", 80],
             ["NDR Blue", "ndr-ndrblue-live.cast.addradio.de", "/ndr/ndrblue/live/mp3/128/stream.mp3", 80],
             ["Radio Blau", "stream.radioblau.de", "/", 80],
             ["Radio France FIP", "direct.fipradio.fr", "/live/fip-midfi.mp3", 80],
             ["BBC Radio 2", "bbcmedia.ic.llnwd.net", "/stream/bbcmedia_radio2_mf_p", 80],
             ["Rai Radio 2 Indie", "icestreaming.rai.it", "/15.mp3", 80],
             ["NPO Radio 2 NL", "icecast.omroep.nl", "/radio2-bb-mp3.m3u", 80],
             ["NRK P3", "lyd.nrk.no", "/nrk_radio_p3_mp3_h", 80],
             ["ORF FM 4", "mp3stream1.apasf.apa.at", "/1", 8000],
             ["Rock Antenne", "mp3.webradio.rockantenne.de", "/", 80],
             ["Landeswelle Thueringen","stream.landeswelle.de","/lwt/mp3-128/web/stream.mp3",80],
             ["Sveriges Radio P3", "sverigesradio.se", "/topsy/direkt/164-hi-mp3.pls", 80]]

# FM4 refusing connection, not working yet
# ["FM4","mp3stream1.apasf.apa.at","/listen.pls", 8000],

station = 3
volume = 0.8

re = RotaryEncoder(36, 35, 34)  # Read Only Pins verwenden
print("Rotary Encoder set up.")

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

    def updateStation(self):
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
    
    def stream(self, buffsize):
        if buffsize>0:
            return self.s.recv(buffsize)
        else:
            return self.s.read(8192)

    def close(self):
        self.s.close()

radio = Streamer(stations, station)
print("Streamer set up.")

print("Taktrate bei: {0}".format(freq()))

def turnLeft():
    global volume
    global station
    if re.buttonIsPressed():
        if station > 0:
            station -= 1
            print("Senderwechsel auf Preset {0}".format(station))
            radio.updateStation()
            connect()
        else:
            print("Niedrigster Sender erreicht")

    else:
        volume = min(1,max(0,volume-0.05))
        player.setVolume(volume) # the range is 0 to 1.0
        print("Volume: {0}".format(volume))

def turnRight():
    global volume
    global station
    if re.buttonIsPressed():
        if station < len(stations)-1:
            station += 1
            print("Senderwechsel auf Preset {0}".format(station))
            radio.updateStation()
            connect()
        else:
            print("Höchster Sender erreicht")
    else:
        volume = min(1,max(0,volume+0.05))
        player.setVolume(volume) # the range is 0 to 1.0
        print("Volume: {0}".format(volume))

def connect():
    if radio.try2connect(): # check for successful initial connection and fetch CDN redirect, if any
        if radio.connect():
            loop()


def loop():
    while True:
        #re.evalState(turnRight, turnLeft, None) # keine Funktion für Button press übergeben sondern in den anderen Callbacks auswerten
        player.writeData(radio.stream(0))
        # buf = radio.stream(12800)
        # while buf:
        #     re.evalState(turnRight, turnLeft, None) # keine Funktion für Button press übergeben sondern in den anderen Callbacks auswerten
        #     player.writeData(buf)
        #     buf = radio.stream(12800)       

connect()

# if radio.try2connect(): # check for successful initial connection and fetch CDN redirect, if any
#     if radio.connect():
#         buf = radio.stream(32)
#         while buf:
#             re.evalState(turnRight, turnLeft, None) # keine Funktion für Button press übergeben sondern in den anderen Callbacks auswerten
#             player.writeData(buf)
#             buf = radio.stream(32)
#         radio.close()
#radio.close()