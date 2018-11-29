# -*- coding: utf-8 -*-
# Python imports
from unittest import TestCase, mock, skip

# Django imports

# 3rd Party imports

# App imports
from ..settings import perform_import, import_from_string, reload_graphene_settings, GrapheneSettings, graphene_settings


class TestSettings(TestCase):
    def test_perform_import_value_none_return_none(self):
        self.assertIsNone(perform_import(None, None))

    def test_perform_import_value_integer_return_integer(self):
        self.assertEqual(perform_import(1, None), 1)

    def test_import_from_string_raise_error(self):
        with self.assertRaises(ImportError) as context:
            import_from_string('x.x', 'y')

        exception = context.exception

        self.assertRegex(exception.msg, "Could not import 'x.x' for Graphene setting 'y'")

    @skip
    @mock.patch('graphene_django.settings.graphene_settings', None)
    def test_reload_graphene_settings(self):
        reload_graphene_settings(
            setting='GRAPHENE',
            value='A'
        )
        self.assertIsInstance(graphene_settings, GrapheneSettings)
