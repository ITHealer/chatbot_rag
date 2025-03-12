from src.utils.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from src.utils.config_loader import ConfigReaderInstance
from urllib.parse import quote_plus as urlquote
from src.helpers.singleton import SingletonMeta
from src.utils.logger.custom_logging import LoggerMixin
import psycopg2

db_config = ConfigReaderInstance.yaml.read_config_from_file(settings.DATABASE_CONFIG_FILENAME)
postgres_config = db_config.get('POSTGRES')

POSTGRES_CONNECTION_STRING = 'postgresql://{}:{}@{}:{}/{}'.format(postgres_config['USER'],
                                                                  urlquote(postgres_config['PASSWORD']),
                                                                  postgres_config['HOST'],
                                                                  postgres_config['PORT'],
                                                                  postgres_config['DATABASE_NAME'])
print(f"POSTGRES_CONNECTION_STRING {POSTGRES_CONNECTION_STRING}")
Base = declarative_base()


class DatabaseConection(LoggerMixin, metaclass=SingletonMeta):
    def __init__(self) -> None:
        super().__init__()
        self.engine = create_engine(POSTGRES_CONNECTION_STRING, echo=True)
        self.SessionLocal = sessionmaker(autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

def get_connection():
    return psycopg2.connect(POSTGRES_CONNECTION_STRING)

# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session
# from urllib.parse import quote_plus as urlquote

# from src.utils.config import settings
# from src.helpers.singleton import SingletonMeta
# from src.utils.logger.custom_logging import LoggerMixin
# from src.utils.config_loader import ConfigReaderInstance

# # Read configuration from YAML file
# db_config = ConfigReaderInstance.yaml.read_config_from_file(settings.DATABASE_CONFIG_FILENAME)

# # Get config
# postgres_config = db_config.get('POSTGRES')

# # URL connection to Database
# POSTGRES_CONNECTION_STRING = 'postgresql://{}:{}@{}:{}/{}'.format(
#     postgres_config['USER'],
#     urlquote(postgres_config['PASSWORD']),
#     postgres_config['HOST'],
#     postgres_config['PORT'],
#     postgres_config['DATABASE_NAME']
# )

# # Create Base object to declare ORM
# Base = declarative_base()

# # Manage connections to PostgreSQL.
# # Ensures that only one instance of this class exists throughout the program.
# class DatabaseConnection(LoggerMixin, metaclass=SingletonMeta):
#     def __init__(self) -> None:
#         super().__init__()
#         self.engine = create_engine(POSTGRES_CONNECTION_STRING, echo=True) # object connects to PostgreSQL.
#         self.SessionLocal = sessionmaker(autoflush=False, bind=self.engine)
#         Base.metadata.create_all(bind=self.engine) # SQLAlchemy will automatically create tables in the database.

#     # Returns a session to perform operations with the database.
#     def get_session(self) -> Session:
#         return self.SessionLocal()