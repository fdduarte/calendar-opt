#!/bin/sh

# Run full champ

START=25
END=30
MODEL=3
TIMESTAMP=$(date +%s)
LOG=0 # 0 False, 1 True
MULTIPLE_DATES=0 # 0 False, 1 True
RANGE=${START}..29
TOY_EXAMPLE=0 # 0 False, 1 True

if [ ${TOY_EXAMPLE} -eq 1 ]; then
  if [ ${LOG} -eq 0 ]; then
    python main.py --start_date 4 --end_date 6 --model ${MODEL} --filepath data/campeonato_prueba.xlsx
  else
    python main.py --start_date 4 --end_date 6 --model ${MODEL} --filepath data/campeonato_prueba.xlsx > logs/${TIMESTAMP}-TOY.log
  fi
else
  if [ ${MULTIPLE_DATES} -eq 0 ]; then
    if [ ${LOG} -eq 0 ]; then
      python main.py --start_date ${START} --end_date ${END} --model ${MODEL}
    else
      python main.py --start_date ${START} --end_date ${END} --model ${MODEL} > logs/${TIMESTAMP}-${START}-${END}.log
    fi
  else
    for i in {${RANGE}}; do 
      if [ ${LOG} -eq 0 ]; then
      python main.py --start_date ${i} --end_date ${END} --model ${MODEL} --breaks 2
      else
        python main.py --start_date ${i} --end_date ${END} --model ${MODEL} > logs/${TIMESTAMP}-${i}-${END}.log
      fi;
      done
  fi
fi
