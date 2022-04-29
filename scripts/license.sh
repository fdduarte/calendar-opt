#!/bin/bash

if [ ! -d "./venv/lib/python3.10/" ]; then
  echo "No se encontró el directorio del virtual environment. Debe crear el venv con el comando python3.10 -m venv venv."
  exit 0
fi

if [ ! -d "./venv/lib/python3.10/site-packages/gurobipy/.libs" ]; then
  echo "No se encontró el directorio de gurobi. Dentro del venv (source venv/bin/activate), instale gurobipy (pip install gurobipy)"
  exit 0
fi

echo "Ingrese el path a gurobi.lic (default \"./gurobi.lic\"):"
read x

if [ "${x}" = "" ]; then
  PATH_TO_LIC="./gurobi.lic"
else
  PATH_TO_LIC="${x}"
fi

if [ ! -e "${PATH_TO_LIC}" ]; then
  echo "Path a la licencia incorrecto."
  exit 0
fi

cp "${PATH_TO_LIC}" "./venv/lib/python3.10/site-packages/gurobipy/.libs"
