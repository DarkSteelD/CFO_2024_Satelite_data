import uuid
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from tqdm import tqdm
import time

# Настройки подключения к Cassandra
CASSANDRA_HOST = 'localhost'
CASSANDRA_PORT = 9042
USERNAME = 'cassandra'
PASSWORD = 'cassandra'

auth_provider = PlainTextAuthProvider(username=USERNAME, password=PASSWORD)
cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT, auth_provider=auth_provider)
session = cluster.connect('geo_data')

# Подготовленный запрос для ускорения записи
prepared_statement = session.prepare("INSERT INTO coordinates (id, latitude, longitude, altitude) VALUES (?, ?, ?, ?)")

# Функция для генерации случайной точки на поверхности Земли с высотой
def generate_random_point():
    latitude = random.uniform(-90, 90)
    longitude = random.uniform(-180, 180)
    altitude = random.uniform(0, 9000)  # Высота от 0 до 9000 метров (9 км)
    point_id = uuid.uuid4()
    return (point_id, latitude, longitude, altitude)

# Функция для записи одной точки в Cassandra
def insert_point_into_cassandra(point):
    try:
        session.execute(prepared_statement, point)
    except Exception as e:
        print(f"Ошибка записи: {e}")

# Параметры генерации
num_points = 566738302122  # Уменьшено количество точек для теста
max_workers = 10  # Количество потоков для параллельной загрузки

# Загрузка данных с использованием пула потоков
def upload_data():
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = (executor.submit(insert_point_into_cassandra, generate_random_point()) for _ in range(num_points))
        
        with tqdm(desc="Загрузка данных") as pbar:
            for _ in futures:
                pbar.update(1)

start_time = time.time()
upload_data()
end_time = time.time() 


elapsed_time = (end_time - start_time) / 60  # Переводим секунды в минуты
print(f"Загрузка данных завершена. Время выполнения: {elapsed_time:.2f} минут.")

# Закрываем соединение после завершения работы
cluster.shutdown()
session.shutdown()
