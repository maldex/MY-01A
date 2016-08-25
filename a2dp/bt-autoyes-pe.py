#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pprint import pprint
from time import sleep
import sys, os, logging, re
import pexpect
logging.basicConfig(format='%(levelname)s:%(message)s',  level=logging.DEBUG)


color_remover = re.compile('(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')

# prompt = "\r\x1b[0;94m[bluetooth]\x1b[0m"
# prompt = [ "\\x1b\[0;94m\[bluetooth\]\\x1b\[0m# ", "\[bluetooth\]# " ]
prompt =   "\\x1b\[0;94m\[bluetooth\]\\x1b\[0m# "
# prompt = "#"

# prompt = "\\x1b[0;94m"


child = pexpect.spawn('bluetoothctl', echo=True)
# child.logfile = sys.stdout


logging.debug("waiting for initial prompt")
child.expect(prompt)
logging.debug("sending initializie" )

child.send("discoverable on\r")
child.expect("Changing discoverable .* succeeded")
child.send("pairable on\r")
child.expect("Changing pairable on succeeded")
child.send("agent on\r")
child.expect("Agent registered")
child.send("default-agent\r")
child.expect("Default agent request successful")
child.send("power on\r")
child.expect("Changing power .* succeeded")
child.expect(prompt)  # wating for prompt to return

logging.info("starting listener loop")


# Default agent request successful
# [NEW] Device BC:E5:9F:76:30:F3 S3500D CUTE
# Request confirmation
# [agent] Confirm passkey 018483 (yes/no):
# 	00001800-0000-1000-8000-00805f9b34fb
# [CHG] Device BC:E5:9F:76:30:F3 Paired: yes
# Authorize service
# [agent] Authorize service 0000110d-0000-1000-8000-00805f9b34fb (yes/no):

def question(before, after):
    if after.find("Confirm passkey") > 0:  # pairing
        passkey = after.split(' ')[-2]
        logging.info("confirming passkey " + passkey)
        child.send("yes\r")

    elif after.find("Authorize service") > 0:  # connecting
        logging.info("Authorizing Service")
        child.send("yes\r")

    else:
        logging.warn("could not decipper")


def info(before, after):
    inf = color_remover.sub('', after).split('\n')[0].strip()
    if inf.startswith('[0m# '):
        inf = inf.split('\r')[-1].strip()

    # if inf.startswith("[0;94m[bluetooth]") : return
    # logging.info("info: " + inf )
    print "LOG:",
    pprint(inf)


def lookupdevice(mac = 'BE:E9:46:65:72:47'):
    child.send("info " + mac + "\r")
    child.expect(prompt)
    for e in child.before.split(os.linesep):
        e = e.strip()
        if e.startswith("Name"):
            return e.split(': ')[1]

print lookupdevice()
while True:
    try:
        type = child.expect([".*\):", "\[.*\]", prompt] , timeout=1)
        if type == 0:
            question(child.before, child.after)
        elif type == 1:
            info(child.before, child.after)


    except pexpect.exceptions.TIMEOUT,e:
        child.flush()
        pass
