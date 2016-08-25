#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, logging, subprocess, re
from time import sleep
logging.basicConfig(format='%(levelname)s:%(message)s',  level=logging.DEBUG)

color_remover = re.compile('(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')

from pprint import pprint

command = "bluetoothctl"
command = "ssh pi@10.83.6.129 " + command
prvi = subprocess.Popen(command.split(' '), shell=False,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)

while True:  # main loop
    out = ''
    while not out.endswith('# ') and not out.endswith('(yes/no): ') and not out.endswith(os.linesep):
        out += prvi.stdout.read(1)
    out = color_remover.sub('', out).strip()
    # out = out.replace('//ro','')
    if out == '' or out == os.linesep or out == '[bluetooth]#':
        continue

    logging.info("read from stdout: " + out)
    # pprint (out)

    if out.endswith('(yes/no):') or out == 'Authorize service':
        logging.info('yes/no: writing to stdin: yes')
        prvi.stdin.write('yes' + os.linesep)

    if out == 'Request PIN code':
        logging.info('PIN request: writing to stdin: 8306')
        prvi.stdin.write('8306' + os.linesep)

    if out.startswith('[NEW] Controller '):
        for start_cmd in ['agent on', 'discoverable on', 'pairable on', 'power on', 'default-agent']:
            logging.info("new controller: writing to stdin: " + start_cmd)
            prvi.stdin.write(start_cmd + os.linesep)
            sleep(0.25)
