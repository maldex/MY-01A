#!/bin/bash
### BEGIN INIT INFO
# Provides: instarc
# Short-Description: instarc dynamic instance loader
# Required-Start: $network $local_fs
# Required-Stop:
# chkconfig: 35 99 01
### END INIT INFO

## sample config which you are to save in /etc/instarc.d/xterm.cfg
#RUNASUSER="`whoami`"
#APPNAME="TERMINALS"
#declare -A INSTANCES
#INSTANCES=(    # dictionary
#	["session1"]="xterm -bg black -fg green"
#	["session2"]="xterm -fg black -bg green"
#)

opmode=$1; shift  			# first script-arg is mode, 
instance=$@				# all other args are instances
if [ "${opmode}" = "" ]; then opmode="status"; fi

#####################################################
if [ -z "${INSTARC_CFG}" ]; then
	n="`basename $0 | cut -d'.' -f2`.cfg"
	INSTARC_CFG="/etc/instarc.d/${n}"
	if [ -e "${n}" ]; then INSTARC_CFG="${n}"; fi
	fi

if [ ! -f ${INSTARC_CFG} ]; then
	echo >&2 "ERROR: no such instarc-config to source: ${INSTARC_CFG}"
	exit 255
	fi

declare -A INSTANCES
source ${INSTARC_CFG}
if [ "$?" != "0" ]; then
	echo >&2 "ERROR: could not source ${INSTARC_CFG}"
	exit 255
	fi
 

##################################################################################3
function rc_comment() { echo -n "$@"; }
function rc_status() {
	stat="$1"
	if [[ "$TERM" != xterm* ]] || ! { /usr/bin/which tput >/dev/null 2>&1 ; }; then
	case "${stat}" in
		"0")    echo "   [ OK ]" ;; "254")  echo "   [UNKN]" ;;
		"255")  echo "   [WARN]" ;; *)      echo "   [FAIL]" ;;
		esac
	else
	spacing=$(( `tput cols` * 6 / 7 ))
	echo -en '\033['${spacing}'D\033['${spacing}'C'
	case "${stat}" in
		"0")    echo -e '[\E[0;32m'"\033[1m OK \033[0m]" ;;
		"255")  echo -e '[\E[1;33m'"\033[1mWARN\033[0m]" ;;
		*)      echo -e '[\E[0;31m'"\033[1mFAIL\033[0m]" ;;
		esac
	fi
	return ${stat}
}

function getPids() {
        grep -lZ "_INSTARC=$1 " /proc/[0-9]*/environ 2>/dev/null | tr '\000' '\n' | cut -d'/' -f3 | sort -r | tr '\n' ' '
}
function getProcessInfo() {
        echo "PID: $1 CMD: `cat /proc/$1/cmdline | tr '\000' ' '`"
}

function opmode_start() {
	rc_comment "Starting '$1': "
	if [ "`getPids $1`" != "" ]; then
		rc_comment "already running"
		rc_status 255; return 0
		fi
		
        export _INSTARC="$1 "
        export _INSTARC_CMD="$2"
	######### here the actual program is started ######### 
        ${_INSTARC_CMD} > $1.out 2>&1 &
	r=$?
	######### here the actual program is started #########
        unset _INSTARC 
	unset _INSTARC_CMD
 
	if [ "${r}" != "0" ]; then 
		rc_comment "COULD NOT START '_INSTARC_CMD'"
		rc_status 4; return 4
		fi
 
	sleep 0.5
	if [ "`getPids $1`" == "" ]; then
		rc_comment "failed to stay alive, check $1.out"
		rc_status 5; return 5
		fi
	rc_comment "`getPids $1`"
	rc_status 0
	return 0
}

function opmode_stop() {
	rc_comment "Stopping '$1': "
	if [ "`getPids $1`" == "" ]; then
		rc_comment "already dead"
		rc_status 0; return 0
		fi
	kill -SIGTERM `getPids $1`
	for d in `seq 1 10`; do
		if [ "`getPids $1`" == "" ]; then break; fi
		sleep 0.1
		rc_comment "."
	done
	if [ "`getPids $1`" == "" ]; then
		rc_comment " term ok"
		rc_status 0; return 0
		fi
	rc_comment "!"
	kill -SIGKILL `getPids $1`
	sleep 0.5
	if [ "`getPids $1`" == "" ]; then
		rc_comment " killed"
		rc_status 0; return 0
		fi
	rc_comment " FAILED on `getPids $1`"
	rc_status 6; return 6
}


function opmode_status() {
	pids=`getPids $1`
	for pid in ${pids}; do	getProcessInfo ${pid} ; done
	rc_comment "Status '$1': "
	if [ "${pids}" = "" ]; then
		rc_comment "no process found"
		rc_status 2; return 2
		fi
	rc_comment "PID ${pids}"
	rc_status 0; return 0
}
	
function help() { echo "instarc - an arbitrary instance spawner
usage:
	$0 (start|stop|status|restart) [instance1 instance7 ....]
"
}

### here we go
if [ "`whoami`" != "${RUNASUSER}" ]; then 	# change user
	#args="$@"; sudo su - ${RUNASUSER} -c "bash -c \"$0 $args\""
	args="$@"; sudo su - ${RUNASUSER} -c "$0 $args"
	exit $?
	fi

if [ "${instance}" = "" ]; then 	# if no instances given as args
	instance=${!INSTANCES[@]}  	# use KEY.value of instances-dict
	fi


RETVAL=0

for i in ${instance}; do
	c="${INSTANCES[${i}]}"		# use key.VALUE of instances-dict
	if [ "${c}" == "" ]; then
		rc_comment "instance '${i}' has no associated cmd, skipping"
		rc_status 255; continue
		fi
	i="${APPNAME}.${i}"
	case "${opmode}" in
	"start")
		opmode_start ${i} "${c}"
		RETVAL=$((${RETVAL}+$?))
		;;
	"stop")
		opmode_stop ${i}
		RETVAL=$((${RETVAL}+$?))
		;;
	"status")
		opmode_status ${i}
		RETVAL=$((${RETVAL}+$?))
		;;
	"restart")
		$0 stop
		$0 start
		;;
	*)	
		help; exit 255
		;;
	esac
done
exit ${RETVAL}
