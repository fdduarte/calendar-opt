# Modelo Optimización Programación Dinámica Calendario Deportivo ANFP

Modelo computacional de optimización del calendario deportivo ANFP.

## Modo de uso

### Generar Calendario

- Cambiar en `SSTPA/modules/params/params.py` variable `MODEL` por `V3` o `V4`. 

Ubicado en la carpeta `ANFP-Calendar-Opt`

### Visualizar Rendimiento

- Se guardan los logs en una carpeta, por ejemplo `python3 SSTPA/V3/model.py >> STPA/logs/log_{fi}-{f2}`.

- Se modifican parámetros de `gen_stats.py`. `LOGS` son los nombres de los logs dentro de la ruta `PATH`.

- Comando `python3 gen_stats.py`.

- Se crea una carpeta en `output/visualization` llamada `{NAME}-vis` con distintas visualizaciones.


### SSTPA V3

`python3 SSTPA/V3/model.py`

### SSTPA V4

`python3 SSTPA/V4/model.py`

## Modelo 1: SSTPA

### Cambios Recientes

- `refactor:` modulo de carga de datos.

- Incorporacion de parametro `BREAKS`.

- `feature:` Generación de gráficos para fit de funciones lineales, polinomiales y exponenciales de tiempo vs fechas.

## Modelo 2: FPP

Standby

## To Do

- `pat_gen` refactor.

- Cambiar variables binarias por enteras.

- Sample de patrones para reducción de dimensionalidad.


