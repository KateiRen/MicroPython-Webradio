# MicroPython Webradio

A minimalistic test / approach to turn an ESP32 plus a VS10xx module into a web radio.

Based on my VS10xx port [here](https://github.com/KateiRen/vs10xx-micropython) the only thing to add is a socket connection to a valid webradio network ressource.

As most stations provide static entry points that respond with a "302 Found" redirect to a dynamically changing CDN source, this layer had to be modelled in the code as well.
