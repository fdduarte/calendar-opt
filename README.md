# Modelo Optimización Programación Dinámica Calendario Deportivo ANFP

Modelo computacional de optimización del calendario deportivo ANFP.

[link](https://www.overleaf.com/3672921821bbsqnmywpbyj) modelo en pdf.

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

`main.py [-h] [--model MODEL] [--start_date START_DATE] [--breaks BREAKS] [--filepath FILEPATH] [--mip_gap MIP_GAP] [--mip_focus MIP_FOCUS] [--time_limit TIME_LIMIT] [--verbose VERBOSE] [--no_local_patterns] [--gurobi_no_log_console] [--gap GAP]`

- `MODEL`:
  - `1`: SSTPA V3
  - `2`: SSTPA V4
  - `3`: SSTPA MP
  - `4`: SSTPA MP CPLEX
  - `5`: SSTPA Benders

### CLI

Por facilidad se usa [invoke](https://www.pyinvoke.org/) para ejecutar el programa mediante comandos más cortos. El el archivo `tasks.py` se pueden modificar los parámetros al comienzo del archivo, y luego ejecutar algún campeonato mediante el comando `invoke run-{size}`.

Los tamaños (size) disponibles son tiny, small, med, big y huge.

Además, mediante el comando `invoke clear-cache` se elimina el cache generado de los parámetros de las instancias.
