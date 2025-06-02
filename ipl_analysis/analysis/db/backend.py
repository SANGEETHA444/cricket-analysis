from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.backends.base.features import BaseDatabaseFeatures
from django.db.backends.base.client import BaseDatabaseClient
from django.db.backends.base.creation import BaseDatabaseCreation
from django.db.backends.base.introspection import BaseDatabaseIntrospection
from django.db.backends.base.validation import BaseDatabaseValidation
from django.db.backends.base.operations import BaseDatabaseOperations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class DatabaseFeatures(BaseDatabaseFeatures):
    supports_transactions = False
    supports_timezones = False
    supports_microsecond_precision = False


class DatabaseOperations(BaseDatabaseOperations):
    compiler_module = "analysis.db.compiler"


class DatabaseClient(BaseDatabaseClient):
    pass


class DatabaseCreation(BaseDatabaseCreation):
    pass


class DatabaseIntrospection(BaseDatabaseIntrospection):
    pass


class DatabaseValidation(BaseDatabaseValidation):
    pass


class DatabaseSchemaEditor(BaseDatabaseSchemaEditor):
    pass


class DatabaseWrapper(BaseDatabaseWrapper):
    vendor = 'mongodb'
    display_name = 'MongoDB'
    
    Database = None
    
    features_class = DatabaseFeatures
    ops_class = DatabaseOperations
    client_class = DatabaseClient
    creation_class = DatabaseCreation
    introspection_class = DatabaseIntrospection
    validation_class = DatabaseValidation
    schema_editor_class = DatabaseSchemaEditor
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection = None
        self._client = None
        
    def get_connection_params(self):
        return {
            'host': self.settings_dict['CLIENT']['host']
        }
    
    def get_new_connection(self, conn_params):
        try:
            self._client = MongoClient(
                conn_params['host'],
                serverSelectionTimeoutMS=5000
            )
            self.connection = self._client.get_database()
            self.connection.list_collection_names()
            return self.connection
        except ConnectionFailure as e:
            raise Exception(f"Could not connect to MongoDB: {str(e)}")
    
    def init_connection_state(self):
        pass
    
    def close(self):
        if self._client:
            self._client.close()
            self._client = None
        self.connection = None
    
    def is_usable(self):
        try:
            self.connection.list_collection_names()
            return True
        except:
            return False
