#!/bin/bash
pulsecmd="pulseaudio -D --log-target=syslog"
runasuser="pi"

if [ "`whoami`" != "${runasuser}" ]; then
	sudo su - ${runasuser} -c "$0 \"$@\""
	exit $?
	fi

pid=`ps -x -o pid,cmd | grep "${pulsecmd}" | grep -v grep | awk '{print $1}'`
if [ "${pid}" != "" ]; then
	kill ${pid}
	fi

${pulsecmd}

text="hi, this is PulsAdio running on `hostname` at `hostname -I`."
if [ "$@" != "" ]; then
	text="$@"
	fi
echo "${text}" | festival --tts &