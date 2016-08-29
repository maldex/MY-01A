#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, logging, subprocess, re, threading, Queue
from time import sleep

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

color_remover = re.compile('(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')

command_prefix = ''
pulse_audio = "~/MY-01A/a2dp/restart-pulseaudio.sh"
play_radio = 'mpg321 -q -l 0 http://radio.netstream.ch/planet105_256k_mp3 2> /dev/null &'

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
            while not out.endswith('#') and not out.endswith('(yes/no):') and not out.endswith('\r') and not out.endswith('\n'):
                out += self.proc.stdout.read(1)
                # print "->",; pprint( out )
            out = color_remover.sub('', out).strip().replace("\r", '')
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
            msg = myInstance.read() # block here until process produced something new
            if msg == '[bluetooth]#':
                continue  # cli ready

            elif msg.startswith('[agent]'):  # i guess pairing rewuest?
                passkey = msg.split(' ')[3]
                logging.info("answering yes to pairing request with passkey " + passkey)
                self.write('yes')
                c = command_prefix + '' + pulse_audio + ' \"confirming ' + ' '.join(passkey[-2:]) + '\" &'
                os.system(c)


            elif msg.endswith('(yes/no):'):
                logging.info("accepting unknown yes/no question with yes")
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
                        c = command_prefix + '' + pulse_audio + ' \"lost ' + self.devices[mac] + '\" &'
                        os.system(c)
                        sleep(3)
                        os.system(play_radio)
                else:
                    pass
                    # logging.debug("unknown [CHG]: '" + str(msg)  + "'")


            elif msg.startswith('[DEL]'):
                pass

            elif msg.startswith('[NEW] Controller'):
                mac = msg.split(' ')[2]
                name = ' '.join(msg.split(' ')[3:])
                self.controllers[mac] = name
                logging.info("added new controller " + mac + " (" + name + ")")

            elif msg.startswith('[NEW] Device'):
                mac = msg.split(' ')[2]
                name = ' '.join(msg.split(' ')[3:])
                self.devices[mac] = name
                logging.info("added new device " + mac + " (" + name + "), trusting")
                self.write('trust ' + mac)
                self.current_device = mac

            else:
                logging.debug("could not parse: '" + str(msg) + "'")
                pass


if __name__ == "__main__":
    c = command_prefix + '' + pulse_audio + ''
    os.system(c)
    os.system(play_radio)

    myInstance = myBluetoothCtlCli(command_prefix + 'bluetoothctl')
    myInstance.start()
    myInstance.process()