import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Настройки подключения к Cassandra
CASSANDRA_HOST = 'localhost'
CASSANDRA_PORT = 9042
USERNAME = 'cassandra'
PASSWORD = 'cassandra'

auth_provider = PlainTextAuthProvider(username=USERNAME, password=PASSWORD)
cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT, auth_provider=auth_provider)
session = cluster.connect('geo_data')

def get_all_points():
    query = "SELECT id, latitude, longitude, altitude FROM coordinates"
    rows = session.execute(query)
    data = pd.DataFrame(rows, columns=['id', 'latitude', 'longitude', 'altitude'])
    return data

# Получаем данные из базы данных
data = get_all_points()

session.shutdown()
cluster.shutdown()

# Извлекаем координаты и высоты
latitude = data['latitude'].values
longitude = data['longitude'].values
altitude = data['altitude'].values

# Задаем уровень воды
water_level = float(input("Введите уровень воды (в метрах): "))

# Создаем сетку для интерполяции
num_grid_points = 200
grid_lon, grid_lat = np.meshgrid(
    np.linspace(np.min(longitude), np.max(longitude), num_grid_points),
    np.linspace(np.min(latitude), np.max(latitude), num_grid_points)
)

# Интерполируем высоты на сетку
grid_altitude = griddata(
    points=(longitude, latitude),
    values=altitude,
    xi=(grid_lon, grid_lat),
    method='linear'
)

# Создаем маску затопленных областей
flooded_mask = grid_altitude <= water_level

# Создаем график
plt.figure(figsize=(12, 10))

# Отображаем рельеф местности
levels = np.linspace(np.nanmin(grid_altitude), np.nanmax(grid_altitude), 100)
contourf = plt.contourf(grid_lon, grid_lat, grid_altitude, levels=levels, cmap='terrain', alpha=0.7)

# Накладываем затопленные области
plt.contourf(grid_lon, grid_lat, flooded_mask, levels=[0.5, 1], colors='blue', alpha=0.5)

# Добавляем цветовую шкалу и подписи
plt.colorbar(contourf, label='Высота над уровнем моря (м)')
plt.xlabel('Долгота')
plt.ylabel('Широта')
plt.title(f'Затопленные территории при уровне воды: {water_level} м')
plt.show()
