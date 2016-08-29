#!/bin/bash
pulsecmd="pulseaudio -D --log-target=syslog"
runasuser=`whoami` #"pi"

if [ "`whoami`" != "${runasuser}" ]; then
	sudo su - ${runasuser} -c "$0 \"$@\""
	exit $?
	fi

killall mpg321 2>/dev/null
pid=`ps -x -o pid,cmd | grep "${pulsecmd}" | grep -v grep | awk '{print $1}'`
if [ "${pid}" != "" ]; then
	kill ${pid}
	fi

${pulsecmd}

text="hi, this`hostname` at `hostname -I`"
if [ ! -z "$1" ]; then
	text="$@"
	fi
echo "${text}" | festival --tts &
