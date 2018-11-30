# -*- coding: utf-8 -*-
# Python imports
from unittest import TestCase

# Django imports

# 3rd Party imports

# App imports
from ..registry import Registry
from ..types import DjangoObjectType
from .models import Reporter


class TestSchema(TestCase):
    def test_should_raise_if_no_model(self):
        with self.assertRaises(Exception) as excinfo:
            class Character1(DjangoObjectType):
                pass

        exception = excinfo.exception
        self.assertRegex(str(exception), "valid Django Model")

    def test_should_raise_if_model_is_invalid(self):
        with self.assertRaises(Exception) as excinfo:
            class Character2(DjangoObjectType):
                class Meta:
                    model = 1

        exception = excinfo.exception
        self.assertRegex(str(exception), "valid Django Model")

    def test_should_map_fields_correctly(self):
        class ReporterType2(DjangoObjectType):
            class Meta:
                model = Reporter
                registry = Registry()

        fields = list(ReporterType2._meta.fields.keys())

        self.assertListEqual(fields[:-2], [
            "id",
            "first_name",
            "last_name",
            "email",
            "pets",
            "a_choice",
            "reporter_type",
        ])

        self.assertListEqual(sorted(fields[-2:]), ["articles", "films"])

    def test_should_map_only_few_fields(self):
        class Reporter2(DjangoObjectType):
            class Meta:
                model = Reporter
                only_fields = ("id", "email")

        self.assertListEqual(list(Reporter2._meta.fields.keys()), ["id", "email"])
