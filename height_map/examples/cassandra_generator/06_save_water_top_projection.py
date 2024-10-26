from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import pandas as pd
import numpy as np
from PIL import Image
from tqdm import tqdm

# Настройки подключения к Cassandra
CASSANDRA_HOST = 'localhost'  # Замените на ваш хост Cassandra
CASSANDRA_PORT = 9042
USERNAME = 'cassandra'  # Замените на ваше имя пользователя
PASSWORD = 'cassandra'  # Замените на ваш пароль

auth_provider = PlainTextAuthProvider(username=USERNAME, password=PASSWORD)
cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT, auth_provider=auth_provider)
session = cluster.connect('geo_data')  # Замените на ваше ключевое пространство


# Получение всех данных из таблицы coordinates
def get_all_points():
    query = "SELECT id, latitude, longitude, altitude FROM coordinates"
    rows = session.execute(query)

    points = []
    print("Начало загрузки данных из Cassandra...")
    for row in tqdm(rows, desc="Загрузка данных", unit="точек"):
        points.append([row.latitude, row.longitude, row.altitude])
    print("Загрузка данных завершена.")
    return pd.DataFrame(points, columns=['latitude', 'longitude', 'altitude'])


# Уровень воды для определения затопленных областей
flood_level = 120  # Установите нужный уровень воды

# Получение всех точек
data = get_all_points()

# Закрытие сессии и соединения
session.shutdown()
cluster.shutdown()

# Преобразование данных для создания сетки
latitudes = np.sort(data['latitude'].unique())
longitudes = np.sort(data['longitude'].unique())

latitude_grid, longitude_grid = np.meshgrid(latitudes, longitudes, indexing='ij')

# Создание словарей для быстрого поиска индексов
lat_to_idx = {lat: idx for idx, lat in enumerate(latitudes)}
lon_to_idx = {lon: idx for idx, lon in enumerate(longitudes)}

# Инициализация сетки высот
altitude_grid = np.full(latitude_grid.shape, np.nan)

# Векторизованное заполнение сетки высот
print("Начало обработки высот для создания сетки...")
data['lat_idx'] = data['latitude'].map(lat_to_idx)
data['lon_idx'] = data['longitude'].map(lon_to_idx)
altitude_grid[data['lat_idx'], data['lon_idx']] = data['altitude'].values
print("Обработка высот завершена.")

# Создание бинарной маски затопленных областей
print("Создание бинарной маски затопленных областей...")
flood_mask = altitude_grid <= flood_level

# Преобразование маски в изображение
print("Преобразование маски в изображение...")
# Инвертируем маску, чтобы затопленные области были 1 (True), а остальные 0 (False)
binary_mask = flood_mask.astype(np.uint8) * 255  # Умножаем на 255 для получения значений пикселей 0 или 255

# Создание изображения из маски
image = Image.fromarray(binary_mask)

# Преобразование в RGB и раскраска затопленных областей в синий цвет
print("Раскраска затопленных областей...")
image_rgb = image.convert('RGB')
pixels = image_rgb.load()

for i in tqdm(range(image_rgb.size[0]), desc="Обработка пикселей по ширине"):
    for j in range(image_rgb.size[1]):
        if binary_mask[j, i] == 255:
            pixels[i, j] = (0, 0, 255)  # Синий цвет для затопленных областей
        else:
            pixels[i, j] = (255, 255, 255)  # Белый цвет для остальных областей

# Сохранение изображения в формате PNG
output_filename = 'flooded_areas.png'
image_rgb.save(output_filename)
print(f"Изображение успешно сохранено: {output_filename}")
