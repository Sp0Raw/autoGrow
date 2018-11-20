#/bin/sh
for val in  28-011319fed7ec 28-01131a050835 28-01131a190d81;
do
 cat /sys/bus/w1/devices/$val/w1_slave
done
