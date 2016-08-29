# raspberry pi as bluetooth speaker

http://raspberrypi.stackexchange.com/questions/47708/setup-raspberry-pi-3-as-bluetooth-speaker

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
su - pi -c "~/MY-01A/a2dp/bt-autopair.py " | tee /var/log/autoyes.log &

# say something
#echo "hi, this is `hostname` at `hostname -I`." | festival --tts
```