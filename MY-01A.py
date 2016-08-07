#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial   # pip install pyserial
import logging
import optparse
from sys import exit
from time import sleep

# class describing features sniffed at PC Control.exe talking to the CZE-01A (v.10)
class SDA01A(object):
    """
    Class talking to the SDA-01A / CZE-01A / FU-01A FM Trasmitter which is connected via USB.
    The USB connection resembles a serial port to the internal MCU of the 01A running at 57.6kbaud.
    The Protocol seems to be proprietary but follows a clear Request/OK-Response with optional 1-2 byte payload.
    """
    def __init__(self, serial_port='//./COM8', baudrate=57600):
        logging.info('Opening ' + serial_port + ' and probing for device')
        self.ser = serial.Serial( port=serial_port, baudrate=baudrate )
        self.t, self.v, self.s = self.getDeviceInfo()
        logging.info('found ' + self.t + ' (v.' + str(self.v) + ') with SN:' + self.s)

    def _io(self, data, raw=False):
        """ send data to device, gather and convert response """
        out = ''
        while not out.startswith('OK'):
            logging.debug('Writing ' + str( data ) )
            self.ser.write(data)
            while self.ser.inWaiting() < 2: sleep(0.01)  # wait for buffer to be filled
            out = ''
            while self.ser.inWaiting() > 0:
                out += self.ser.read(1) # read form device byte by byte

            if not out.startswith('OK'):
                logging.error('MISSREADING: ' + out)
                sleep(1)

        logging.debug('Read OK 0x' + out.encode('hex') )
        out = out[2:]  # remove first two bytes (the 'OK' string)

        if raw:
            return out  # do not convert to integer

        if len(out) == 2: # answer was two byte -> convert to int
            r = int(ord(out[0]) * 256 + ord(out[1]))
        elif len(out) == 1: # answer was one byte -> convert to int
            r = ord(out[0])
        else:
            r = None
        return r

    def getDeviceInfo(self):
        """ get some meta information """
        type = '???-' + ''.join(str(x) for x in self._io([0x01, 0x01, 0x1B], raw=True))
        version = self._io([0x01, 0x01, 0x16])
        serial = self._io([0x01, 0x01, 0x19], raw=True).encode('hex')
        return type, version, serial

    def powerOn(self, enabled=True):
        """ Switch device on or off """
        logging.info("01A: powerOn " + str(enabled))
        if enabled: self._io([0x01, 0x01, 0x03])     # startup signal
        else: self._io([0x01, 0x01, 0x02])          # shutdown signal
        sleep(3)

    def getFrequency(self):
        """ get current frequency in mhz """
        return self._io([0x01, 0x01, 0x1c]) / 10.0

    def setFrequency(self, mhz):
        """ set transmit frequency """
        assert mhz <= 108.0 and mhz >= 76.0, "frequency must be between 76 and 108mhz"
        if mhz < 87.5 or mhz > 104.0:   logging.warn("Frequency outside common FM reception")
        logging.info("01A: setFrequency " + str(mhz))
        mhz = int(mhz * 10)
        ordinals = [ ord(chr(int( mhz / 256) )), ord(chr(mhz%256)) ]
        self._io([0x01, 0x03, 0x0E] + ordinals)
        sleep(0.3)

    def getTxPower(self):
        """ get transmit power setting """
        return self._io([0x01, 0x01, 0x1f])

    def setTxPower(self, power):
        """ set trasmit power of device """
        assert power <= 15 and power >= 0, "Power must be between 0 and 15"
        logging.info("01A: setTxPower " + str(power))
        self._io([0x01, 0x02, 0x11] + [power])

    def getStereo(self):
        """ get stereo or mono mode """
        return self._io([0x01, 0x01, 0x18]) == 122

    def setStereo(self, enable=True):
        """ set stereo or mono mode"""
        logging.info("01A: setStereo " + str(enable))
        if enable:     self._io([0x01, 0x01, 0x0C]) # set stereo
        else:          self._io([0x01, 0x01, 0x0D]) # set mono

    def getLineVolume(self):
        """ get current volume setting of line input"""
        return self._io([0x01, 0x01, 0x1d])

    def setLineVolume(self, vol):
        """ set volume on line input """
        assert vol <= 30 and vol >= 0, "Volume must be between 0 and 30"
        logging.info("01A: setLineVolume " + str(vol))
        self._io([0x01, 0x02, 0x0F] + [vol])

    def getMicVolume(self):
        """ get current volume setting of microphone input"""
        return self._io([0x01, 0x01, 0x1e])

    def setMicVolume(self, vol):
        """ set volume on microphone input """
        assert vol <= 30 and vol >= 0, "Volume must be between 0 and 30"
        logging.info("01A: setMicVol " + str(vol))
        self._io([0x01, 0x02, 0x10] + [vol])

    # could not figure out which request answers blacklight, no getter :(
    def setBacklight(self, enabled=True):
        """ enables or disables the Baclkight of device display"""
        logging.info("01A: setBacklight " + str(enabled))
        if enabled: self._io([0x01, 0x01, 0x0A])
        else:       self._io([0x01, 0x01, 0x0B])

