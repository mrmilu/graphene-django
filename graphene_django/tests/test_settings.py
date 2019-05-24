# -*- coding: utf-8 -*-
# General imports
from mock import patch
from pytest import raises

# App imports
import graphene_django.settings as settings


def test_perform_import_value_none_return_none():
    assert settings.perform_import(None, None) is None


def test_perform_import_value_integer_return_integer():
    assert settings.perform_import(1, None) == 1


def test_import_from_string_raise_error():
    with raises(ImportError) as excinfo:
        settings.import_from_string('x.x', 'y')

    assert "Could not import 'x.x' for Graphene setting 'y'" in str(excinfo.value)


@patch('graphene_django.settings.graphene_settings', None)
def test_reload_graphene_settings():
    settings.reload_graphene_settings(
        setting='GRAPHENE',
        value=None
    )
    assert isinstance(settings.graphene_settings, settings.GrapheneSettings)
