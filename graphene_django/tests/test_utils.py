# -*- coding: utf-8 -*-
# Python imports
from unittest import TestCase, mock

# Django imports

# 3rd Party imports

# App imports
from ..utils import get_model_fields, import_single_dispatch
from .models import Film, Reporter


class TestUtils(TestCase):

    def test_get_model_fields_no_duplication(self):
        reporter_fields = get_model_fields(Reporter)
        reporter_name_set = set([field[0] for field in reporter_fields])
        self.assertEqual(len(reporter_fields), len(reporter_name_set))

        film_fields = get_model_fields(Film)
        film_name_set = set([field[0] for field in film_fields])
        self.assertEqual(len(film_fields), len(film_name_set))

    def test_import_single_dispatch_raise_Exception(self):
        modules = {
            'functools': None
        }

        self.module_patcher = mock.patch.dict('sys.modules', modules)
        self.module_patcher.start()
        with self.assertRaises(Exception) as context:
            single_dispatch = import_single_dispatch()

        exception = context.exception

        self.assertRegex(str(exception), "Please install the 'singledispatch'")
        self.module_patcher.stop()
