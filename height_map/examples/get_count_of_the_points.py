from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

CASSANDRA_HOST = 'localhost'
CASSANDRA_PORT = 9042
USERNAME = 'cassandra'
PASSWORD = 'cassandra'

auth_provider = PlainTextAuthProvider(username=USERNAME, password=PASSWORD)
cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT, auth_provider=auth_provider)
session = cluster.connect('geo_data')

from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement

def get_count_points():
    query = SimpleStatement("SELECT COUNT(*) FROM coordinates;", consistency_level=ConsistencyLevel.ONE)
    result = session.execute(query)
    
    for row in result:
        print("Total points count:", row[0])

get_count_points()
