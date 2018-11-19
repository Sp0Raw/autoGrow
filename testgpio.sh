gpio -g mode 19 out  
gpio -g mode 6 out
while true; do  
    gpio -g write 19 1
    gpio -g write 6 0
    sleep 1
    gpio -g write 19 0
    gpio -g write 6 1
    sleep 1
done
