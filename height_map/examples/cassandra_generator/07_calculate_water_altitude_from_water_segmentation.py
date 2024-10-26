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

# Загрузка изображения и создание бинарной маски
print("Загрузка и обработка изображения...")
image_filename = 'flooded_areas.png'  # Замените на ваше имя файла
image = Image.open(image_filename).convert('RGB')

# Проверка размеров изображения и сетки высот
if image.size != (altitude_grid.shape[1], altitude_grid.shape[0]):
    print("Размеры изображения и сетки высот не совпадают.")
    print(f"Размер изображения: {image.size}")
    print(f"Размер сетки высот: {(altitude_grid.shape[1], altitude_grid.shape[0])}")
    # Масштабирование изображения до размеров сетки высот
    print("Масштабирование изображения до размеров сетки высот...")
    image = image.resize((altitude_grid.shape[1], altitude_grid.shape[0]), Image.NEAREST)

# Преобразование изображения в массив
image_array = np.array(image)

# Создание бинарной маски затопленных областей
# Предполагаем, что затопленные области имеют синий цвет (0, 0, 255)
print("Создание бинарной маски затопленных областей...")
flood_mask = np.all(image_array == [0, 0, 255], axis=-1)

# Извлечение высот затопленных областей
print("Извлечение высот затопленных областей...")
flooded_altitudes = altitude_grid[flood_mask]

# Проверка наличия затопленных точек
if len(flooded_altitudes) == 0:
    print("Затопленных областей не обнаружено на изображении.")
    flood_level = None
else:
    # Определение уровня воды
    flood_level = np.max(flooded_altitudes)
    print(f"Определённый уровень воды: {flood_level} м")

# Дополнительно можно проверить высоты незатопленных областей
non_flooded_altitudes = altitude_grid[~flood_mask]
if len(non_flooded_altitudes) > 0:
    min_non_flooded_altitude = np.min(non_flooded_altitudes)
    print(f"Минимальная высота среди незатопленных областей: {min_non_flooded_altitude} м")
    print(f"Уровень воды находится между {flood_level} м и {min_non_flooded_altitude} м")
else:
    print("Все области затоплены.")

# Вывод результата
if flood_level is not None:
    print(f"\nУровень воды, использованный при создании изображения: {flood_level} м")
else:
    print("\nНе удалось определить уровень воды.")
