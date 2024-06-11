################################################################################
############# Written by ChatGPT and tweaked By Jacob.h.Barrow #################
################################################################################
import importlib
import inspect

class ModelLoaderMeta(type):
    models = {}

    def __new__(cls, name, bases, attrs, module_name=None):
        new_class = super().__new__(cls, name, bases, attrs)
        if module_name:
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if hasattr(obj, '__tablename__'):
                    cls.models[obj.__name__] = obj
        return new_class

class QueryBuilder(metaclass=ModelLoaderMeta):
    def __init__(self, session, module_name='models', **kwargs):
        self.session = session
        
        if module_name:
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if hasattr(obj, '__tablename__'):
                    ModelLoaderMeta.models[obj.__name__] = obj

        for key, value in kwargs.items():
            if key in ModelLoaderMeta.models:
                setattr(self, key, ModelLoaderMeta.models[key])
            else:
                raise ValueError(f"Model {key} not found in module {module_name}")
        
    def get_table(self, table: str):
        return ModelLoaderMeta.models[table]

    def build_insert(self, insert_data):
        inserts = []
        for key, value in insert_data.items():
            table = self.get_table(value['TABLE'])
            values = value['VALUES']
            inserts.append(table(**values))

        return inserts

    def build_select(self, select_data):
        queries = {}
        
        for key, value in select_data.items():
            table = self.get_table(value['TABLE'])
            filters = value['FILTER']
            returning = value['RETURNING']
            
            query = self.session.query(table)
            for attr in filters:
                query = query.filter(getattr(table, attr) == filters[attr])
            query = query.with_entities(*[getattr(table, attr) for attr in returning[0]['Attributes']])
            queries[key] = query
            
        return queries

    def execute(self, query_json):
        # Handle inserts
        try:
            results = {}
            
            if 'INSERT' in query_json:
                insert_data = query_json['INSERT']
                insert_queries = self.build_insert(insert_data)
                for query in insert_queries:
                    self.session.add(query)
                self.session.commit()

            if 'SELECT' in query_json:
                select_data = query_json['SELECT']
                select_queries = self.build_select(select_data)
                for key, query in select_queries.items():
                    results[key] = query.all()
                    
            return results
            
        except:
            print(f'Failed: {query_json}')

################################################################################
############# Written by ChatGPT and tweaked By Jacob.h.Barrow #################
################################################################################

if __name__ == "__main__":
    import datetime
    import uuid
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine

    engine = create_engine('sqlite:///./events.db', echo=False)  # Replace with your actual database URL
    Session = sessionmaker(bind=engine)
    session = Session()

    query_json = {
       'INSERT': {
            'user_insertion': {
                'TABLE': 'User',
                'VALUES': {'username': 'Jarvis'},
                'REJECTS': ['id', 'created', 'updated'],
                'RETURNING': False,
            },
            'event_insertion': {
                'TABLE': 'Event',
                'VALUES': {'title': 'Hello World', 'date': datetime.datetime.now(), 'user_id': uuid.UUID('97111a05296b4aa198aa678ab8361737')},
                'REJECTS': ['id', 'created', 'updated'],
                'RETURNING': [{'TABLE': 'User', 'Attributes': ['id']}]
            }
        },
        'SELECT': {
            'select_user_by_id': {
                'TABLE': 'User',
                'FILTER': {'id': uuid.UUID('97111a05296b4aa198aa678ab8361737')},
                'RETURNING': [{'TABLE': 'User', 'Attributes': ['id', 'username']}]
            },
            'select_event_by_id': {
                'TABLE': 'Event',
                'FILTER': {'title': 'Birth', 'user_id': uuid.UUID('3354087c5fcb4ab6960e3b7744e59cb2')},
                'RETURNING': [{'TABLE': 'Event', 'Attributes': ['title', 'date', 'user_id']}]
            }
        }
    }

    qb = QueryBuilder(session)
    result = qb.execute(query_json)
    print(result)
