from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from tqdm import tqdm

# Настройки подключения к Cassandra
CASSANDRA_HOST = 'localhost'
CASSANDRA_PORT = 9042
USERNAME = 'cassandra'
PASSWORD = 'cassandra'

auth_provider = PlainTextAuthProvider(username=USERNAME, password=PASSWORD)
cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT, auth_provider=auth_provider)
session = cluster.connect('geo_data')


# Получение всех данных
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

# Преобразование данных для сетки
latitudes = np.sort(data['latitude'].unique())
longitudes = np.sort(data['longitude'].unique())

latitude_grid, longitude_grid = np.meshgrid(latitudes, longitudes, indexing='ij')

# Создание словарей для быстрого поиска индексов
lat_to_idx = {lat: idx for idx, lat in enumerate(latitudes)}
lon_to_idx = {lon: idx for idx, lon in enumerate(longitudes)}

# Инициализация сетки высот
altitude_grid = np.full(latitude_grid.shape, np.nan)

# Векторизованное заполнение сетки высот
print("Начало обработки высот для создания 3D-сетки...")
data['lat_idx'] = data['latitude'].map(lat_to_idx)
data['lon_idx'] = data['longitude'].map(lon_to_idx)
altitude_grid[data['lat_idx'], data['lon_idx']] = data['altitude'].values
print("Обработка высот завершена.")

# Настройка интерактивной визуализации
# plt.style.use('seaborn')  # Закомментировано или заменено

# Можно использовать другой стиль, например, 'ggplot'
plt.style.use('ggplot')

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Начальный уровень воды
initial_flood_level = 120  # Задайте начальный уровень воды


# Создание функции для обновления графика
def update(flood_level):
    ax.clear()

    # Создание маски для затопленных областей
    flood_mask = altitude_grid <= flood_level

    # Определение цветов
    colors = np.empty(altitude_grid.shape, dtype=object)
    colors[flood_mask] = 'blue'  # Затопленные области
    colors[~flood_mask] = 'brown'  # Суша

    # Визуализация поверхности местности
    surf = ax.plot_surface(latitude_grid, longitude_grid, altitude_grid, facecolors=colors, linewidth=0,
                           antialiased=False)

    # Добавление полупрозрачной плоскости уровня воды
    water_level = flood_level  # Уровень воды
    x_plane = latitude_grid
    y_plane = longitude_grid
    z_plane = np.full_like(latitude_grid, water_level)

    # Визуализация плоскости уровня воды
    ax.plot_surface(x_plane, y_plane, z_plane, color='cyan', alpha=0.3)

    # Настройки осей и заголовок
    ax.set_title('3D Карта Высот с учётом затопления (Уровень воды: {} м)'.format(flood_level))
    ax.set_xlabel('Широта')
    ax.set_ylabel('Долгота')
    ax.set_zlabel('Высота')

    # Установка лимитов по осям для лучшей визуализации
    ax.set_zlim(altitude_grid.min(), altitude_grid.max())

    # Настройка угла обзора
    ax.view_init(elev=45, azim=120)  # Угол обзора

    plt.draw()


# Первоначальная отрисовка графика
update(initial_flood_level)

# Добавление слайдера для изменения уровня воды
ax_slider = plt.axes([0.25, 0.02, 0.5, 0.03])  # Позиция слайдера: [лево, низ, ширина, высота]
flood_slider = Slider(
    ax=ax_slider,
    label='Уровень воды (м)',
    valmin=altitude_grid.min(),
    valmax=altitude_grid.max(),
    valinit=initial_flood_level,
)


# Обработка изменений слайдера
def on_flood_level_change(val):
    flood_level = flood_slider.val
    update(flood_level)


flood_slider.on_changed(on_flood_level_change)

plt.show()
