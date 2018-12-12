# -*- coding: utf-8 -*-
# General imports
from mock import patch

# App imports
from graphene_django.tests.test_types import with_local_registry
from .. import registry
from ..types import DjangoObjectType
from .models import Reporter as ReporterModel

registry.reset_global_registry()


class Reporter(DjangoObjectType):
    """Reporter description"""

    class Meta:
        model = ReporterModel


@with_local_registry
@patch("graphene_django.tests.models.Reporter.objects.get", return_value=Reporter(id=1))
def test_django_objecttype_with_permissions_denied(get):
    class Info(object):
        pass

    class IsAuthenticated(object):
        @staticmethod
        def has_permission(context):
            return False

    class Reporter(DjangoObjectType):
        class Meta:
            model = ReporterModel
            exclude_fields = ("first_name",)
            permission_fields = {
                "email": [IsAuthenticated()]
            }

    info = Info()
    info.context = Info()
    info.context.user = Info()

    reporter = Reporter.get_node(info, 1)
    get.assert_called_with(pk=1)
    assert reporter.id == 1

    fields = list(Reporter._meta.fields.keys())
    assert "email" not in fields
    assert "first_name" not in fields
    assert "id" in fields


@with_local_registry
@patch("graphene_django.tests.models.Reporter.objects.get", return_value=Reporter(id=1))
def test_django_objecttype_with_multiple_permissions_denied(get):
    class Info(object):
        pass

    class IsAuthenticated(object):
        @staticmethod
        def has_permission(context):
            return False

    class IsAllowed(object):
        @staticmethod
        def has_permission(context):
            # return context.user and context.user.is_authenticated
            return True

    class Reporter(DjangoObjectType):
        class Meta:
            model = ReporterModel
            exclude_fields = ("first_name",)
            permission_fields = {
                "email": [IsAuthenticated(), IsAllowed()]
            }

    info = Info()
    info.context = Info()
    info.context.user = Info()

    reporter = Reporter.get_node(info, 1)
    get.assert_called_with(pk=1)
    assert reporter.id == 1

    fields = list(Reporter._meta.fields.keys())
    assert "email" not in fields
    assert "first_name" not in fields
    assert "id" in fields


@with_local_registry
@patch("graphene_django.tests.models.Reporter.objects.get", return_value=Reporter(id=1))
def test_django_objecttype_with_permissions_allowed(get):
    class Info(object):
        pass

    class IsAuthenticated(object):
        @staticmethod
        def has_permission(context):
            # return context.user and context.user.is_authenticated
            return True

    class Reporter(DjangoObjectType):
        class Meta:
            model = ReporterModel
            exclude_fields = ("first_name",)
            permission_fields = {
                "email": [IsAuthenticated()]
            }

    info = Info()
    info.context = Info()
    info.context.user = Info()

    reporter = Reporter.get_node(info, 1)
    get.assert_called_with(pk=1)
    assert reporter.id == 1

    fields = list(Reporter._meta.fields.keys())
    assert "email" in fields
    assert "first_name" not in fields
    assert "id" in fields


@with_local_registry
@patch("graphene_django.tests.models.Reporter.objects.get", return_value=Reporter(id=1))
def test_django_objecttype_with_multiple_permissions_allowed(get):
    class Info(object):
        pass

    class IsAuthenticated(object):
        @staticmethod
        def has_permission(context):
            # return context.user and context.user.is_authenticated
            return True

    class IsAllowed(object):
        @staticmethod
        def has_permission(context):
            # return context.user and context.user.is_authenticated
            return True

    class Reporter(DjangoObjectType):
        class Meta:
            model = ReporterModel
            exclude_fields = ("first_name",)
            permission_fields = {
                "email": [IsAuthenticated(), IsAllowed()]
            }

    info = Info()
    info.context = Info()
    info.context.user = Info()

    reporter = Reporter.get_node(info, 1)
    get.assert_called_with(pk=1)
    assert reporter.id == 1

    fields = list(Reporter._meta.fields.keys())
    assert "email" in fields
    assert "first_name" not in fields
    assert "id" in fields
