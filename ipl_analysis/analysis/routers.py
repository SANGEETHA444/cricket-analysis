class DatabaseRouter:
    """
    A router to control all database operations on models in the
    auth, contenttypes, and sessions applications.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth, contenttypes, and sessions models go to default (SQLite).
        """
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions']:
            return 'default'
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth, contenttypes, and sessions models go to default (SQLite).
        """
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions']:
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth, contenttypes, or sessions app is
        involved.
        """
        if obj1._meta.app_label in ['auth', 'contenttypes', 'sessions']:
            return True
        if obj2._meta.app_label in ['auth', 'contenttypes', 'sessions']:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth, contenttypes, and sessions apps only appear in the
        default database (SQLite).
        """
        if app_label in ['auth', 'contenttypes', 'sessions']:
            return db == 'default'
        return None

    def allow_query(self, model, **hints):
        """
        Allow queries for auth, contenttypes, and sessions models.
        """
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions']:
            return True
        return None

    def allow_syncdb(self, db, model):
        """
        Allow syncdb for auth, contenttypes, and sessions models.
        """
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions']:
            return True
        return None
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions']:
            return True
        return None

    def allow_syncdb(self, db, model):
        """
        Allow syncdb for auth, contenttypes, and sessions models.
        """
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions']:
            return True
        return None

    def allow_syncdb(self, db, model):
        """
        Allow syncdb for auth, contenttypes, and sessions models.
        """
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions']:
            return True
        return None
