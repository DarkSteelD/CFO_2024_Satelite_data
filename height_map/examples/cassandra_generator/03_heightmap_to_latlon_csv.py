import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt

# Загрузка сохраненного изображения карты высот
height_map_image = Image.open('modified_heightmap.png').convert('L')
height_map_data = np.array(height_map_image)

# Нормализация значений высоты для масштабирования
max_height = np.max(height_map_data)
normalized_data = height_map_data / max_height

# Параметры начальной точки (широта и долгота)
initial_latitude = 55.0  # пример широты
initial_longitude = 37.0  # пример долготы

# Между точками 10 метров, преобразуем в градусы
# 1 градус широты приблизительно равен 111000 метрам
meters_per_degree_lat = 111000
meters_per_degree_lon = meters_per_degree_lat * np.cos(np.radians(initial_latitude))

# Преобразование карты высот в массив координат
points = []
for i in range(normalized_data.shape[0]):
    for j in range(normalized_data.shape[1]):
        latitude = initial_latitude + (i * 10 / meters_per_degree_lat)
        longitude = initial_longitude + (j * 10 / meters_per_degree_lon)
        altitude = normalized_data[i, j] * max_height
        points.append([latitude, longitude, altitude])

# Сохранение массива в CSV
df = pd.DataFrame(points, columns=['latitude', 'longitude', 'altitude'])
df.to_csv('heightmap_3d_points.csv', index=False)

print("CSV файл успешно создан: heightmap_3d_points.csv")
