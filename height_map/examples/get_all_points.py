from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Настройки подключения
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
    
    for row in rows:
        print(f"ID: {row.id}, Latitude: {row.latitude}, Longitude: {row.longitude}, Altitude: {row.altitude}")

get_all_points()

session.shutdown()
cluster.shutdown()
