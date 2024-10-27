from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

CASSANDRA_HOST = 'localhost'
CASSANDRA_PORT = 9042
USERNAME = 'cassandra'
PASSWORD = 'cassandra'

auth_provider = PlainTextAuthProvider(username=USERNAME, password=PASSWORD)
cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT, auth_provider=auth_provider)
session = cluster.connect('geo_data')

def get_points_above_altitude(min_altitude):
    query = "SELECT id, latitude, longitude, altitude FROM coordinates WHERE altitude > ? ALLOW FILTERING"
    prepared = session.prepare(query)
    rows = session.execute(prepared, (min_altitude,))
    
    for row in rows:
        print(f"ID: {row.id}, Latitude: {row.latitude}, Longitude: {row.longitude}, Altitude: {row.altitude}")

min_altitude = 100  # Высота для фильтрации
get_points_above_altitude(min_altitude)

session.shutdown()
cluster.shutdown()
