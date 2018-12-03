# -*- coding: utf-8 -*-
# imports


class Permissions(object):

    def __init__(self, permissions_classes):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        self.excluded_fields = []
        for permission in permissions_classes:
            self.excluded_fields.append(*permission().has_permission())

        self.excluded_fields = set(self.excluded_fields)

    def exclude_fields(self, meta):
        excluded = meta.exclude_fields if 'exclude_fields' in meta.__dict__ else ()
        return list(self.excluded_fields | set(excluded))

    def __call__(self, cls):
        class Wrapper(cls):
            class Meta:
                model = cls._meta.model
                registry = cls._meta.registry
                skip_registry = cls._meta.skip_registry if 'skip_registry' in cls._meta.__dict__ else None
                only_fields = cls._meta.only_fields if 'only_fields' in cls._meta.__dict__ else ()
                exclude_fields = self.exclude_fields(cls._meta)
                filter_fields = cls._meta.filter_fields
                connection = cls._meta.connection
                connection_class = cls._meta.connection_class if 'connection_class' in cls._meta.__dict__ else None
                use_connection = cls._meta.use_connection if 'use_connection' in cls._meta.__dict__ else None
                interfaces = cls._meta.interfaces

        return Wrapper
