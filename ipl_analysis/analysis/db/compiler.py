from django.db.backends.utils import CursorDebugWrapper
from django.db.backends.base.compiler import SQLCompiler

class SQLCompiler(SQLCompiler):
    pass

class SQLInsertCompiler(SQLCompiler):
    pass

class SQLDeleteCompiler(SQLCompiler):
    pass

class SQLUpdateCompiler(SQLCompiler):
    pass

class SQLAggregateCompiler(SQLCompiler):
    pass
