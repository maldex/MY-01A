#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading, Queue

import os, sys, logging, subprocess, re
from time import sleep
logging.basicConfig(format='%(levelname)s:%(message)s',  level=logging.DEBUG)

color_remover = re.compile('(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')

from pprint import pprint
command_prefix = ''
command_prefix = "ssh pi@10.83.6.129 "


class myBluetoothCtlCli (threading.Thread):
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

    def run(self):   # thread
        logging.debug("starting stdout listener thread")
        self.initialize_agent()
        while True:
            out = ''
            while not out.endswith('#') and not out.endswith('(yes/no):') and not out.endswith(os.linesep):
                out += self.proc.stdout.read(1)
                # print "->",; pprint( out )
            out = color_remover.sub('', out).strip()   # .replace("\ro",'')
            self.stdout_queue.put(out)
        print "Exiting "

    def initialize_agent(self):
        for start_cmd in ['agent on', 'discoverable on', 'pairable on', 'power on', 'default-agent']:
            self.write(start_cmd + '\r')
            sleep(0.25)

    def write(self, c):
        self.proc.stdin.write(c + '\r')

    def read(self):
        return self.stdout_queue.get()

    def process(self):
        while True:
            msg = myInstance.read()
            # print "msg:",;pprint(msg)
            if msg == '[bluetooth]#':
                continue  # cli ready

            elif msg.startswith('[agent]'): # i guess pairing rewuest?
                passkey = msg.split(' ')[3]
                logging.info("answering yes to pairing request with passkey " + passkey)
                self.write('yes')
                c=command_prefix + '"/home/pi/MY-01A/a2dp/restart-pulseaudio.sh \"confirming ' + ' '.join(passkey[-2:]) + '\"" &'
                print c
                os.system(c)


            elif msg.endswith('(yes/no):'):
                logging.info("accepting unknown yes/no question with yes")
                self.write('yes')



            elif msg.startswith('[CHG]') or msg.startswith('[DEL]'):
                if msg.endswith('Connected: yes'):
                    mac = msg.split(' ')[2]
                    logging.info('connected device:: ' + mac + " - " + self.devices[mac])
                    self.current_device = mac
                    # print self.current_device

                elif msg.endswith('Connected: no'):
                    mac = msg.split(' ')[2]
                    self.write('remove ' + mac)
                    logging.info('lost device: ' + mac + " - " + self.devices[mac])
                    # print self.current_device
                    # if mac == self.current_device:
                    #     c = command_prefix + '"/home/pi/MY-01A/a2dp/restart-pulseaudio.sh \"lost ' + self.devices[mac] + '\""'
                    #     # c = command_prefix + 'echo \"lost ' + self.devices[mac] + '\" | ' + command_prefix +'"festival --tts"'
                    #     print c
                    #     os.system(c)
                else:
                    pass

            elif msg.startswith('[NEW] Controller'):
                mac = msg.split(' ')[2]
                name = ' '.join(msg.split(' ')[3:])
                self.controllers[mac] = name

            elif msg.startswith('[NEW] Device'):
                mac = msg.split(' ')[2]
                name = ' '.join(msg.split(' ')[3:])
                self.devices[mac] = name

            else:
                logging.debug("could not parse: '" + str(msg)  + "'")
                pass


if __name__ == "__main__":

    myInstance = myBluetoothCtlCli(command_prefix + 'bluetoothctl')
    myInstance.start()

    myInstance.process()