# some stuff for the CLI
def cli_report(my01A):
    """ assemble little report of device """
    assert isinstance(my01A, SDA01A)
    from os import linesep
    r = "<><><><><> " + my01A.t + " (" + my01A.s + ") <><><><><>" + linesep
    r += "Freq: " + str(my01A.getFrequency()) + "mhz, TxPower: " + str(my01A.getTxPower()) + ", Stereo: " + str(my01A.getStereo()) + linesep
    r += "Line: " + str(my01A.getLineVolume()) + ", Mic: " + str(my01A.getMicVolume()) + linesep
    return r

def cli_interactive(my01A):  # experimental
    """ interactive mode - keep screen refreshed? """
    assert isinstance(my01A, SDA01A)
    import os, sys
    k = ''
    while k.lower() != 'q':
        rep = cli_report(my01A)
        os.system("cls")
        print rep
        print
        # print "Keys:"
        # print "F/f Freq, T/t Transmit, S/s Stereo, L/l Line, M/m Mic"
        # print "B/b Backlight, P/p Power, Q/q Quit, Enter enter/refresh ",
        # todo: read keyboard interrupt and do something smart
        sleep(1)

# here we actually start
if __name__ == "__main__":
    # parse arguments given to this script
    parser = optparse.OptionParser(description="MY-01A.py  -  SDA-01A FM Transmitter configuration")
    parser.add_option('-I', '--interactive', action="store_true", dest="interactive", help="interactive mode (experimental)", default=False)

    parser.add_option('-v', '--verbose', action="store_true", dest="log_verbose", help="talk a bit more")
    parser.add_option('-d', '--debug', action="store_true", dest="log_debug", help="talk a lot more")

    parser.add_option('-D', '--device', action="store", dest="device", default="//./COM8",
                      help="Serial Port of 01A (//./COM0|/dev/ttyUSB0) [default:%default]")

    parser.add_option('-p', '--power', action="store", dest="power", help="switch device [on|off]", default=None)
    parser.add_option('-b', '--backlight', action="store", dest="backlight", help="switch backlight [on|off]", default=None)
    parser.add_option('-s', '--stereo', action="store", dest="stereo", help="switch stereo [on|off]", default=None)
    parser.add_option('-f', '--freq', action="store", dest="freq", help="set Frequency [76.0 ... 108.0] mhz", default=None)
    parser.add_option('-t', '--txpower', action="store", dest="txpower", help="set transmit power [0 ... 15]", default=None)
    parser.add_option('-l', '--linevol', action="store", dest="linevol", help="set line volume [0 ... 30]", default=None)
    parser.add_option('-m', '--micvol', action="store", dest="micvol", help="set mic volume [0 ... 30]", default=None)

    options, args = parser.parse_args()

    # configure logging
    verbosity = logging.WARN
    if options.log_verbose: verbosity = logging.INFO
    if options.log_debug: verbosity = logging.DEBUG

    logging.basicConfig(format='%(levelname)s:%(message)s',  level=verbosity)

    # instanciate object
    try:
        my_01a = SDA01A(options.device)
    except serial.serialutil.SerialException, e:
        # mostrly wrong serial device or busy / used by other program
        logging.fatal(str(e))
        exit(255)

    # configure device according to script arguments given
    if options.power is not None:
        my_01a.powerOn(options.power == "on")

    if options.backlight is not None:
        my_01a.setBacklight(options.backlight == "on")

    if options.stereo is not None:
        my_01a.setStereo(options.stereo == "on")

    if options.freq is not None:
        value = float(options.freq)
        if value < 76.0 or value > 108.0: logging.error("Frequency must be between 76.0 and 108.0")
        else:                       my_01a.setFrequency(value)

    if options.txpower is not None:
        value = int(options.txpower)
        if value < 0 or value > 15: logging.error("TX Power must be between 0 and 15")
        else:                       my_01a.setTxPower(value)

    if options.linevol is not None:
        value = int(options.linevol)
        if value < 0 or value > 30: logging.error("Line Volume must be between 0 and 30")
        else:                       my_01a.setLineVolume(value)

    if options.micvol is not None:
        value = int(options.micvol)
        if value < 0 or value > 30: logging.error("Mic Volume must be between 0 and 30")
        else:                       my_01a.setMicVolume(value)

    if options.interactive:
        cli_interactive(my_01a)

    print cli_report(my_01a)
    # finish
