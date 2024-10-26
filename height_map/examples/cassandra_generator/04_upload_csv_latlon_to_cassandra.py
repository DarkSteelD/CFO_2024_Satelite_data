import pandas as pd
import uuid
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider


CASSANDRA_HOST = 'localhost'
CASSANDRA_PORT = 9042
USERNAME = 'cassandra'
PASSWORD = 'cassandra'


auth_provider = PlainTextAuthProvider(username=USERNAME, password=PASSWORD)
cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT, auth_provider=auth_provider)
session = cluster.connect('geo_data')


def load_data_to_cassandra(csv_file_path):
    data = pd.read_csv(csv_file_path)

    if not {'latitude', 'longitude', 'altitude'}.issubset(data.columns):
        raise ValueError("CSV файл должен содержать колонки: latitude, longitude, altitude")


    insert_query = """
    INSERT INTO coordinates (id, latitude, longitude, altitude)
    VALUES (?, ?, ?, ?)
    """

    prepared = session.prepare(insert_query)

    for _, row in data.iterrows():
        session.execute(prepared, (uuid.uuid4(), row['latitude'], row['longitude'], row['altitude']))

    print("Данные успешно загружены в Cassandra.")


csv_file_path = './heightmap_3d_points.csv'
load_data_to_cassandra(csv_file_path)


session.shutdown()
cluster.shutdown()
