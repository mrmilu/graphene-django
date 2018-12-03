# -*- coding: utf-8 -*-
# 3rd Party imports
from graphene_django import DjangoObjectType
from graphene_django.decorators.permissions import Permissions
from graphene_django.tests.test_types import with_local_registry

# App imports
from .models import Reporter as ReporterModel


@with_local_registry
def test_django_objecttype_():
    def can_see_email():
        return False

    class Permission(object):
        fields = ['email']

        def has_permission(self):
            if can_see_email():
                return []
            return self.fields

    @Permissions(permissions_classes=[Permission])
    class Reporter(DjangoObjectType):
        class Meta:
            model = ReporterModel

    fields = list(Reporter._meta.fields.keys())
    assert "email" not in fields
