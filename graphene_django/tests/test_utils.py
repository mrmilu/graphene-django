# -*- coding: utf-8 -*-
# general imports
import mock
from pytest import raises

# App imports
from ..utils import get_model_fields, import_single_dispatch
from .models import Film, Reporter


def test_get_model_fields_no_duplication():
    reporter_fields = get_model_fields(Reporter)
    reporter_name_set = set([field[0] for field in reporter_fields])
    assert len(reporter_fields) == len(reporter_name_set)

    film_fields = get_model_fields(Film)
    film_name_set = set([field[0] for field in film_fields])
    assert len(film_fields) == len(film_name_set)


def test_import_single_dispatch_raise_exception():
    modules = {
        'functools': None
    }

    module_patcher = mock.patch.dict('sys.modules', modules)
    module_patcher.start()
    with raises(Exception) as excinfo:
        single_dispatch = import_single_dispatch()

    assert "Please install the 'singledispatch'" in str(excinfo.value)
    module_patcher.stop()
