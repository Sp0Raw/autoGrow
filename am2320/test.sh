#!/bin/bash
for ((varF = 1; varF <= 1000; varF++)); do
 
    echo "number is $varF"
 
 
 for var in 17 27 22 5 6 13 19 26; do
  gpio -g mode $var out
  gpio -g write $var 0
  ## echo The $var item
  sleep 1
 done
 for var in 17 27 22 5 6 13 19 26; do
  gpio -g mode $var out
  gpio -g write $var 1
  sleep 1
 done
done
