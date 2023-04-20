#!/bin/bash

read T
ti=1
while [ $ti -le $T ]
do
  read N M
  read -a C
  sum=0
  for ((i=0;i<N;i++)) do
    ((sum+=${C[$i]}))
  done
  ((modulo=$sum%$M))
  echo "Case #$ti: $modulo"
  ((ti++))
done
