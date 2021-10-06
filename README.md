# Modelo Optimización Programación Dinámica Calendario Deportivo ANFP

Modelo computacional de optimización del calendario deportivo ANFP.

## Modo de uso

`main.py [-h] [--model MODEL] [--start_date START_DATE] [--end_date END_DATE] [--filepath FILEPATH] [--timelimit TIMELIMIT]`

- `MODEL`:
  - `1`: SSTPA V3
  - `2`: SSTPA V4
  - `3`: SSTPA MP
  - `4`: SSTPA MP CPLEX
  - `5`: SSTPA Benders

## Comandos útiles

- Correr campeonato de prueba:

`python main.py --start_date 4 --filepath data/campeonato_prueba.xlsx --model 5 --end_date 6`

- Correr campeonato real:

`python main.py --start_date 28 --filepath data/Datos.xlsx --model 5 --end_date 30`



