# raspberry pi as bluetooth speaker

http://raspberrypi.stackexchange.com/questions/47708/setup-raspberry-pi-3-as-bluetooth-speaker

## /etc/rc.local
```
# setting cpu frequency and scale-up threshold
gov="ondemand"   # conservative ondemand userspace powersave performance
for e in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo ${gov} > ${e}
done
echo "20" > /sys/devices/system/cpu/cpufreq/ondemand/up_threshold

# starting pulse audio deamon
su - pi -c "pulseaudio -D --log-target=syslog"
# powering on SDA-01A
su - pi -c "python ~/MY-01A/MY-01A.py --power on --stereo on --freq 101.2 --txpower 10 --linevol 25 --micvol 0"
# auto-yes-ing all bluetooth paring and service requests
su - pi -c "/home/pi/autoyes.py " 2>&1 | tee /var/log/autoyes.log &

# say something
echo "hi, this is `hostname` at `hostname -I`." | festival --tts
```