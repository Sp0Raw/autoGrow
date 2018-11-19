#/bin/sh
for ((varF = 1; varF <= 1000; varF++)); do
  #clear
  echo "======================================"
  date && echo num rec $varF
  echo "======================================" 
  #echo " num rec "  && echo $varF
  /root/am2320/main.sh
  echo "**************************************"  
sleep 60
done
