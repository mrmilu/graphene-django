# -*- coding: utf-8 -*-
# General imports


# App imports

class DjangoPermissionsMiddleware(object):

    def resolve(self, next, root, info, **args):
        context = info.context
        for name, field in info.schema._query._meta.fields.items():
            for field_name, permissions in field._type._meta.permission_fields.items():
                if info.field_name == field_name:
                    for permission in permissions:
                        if not permission.has_permission(context):
                            return ''

        return next(root, info, **args)
