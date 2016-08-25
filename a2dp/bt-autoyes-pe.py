#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pprint import pprint
from time import sleep
import sys, os, logging, re
import pexpect      # sudo pip install pexpect
logging.basicConfig(format='%(levelname)s:%(message)s',  level=logging.DEBUG)


color_remover = re.compile('(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')

# prompt = "\r\x1b[0;94m[bluetooth]\x1b[0m"
# prompt = [ "\\x1b\[0;94m\[bluetooth\]\\x1b\[0m# ", "\[bluetooth\]# " ]
prompt =   "\\x1b\[0;94m\[bluetooth\]\\x1b\[0m# "
# prompt = "#"

# prompt = "\\x1b[0;94m"

btctl = 'bluetoothctl'
btctl = "ssh pi@10.83.6.129 " + btctl
child = pexpect.spawn(btctl, echo=True)
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
        c = 'echo "i hereby confirm the pass key ' + passkey + '" | festival --tts &'
        os.system(c)
        print c

    elif after.startswith("Authorize service") or after.endswith('(yes/no):'):  # connecting
        logging.info("Authorizing Service")
        child.send("yes\r")

    else:
        logging.warn("could not decipper - sending yes anyway")
        pprint(before)
        pprint(after)
        child.send("yes\r")


def info(before, after):
    inf = color_remover.sub('', after).split('\n')[0].strip()
    if inf.startswith('[0m# '):
        inf = inf.split('\r')[-1].strip()

    if inf.endswith("Connected: yes") or inf.endswith("Connected: no"):
        mac = inf.split(' ')[-3]
        device = lookupdevice(mac)
        inf = inf.replace(mac, device)
        if inf.endswith("Connected: yes"): say = "device " + device + " is now connected!"
        if inf.endswith("Connected: no"):  say = "device " + device + " has been lost!"

        c = './restart-pulseaudio.sh "' + say + '"'
        print c
        os.system(c)
        sleep(0.5)

    if inf.startswith("[NEW]"):
        inf = ' '.join(inf.split(' ')[0:2]) + ' ' + ' '.join(inf.split(' ')[3:])
        inf = inf + " hi there how are you?"
        c = 'echo "' + inf + '" | festival --tts &'
        os.system(c)
        print c

    logging.info("notice: " + inf )



def lookupdevice(mac = 'BE:E9:46:65:72:47'):
    child.send("info " + mac + "\r")
    child.expect(prompt)
    for e in child.before.split(os.linesep):
        e = e.strip()
        if e.startswith("Name"):
            return e.split(': ')[1]
    return mac


while True:
    try:
        type = child.expect([".*\):", "\[.*\]", prompt] , timeout=3)
        b = color_remover.sub('', child.before).strip()
        a = color_remover.sub('', child.after).strip()
        if type == 0:
            question(b,a)
        elif type == 1:
            info(b,a)


    except pexpect.exceptions.TIMEOUT:
        child.flush()
        child.send("version\r")
        child.expect(prompt)
        pass
