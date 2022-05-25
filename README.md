# Modelo Optimización Programación Dinámica Calendario Deportivo ANFP

Modelo computacional de optimización del calendario deportivo ANFP.

## Requerimientos

- Python 3.10
- Licencia de Gurobi (`gurobi.lic`)

## Instalación

(Recomendado)

- crear un `venv` con la versión `3.10` de `python`. En MacOS se usa el comando `python3.10 -m venv venv`.
- Activar el `venv`. (Linux y MacOS `source venv/bin/activate`)
- Se puede comprobar que se esté conectado al `venv` con el comando `which python`.
- Se puede comprobar le versión de python con el comando `python -V`.

- Se deben instalar las dependencias `pip install -r requirements.txt`.
- Por último, se debe instalar la licencia de gurobi. Para esto ejecutar el script `license.sh` (`source scripts/license.sh`), donde se pedirá el path a `gurobi.lic`.

## Modo de uso

### Script

En linux y MacOS: `source scripts/run.sh`.

Detalles de los parámetros se encuentran en `scripts/run.sh`.

### Manual

`main.py [-h] [--model MODEL] [--start_date START_DATE] [--filepath FILEPATH] [--timelimit TIMELIMIT] [--mip_gap GAP] [--mip_focus FOCUS`

- `MODEL`:
  - `1`: SSTPA V3
  - `2`: SSTPA V4
  - `3`: SSTPA MP
  - `4`: SSTPA MP CPLEX
  - `5`: SSTPA Benders

#### Comandos útiles

- Correr campeonato de prueba:

`python main.py --start_date 4 --filepath data/campeonato_prueba.xlsx --model 5`

- Correr campeonato de prueba mediano

`python main.py --start_date 10 --filepath data/campeonato_prueba_10eq.xlsx --model 3`

- Correr campeonato real:

`python main.py --start_date 28 --filepath data/Datos.xlsx --model 5`
