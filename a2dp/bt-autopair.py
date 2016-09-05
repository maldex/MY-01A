#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, logging, subprocess, re, threading, Queue
from time import sleep

url="http://radio.netstream.ch/planet105club_192k_mp3"
#url="http://radio.netstream.ch/planet105_256k_mp3"

radio = "mpg321 -q -l 0 "+url+" &"
radio = "./rc.idlestream.sh restart &"
pulse_audio = "./rc.pulseaudio.sh restart &"
command_prefix = ''

color_remover = re.compile('(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

blacklist = ['00:00:00:00:00:00',
             'BE:E9:46:65:72:48']

class myBluetoothCtlCli(threading.Thread):
    def __init__(self, command):
        threading.Thread.__init__(self)
        self.daemon = True
        self.stdout_queue = Queue.Queue()
        self.proc = subprocess.Popen(command.split(' '), shell=False,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
        self.devices = {}
        self.controllers = {}
        self.current_device = '00:00:00:00:00:00'

    def run(self):  # thread
        logging.debug("starting stdout listener thread")
        self.initialize_agent()
        while True:
            out = ''
            while not out.endswith('# ') and not out.endswith('o): ') and not out.endswith(
                    '\n'):  # and not out.endswith('\r'):
                out += self.proc.stdout.read(1)
                # from pprint import pprint
                # print "->",; pprint( out )
            out = color_remover.sub('', out).strip()  # .replace('\ro','')
            out = out.strip()
            if out == '': continue
            self.stdout_queue.put(out)

    def initialize_agent(self):
        for start_cmd in ['agent on', 'discoverable on', 'pairable on', 'power on', 'default-agent']:
            self.write(start_cmd + '\r')

    def write(self, c):
        self.proc.stdin.write(c + '\r')
        sleep(0.2)

    def read(self):
        return self.stdout_queue.get()

    def process(self):
        while True:
            msg = myInstance.read()  # block here until process produced something new
            # from pprint import pprint
            # pprint(msg)

            if msg == '[bluetooth]#':
                continue  # cli ready

            elif msg.startswith('[agent] Confirm passkey'):  # i guess pairing rewuest?
                passkey = msg.split(' ')[3]
                logging.info("answering yes to pairing request with passkey " + passkey)
                self.write('yes')
                restart_pulse('confirming ' + ' '.join(passkey[-2:]) + '')
				
            elif msg.startswith('[agent] Authorize service'):
                logging.info("answering yes to service request")
                self.write('yes')


            elif msg.endswith('o):'):
                logging.info("answering yes to unknown yes/no question with yes")
                self.write('yes')


            elif msg.startswith('[CHG]'):
                if msg.endswith('Connected: yes'):  # this even being called?
                    mac = msg.split(' ')[2]
                    logging.info('connected device: ' + mac + " - " + self.devices[mac])
                    self.current_device = mac

                elif msg.endswith('Connected: no'):
                    mac = msg.split(' ')[2]
                    logging.info('lost device: ' + mac + " (" + self.devices[mac] + "), untrusting and removing")
                    self.write('untrust ' + mac)
                    self.write('remove ' + mac)
                    if mac == self.current_device:
                        restart_pulse('lost ' + self.devices[mac] + '', play_radio=True)
                else:
                    pass
                    # logging.debug("unknown [CHG]: '" + str(msg)  + "'")


            elif msg.startswith('[DEL]'):
                pass

            elif msg.startswith('[NEW] Controller'):
                mac = msg.split(' ')[2]
                name = ' '.join(msg.split(' ')[3:])
                self.controllers[mac] = name
                logging.info("added new controller " + mac + " (" + name + ") - " + msg)

            elif msg.startswith('[NEW] Device'):
                mac = msg.split(' ')[2]
                name = ' '.join(msg.split(' ')[3:])
                self.devices[mac] = name
                if mac in blacklist:
                    logging.warning("blacklisted device! blocking " + mac + " (" + name + ")")
                    self.write('block ' + mac)
                else:
                    logging.info("added new device " + mac + " (" + name + "), trusting")
                    self.write('trust ' + mac)
                    self.current_device = mac

            else:
                # if not msg.startswith('00001'): logging.debug("could not parse: '" + str(msg) + "'")
                pass
				
def restart_pulse(text=None, play_radio=False):
    if text is not None:
        with open('/tmp/welcome.txt','w') as f:
            f.write(text)
        #os.system('cat /tmp/welcome.txt | text2wave  -o /tmp/welcome.wav')
        #os.system('aplay /tmp/welcome.wav')
    logging.info("restarting pulseaudio " + str(text))
    os.system('killall mpg321')
    os.system(pulse_audio)  #(pulse_audio)
    if play_radio:
        #sleep(1)
        os.system(radio)

		
		
if __name__ == "__main__":
    #os.system('echo "hi, this is `hostname` at `hostname -I`." > /tmp/welcome.txt')
    #os.system('echo "hi, this is `hostname`." > /tmp/welcome.txt')
    #os.system('killall pulseaudio mpg321 aplay')
    restart_pulse("hi, this is the bluetooth auto answering machine", play_radio=True)
    

    myInstance = myBluetoothCtlCli(command_prefix + 'bluetoothctl')
    myInstance.start()
    myInstance.process()
