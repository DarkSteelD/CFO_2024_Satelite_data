# Height Map services


```bash
(height) darius@MacBook-Pro-darius cassandra_generator % python 05_optimization_water_overflow.py
Начало загрузки данных из Cassandra...
Загрузка данных: 331776точек [00:03, 91639.59точек/s] 
Загрузка данных завершена.
Начало обработки высот для создания 3D-сетки...
Обработка высот завершена.
```

![Screenshot 2024-10-27 at 00.40.20.png](__assets__/Screenshot%202024-10-27%20at%2000.40.20.png)


## Run

You need to download `NASA Shuttle Radar Topography Mission Global 1 arc second V003` and run `data_preprocessing.py`, after this you need to do:

1. Up the infra cassandra db
2. run setup.py
3. run data_upload.py
4. run service.py


OR


run AirFlow DAG HeightMap


View Laravel WEB app for next work