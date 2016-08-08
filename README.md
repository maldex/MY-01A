# Utility to configure SDA-01A / CZE-01A / CEA-01A / FU-01A PC Control 1Watt FM Transmitter
CLI Utility for configuring ???-01A Stereo FM Transmitter devices.
This is an unofficial and not supported rewrite of the protocol which the -01A Device (which resembles a 'Silicon Labs CP210x USB to UART Bridge') to the shipped 'SDA-01A PC control.exe'.
Use of either this utility or operating such an trasmitter according to local authorities is your own risk.

Usermanual: http://www.108mhz.com/download/SDA-01A%20User%20Manual.pdf

Thanks to the folks over at 'HHD Software' for the 'Free Serial Port Monitor' which allowed me to sniff serial communication on Windows.

## requirements
requires python (2.7isch) and pySerial.

## todo
- figure how to read backlight
- Automatic Power Off (APO) - won't do as it's useless
- setting a password
- interactive mode

## usage
```
# see the help page
python MY-01A.py --help

# be verbose when powering down
python MY-01A.py --debug --device //./COM8 --power off

# the backlight will come to live anyway
python MY-01A.py --verbose --device /dev/ttyUSB0 --backlight on

# lets start the 01A fully
python MY-01A.py --power on --stereo on --freq 99.9 --txpower 3 --linevol 25 --micvol 0
```
