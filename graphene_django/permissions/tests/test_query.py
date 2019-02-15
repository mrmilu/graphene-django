# -*- coding: utf-8 -*-
# General imports
import pytest
import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType

# App imports
from ...tests.models import Reporter
from ..middleware import DjangoPermissionsMiddleware


class context(object):
    pass


pytestmark = pytest.mark.django_db


def test_should_query_field():
    r1 = Reporter(first_name="FOO", last_name="ABA", email='a@a.com')
    r1.save()

    class IsAuthenticated(object):
        @staticmethod
        def has_permission(context):
            return False

    class ReporterType(DjangoObjectType):
        class Meta:
            model = Reporter
            exclude_fields = ("first_name",)
            only_fields = ("id", "last_name", "email")
            permission_fields = {
                "email": [IsAuthenticated()]
            }
            interfaces = (Node,)

    class Query(graphene.ObjectType):
        reporter = graphene.Field(ReporterType)

        def resolve_reporter(self, info, **args):
            return Reporter.objects.first()

    query = """
            query ReporterQuery {
              reporter {
                id
                lastName
                email
              }
            }
        """

    schema = graphene.Schema(query=Query)
    result = schema.execute(
        query, context_value=context(), middleware=[DjangoPermissionsMiddleware()]
    )
    assert not result.errors
    assert result.data['reporter']['lastName'] == r1.last_name
    assert result.data['reporter']['email'] == ''


def test_django_objecttype_with_multiple_permissions_denied():
    r1 = Reporter(first_name="FOO", last_name="ABA", email='a@a.com')
    r1.save()

    class IsAuthenticated(object):
        @staticmethod
        def has_permission(context):
            return False

    class IsAllowed(object):
        @staticmethod
        def has_permission(context):
            # return context.user and context.user.is_authenticated
            return True

    class ReporterType(DjangoObjectType):
        class Meta:
            model = Reporter
            exclude_fields = ("first_name",)
            permission_fields = {
                "email": [IsAuthenticated(), IsAllowed()]
            }

    class Query(graphene.ObjectType):
        reporter = graphene.Field(ReporterType)

        def resolve_reporter(self, info, **args):
            return Reporter.objects.first()

    query = """
            query ReporterQuery {
              reporter {
                id
                lastName
                email
              }
            }
        """

    schema = graphene.Schema(query=Query)
    result = schema.execute(
        query, context_value=context(), middleware=[DjangoPermissionsMiddleware()]
    )

    assert not result.errors
    assert result.data['reporter']['lastName'] == r1.last_name
    assert result.data['reporter']['email'] == ''


def test_django_objecttype_with_permissions_allowed():
    r1 = Reporter(first_name="FOO", last_name="ABA", email='a@a.com')
    r1.save()

    class IsAuthenticated(object):
        @staticmethod
        def has_permission(context):
            return True

    class ReporterType(DjangoObjectType):
        class Meta:
            model = Reporter
            exclude_fields = ("first_name",)
            permission_fields = {
                "email": [IsAuthenticated()]
            }

    class Query(graphene.ObjectType):
        reporter = graphene.Field(ReporterType)

        def resolve_reporter(self, info, **args):
            return Reporter.objects.first()

    query = """
            query ReporterQuery {
              reporter {
                id
                lastName
                email
              }
            }
        """

    schema = graphene.Schema(query=Query)
    result = schema.execute(
        query, context_value=context(), middleware=[DjangoPermissionsMiddleware()]
    )

    assert not result.errors
    assert result.data['reporter']['lastName'] == r1.last_name
    assert result.data['reporter']['email'] == r1.email


def test_django_objecttype_with_multiple_permissions_allowed():
    r1 = Reporter(first_name="FOO", last_name="ABA", email='a@a.com')
    r1.save()

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

    class ReporterType(DjangoObjectType):
        class Meta:
            model = Reporter
            exclude_fields = ("first_name",)
            permission_fields = {
                "email": [IsAuthenticated(), IsAllowed()]
            }

    class Query(graphene.ObjectType):
        reporter = graphene.Field(ReporterType)

        def resolve_reporter(self, info, **args):
            return Reporter.objects.first()

    query = """
            query ReporterQuery {
              reporter {
                id
                lastName
                email
              }
            }
        """

    schema = graphene.Schema(query=Query)
    result = schema.execute(
        query, context_value=context(), middleware=[DjangoPermissionsMiddleware()]
    )

    assert not result.errors
    assert result.data['reporter']['lastName'] == r1.last_name
    assert result.data['reporter']['email'] == r1.email
