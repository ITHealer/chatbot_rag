import psycopg2
from urllib.parse import quote_plus as urlquote

from src.utils.config import settings
from src.utils.config_loader import ConfigReaderInstance


# Read configuration from YAML file
db_config = ConfigReaderInstance.yaml.read_config_from_file(settings.DATABASE_CONFIG_FILENAME)

# Get config
postgres_config = db_config.get('POSTGRES')

# URL connection to Database
POSTGRES_CONNECTION_STRING = 'postgresql://{}:{}@{}:{}/{}'.format(
    postgres_config['USER'],
    urlquote(postgres_config['PASSWORD']),
    postgres_config['HOST'],
    postgres_config['PORT'],
    postgres_config['DATABASE_NAME']
)
print(f"POSTGRES_CONNECTION_STRING {POSTGRES_CONNECTION_STRING}")

# The Repository class acts as a layer to query data from the database.
class Repository:
    def __init__(self):
        pass

    @staticmethod
    def create_connection():
        # from src.utils.config import settings
        POSTGRESQL_URI = POSTGRES_CONNECTION_STRING
        return psycopg2.connect(POSTGRESQL_URI)
