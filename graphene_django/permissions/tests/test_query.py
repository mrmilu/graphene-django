# -*- coding: utf-8 -*-
# General imports
import datetime

import pytest
import graphene
from graphene.relay import Node
from graphene_django import DjangoObjectType, DjangoConnectionField

# App imports
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.utils import DJANGO_FILTER_INSTALLED
from ...tests.models import Reporter, Pet, Film, Article
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


def test_django_objecttype_with_int_choice_denied_field():
    r1 = Reporter(first_name="FOO", last_name="ABA", email='a@a.com', reporter_type=1)
    r1.save()

    class IsAuthenticated(object):
        @staticmethod
        def has_permission(context):
            return False

    class ReporterType(DjangoObjectType):
        class Meta:
            model = Reporter
            exclude_fields = ("first_name",)
            permission_fields = {
                "reporter_type": [IsAuthenticated()]
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
                reporterType
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
    assert result.data['reporter']['reporterType'] is None


def test_django_objecttype_with_int_denied_field():
    r1 = Pet(age=10, name="ABA")
    r1.save()

    class IsAuthenticated(object):
        @staticmethod
        def has_permission(context):
            return False

    class PetType(DjangoObjectType):
        class Meta:
            model = Pet
            permission_fields = {
                "age": [IsAuthenticated()]
            }

    class Query(graphene.ObjectType):
        pet = graphene.Field(PetType)

        def resolve_pet(self, info, **args):
            return Pet.objects.first()

    query = """
            query PetQuery {
              pet {
                id
                name
                age
              }
            }
        """

    schema = graphene.Schema(query=Query)
    result = schema.execute(
        query, context_value=context(), middleware=[DjangoPermissionsMiddleware()]
    )

    assert not result.errors
    assert result.data['pet']['name'] == r1.name
    assert result.data['pet']['age'] == 0


#
# @pytest.mark.skipif(
#     not DJANGO_FILTER_INSTALLED, reason="django-filter should be installed"
# )
def test_django_objecttype_with_annidated_denied_field():
    class IsAuthenticated(object):
        @staticmethod
        def has_permission(context):
            return False

    class ReporterType(DjangoObjectType):
        class Meta:
            model = Reporter
            exclude_fields = ("first_name",)
            interfaces = (Node,)
            permission_fields = {
                "reporter_type": [IsAuthenticated()]
            }

    class ArticleType(DjangoObjectType):
        class Meta:
            model = Article
            interfaces = (Node,)
            filter_fields = ("lang",)

    class Query(graphene.ObjectType):
        all_reporters = DjangoConnectionField(ReporterType)

    r = Reporter.objects.create(
        first_name="John", last_name="Doe", email="johndoe@example.com", a_choice=1
    )
    Article.objects.create(
        headline="Article Node 1",
        pub_date=datetime.date.today(),
        pub_date_time=datetime.datetime.now(),
        reporter=r,
        editor=r,
        lang="es",
    )
    Article.objects.create(
        headline="Article Node 2",
        pub_date=datetime.date.today(),
        pub_date_time=datetime.datetime.now(),
        reporter=r,
        editor=r,
        lang="en",
    )

    schema = graphene.Schema(query=Query)
    query = """
        query NodeFilteringQuery {
            allReporters {
                edges {
                    node {
                        id
                        email
                        articles(lang: "es") {
                            edges {
                                node {
                                    id
                                }
                            }
                        }
                    }
                }
            }
        }
    """

    expected = {
        "allReporters": {
            "edges": [
                {
                    "node": {
                        "id": "UmVwb3J0ZXJUeXBlOjE=",
                        "email": "",
                        "articles": {
                            "edges": [{"node": {"id": "QXJ0aWNsZVR5cGU6MQ=="}}]
                        },
                    }
                }
            ]
        }
    }

    result = schema.execute(query, context_value=context(), middleware=[DjangoPermissionsMiddleware()])
    assert not result.errors
    assert result.data['allReporters']['edges'][0]['node']['email'] == ""
