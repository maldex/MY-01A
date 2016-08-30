# raspberry pi as bluetooth speaker - headless paring

- follow this guide to setup your linux as A2DP Sink (Loudspeaker)
http://raspberrypi.stackexchange.com/questions/47708/setup-raspberry-pi-3-as-bluetooth-speaker
- make sure the following is installed:?  mpg321
- use 'bt-autopair.py' for headless automatic bluetooth pairing

## caveat
- pulseaudio has prooven to be quite unstable when alternaing inputsources, hence i restart it like all the times.
- pairing is being removed after disconnect: as pairing takes time, this time is used for restarting pulseadio

## /etc/rc.local
```
gov="ondemand"   # conservative ondemand userspace powersave performance
for e in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo ${gov} > ${e}
done
echo "20" > /sys/devices/system/cpu/cpufreq/ondemand/up_threshold

if [ -e /dev/ttyUSB0 ]; then
        su - pi -c "~/MY-01A/MY-01A.py --power on --stereo on --freq 87.6 --txpower 15 --linevol 24 --micvol 0"
        fi
find /var/log -iname "bt-autopair-*.log" -mtime +7 -exec rm {} \;
su - pi -c "~/MY-01A/a2dp/bt-autopair.py" 2>&1 | tee -a /var/log/bt-autopair-`date +%Y%m%d-%H%M`.log &

```