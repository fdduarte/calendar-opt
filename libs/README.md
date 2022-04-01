# Modules

## Visualizar Rendimiento

- Guardar stdout una carpeta, por ejemplo `python3 SSTPA/V3/model.py fi ff >> STPA/logs/log_{fi}-{ff}`.

- Se modifican parámetros de `gen_stats.py`. `LOGS` son los nombres de los logs dentro de la ruta `PATH`.

- Comando `python3 gen_stats.py`.

- Se crea una carpeta en `output/visualization` llamada `{NAME}-vis` con distintas visualizaciones.

- Comando para guardar varios logs a una carpeta `for i in {fi..ff}; do python3 SSTPA/model.py $i 30 > SSTPA/logs/folder/log_$i-30; done `, por ejemplo, `for i in {18..25}; do python3 SSTPA/model.py $i 30 > SSTPA/logs/26-6/log_$i-30; done `