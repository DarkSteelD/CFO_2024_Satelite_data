from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

CASSANDRA_HOST = 'localhost'
CASSANDRA_PORT = 9042
USERNAME = 'cassandra'
PASSWORD = 'cassandra'

auth_provider = PlainTextAuthProvider(username=USERNAME, password=PASSWORD)
cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT, auth_provider=auth_provider)
session = cluster.connect()

def setup_cassandra():
    session.execute("""
    CREATE KEYSPACE IF NOT EXISTS geo_data
    WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1}
    """)
    session.set_keyspace('geo_data')
    session.execute("""
    CREATE TABLE IF NOT EXISTS coordinates (
        id UUID PRIMARY KEY,
        latitude float,
        longitude float,
        altitude float
    )
    """)
    print("Keyspace и таблица созданы успешно.")

setup_cassandra()

session.shutdown()
cluster.shutdown()
