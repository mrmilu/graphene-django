# -*- coding: utf-8 -*-
# General imports


# App imports
from graphene.utils.str_converters import to_camel_case


class DjangoPermissionsMiddleware(object):

    def resolve(self, next, root, info, **args):
        context = info.context
        for name, field in info.schema._query._meta.fields.items():
            for field_name, permissions in field._type._meta.permission_fields.items():
                if info.field_name == to_camel_case(field_name):
                    for permission in permissions:
                        if not permission.has_permission(context) and root is not None:
                            if root._meta.get_field(field_name).null:
                                return None
                            if type(getattr(root, field_name)) == str:
                                return ''
                            if type(getattr(root, field_name)) == int:
                                return 0
                            return None

        return next(root, info, **args)
