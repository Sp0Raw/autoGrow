#!/bin/bash
 
for var in 17 27 22 5 6 13 19 26; do
 
  gpio -g mode $var out 
  gpio -g write $var 1
  sleep 2
## echo The $var item
 
done
