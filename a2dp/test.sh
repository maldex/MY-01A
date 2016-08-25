#!/usr/bin/expect -f

spawn "bluetoothctl"
expect "#"
send "discoverable on\r"
expect "Changing discoverable on succeeded"
send "pairable on\r"
expect "Changing pairable on succeeded"
send "agent on\r"
expect "Agent registered"
send "default-agent\r"
expect "Default agent request successful"
send "power on\r"
expect "Changing power on succeeded"

#[bluetooth]# default-agent
#Default agent request successful
#[NEW] Device BC:E5:9F:76:30:F3 S3500D CUTE
#Request confirmation
#[agent] Confirm passkey 018483 (yes/no):
#
#	00001132-0000-1000-8000-00805f9b34fb
#	00001200-0000-1000-8000-00805f9b34fb
#	00001800-0000-1000-8000-00805f9b34fb
#[CHG] Device BC:E5:9F:76:30:F3 Paired: yes
#Authorize service
#[agent] Authorize service 0000110d-0000-1000-8000-00805f9b34fb (yes/no):

expect "agent*Confirm passkey*): "
send "yes\r"

expect "agent*Authorize service*): "
send "yes\r"       ;# this shows up and if the connection with the computer isn't initialised, both top level expects timeout and this gets send.
interact #Just so that you can continue debugging afterwards