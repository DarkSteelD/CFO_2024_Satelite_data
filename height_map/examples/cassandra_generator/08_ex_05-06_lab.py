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
plt.style.use('ggplot')

fig = plt.figure(figsize=(16, 8))

# Создаем два подграфика: левый для 3D визуализации, правый для 2D вида сверху
ax3d = fig.add_subplot(121, projection='3d')
ax2d = fig.add_subplot(122)

# Начальный уровень воды
initial_flood_level = 120  # Задайте начальный уровень воды

# Создание функции для обновления графиков
def update(flood_level):
    ax3d.clear()
    ax2d.clear()

    # Создание маски для затопленных областей
    flood_mask = altitude_grid <= flood_level

    # Определение цветов для 3D графика
    colors = np.empty(altitude_grid.shape, dtype=object)
    colors[flood_mask] = 'blue'   # Затопленные области
    colors[~flood_mask] = 'brown' # Суша

    # Визуализация поверхности местности в 3D
    surf = ax3d.plot_surface(latitude_grid, longitude_grid, altitude_grid, facecolors=colors, linewidth=0,
                             antialiased=False)

    # Добавление полупрозрачной плоскости уровня воды
    water_level = flood_level  # Уровень воды
    x_plane = latitude_grid
    y_plane = longitude_grid
    z_plane = np.full_like(latitude_grid, water_level)

    # Визуализация плоскости уровня воды
    ax3d.plot_surface(x_plane, y_plane, z_plane, color='cyan', alpha=0.3)

    # Настройки осей и заголовок для 3D графика
    ax3d.set_title('3D Карта Высот с учётом затопления (Уровень воды: {} м)'.format(flood_level))
    ax3d.set_xlabel('Широта')
    ax3d.set_ylabel('Долгота')
    ax3d.set_zlabel('Высота')

    # Установка лимитов по осям для лучшей визуализации
    ax3d.set_zlim(altitude_grid.min(), altitude_grid.max())

    # Настройка угла обзора
    ax3d.view_init(elev=45, azim=120)  # Угол обзора

    # Визуализация затопленных областей в 2D виде сверху
    # Преобразуем flood_mask для правильной ориентации в изображении
    flood_mask_image = np.flipud(flood_mask)

    # Отображение затопленных областей
    ax2d.imshow(flood_mask_image, cmap='Blues', extent=[
                longitudes.min(), longitudes.max(), latitudes.min(), latitudes.max()], aspect='auto')

    # Настройки осей и заголовок для 2D графика
    ax2d.set_title('Вид сверху затопленных областей (Уровень воды: {} м)'.format(flood_level))
    ax2d.set_xlabel('Долгота')
    ax2d.set_ylabel('Широта')

    plt.draw()

# Первоначальная отрисовка графиков
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
