# -*- coding: utf-8 -*-
# Python imports
from collections import OrderedDict

# Django imports
from django.shortcuts import get_object_or_404

# 3rd Party imports
from rest_framework.exceptions import ErrorDetail
import graphene
from graphene.types import Field, InputField
from graphene.types.mutation import MutationOptions
from graphene.relay.mutation import ClientIDMutation
from graphene.types.objecttype import yank_fields_from_attrs
from graphql import GraphQLError

# App imports
from graphene_django.rest_framework.types import ListErrorType
from .serializer_converter import convert_serializer_field


class SerializerMutationOptions(MutationOptions):
    lookup_field = None
    model_class = None
    model_operations = ["create", "update"]
    serializer_class = None


def fields_for_serializer(serializer, only_fields, exclude_fields, is_input=False):
    fields = OrderedDict()
    for name, field in serializer.fields.items():
        is_not_in_only = only_fields and name not in only_fields
        is_excluded = (
                              name
                              in exclude_fields  # or
                          # name in already_created_fields
                      ) or (
                              field.write_only and not is_input  # don't show write_only fields in Query
                      )

        if is_not_in_only or is_excluded:
            continue

        fields[name] = convert_serializer_field(field, is_input=is_input)
    return fields


class SerializerMutation(ClientIDMutation):
    class Meta:
        abstract = True

    errors = graphene.List(
        ListErrorType,
        description='May contain more than one error for same field.'
    )

    @classmethod
    def __init_subclass_with_meta__(
            cls,
            lookup_field=None,
            serializer_class=None,
            model_class=None,
            model_operations=["create", "update"],
            permission_classes=[],
            only_fields=(),
            exclude_fields=(),
            **options
    ):

        if not serializer_class:
            raise Exception("serializer_class is required for the SerializerMutation")

        if "update" not in model_operations and "create" not in model_operations:
            raise Exception('model_operations must contain "create" and/or "update"')

        serializer = serializer_class()
        if model_class is None:
            serializer_meta = getattr(serializer_class, "Meta", None)
            if serializer_meta:
                model_class = getattr(serializer_meta, "model", None)

        if lookup_field is None and model_class:
            lookup_field = model_class._meta.pk.name

        input_fields = fields_for_serializer(
            serializer, only_fields, exclude_fields, is_input=True
        )
        output_fields = fields_for_serializer(
            serializer, only_fields, exclude_fields, is_input=False
        )

        _meta = SerializerMutationOptions(cls)
        _meta.lookup_field = lookup_field
        _meta.model_operations = model_operations
        _meta.serializer_class = serializer_class
        _meta.model_class = model_class
        _meta.fields = yank_fields_from_attrs(output_fields, _as=Field)
        _meta.permission_classes = permission_classes

        input_fields = yank_fields_from_attrs(input_fields, _as=InputField)
        super(SerializerMutation, cls).__init_subclass_with_meta__(
            _meta=_meta, input_fields=input_fields, **options
        )

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        lookup_field = cls._meta.lookup_field
        model_class = cls._meta.model_class

        if model_class:
            if "update" in cls._meta.model_operations and lookup_field in input:
                instance = get_object_or_404(
                    model_class, **{lookup_field: input[lookup_field]}
                )
            elif "create" in cls._meta.model_operations:
                instance = None
            else:
                raise Exception(
                    'Invalid update operation. Input parameter "{}" required.'.format(
                        lookup_field
                    )
                )

            return {
                "instance": instance,
                "data": input,
                "context": {"request": info.context},
            }

        return {"data": input, "context": {"request": info.context}}

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        kwargs = cls.get_serializer_kwargs(root, info, **input)
        serializer = cls._meta.serializer_class(**kwargs)

        cls.check_permissions(kwargs)
        cls.check_object_permissions(kwargs, obj=kwargs.get('instance'))

        if serializer.is_valid():
            return cls.perform_mutate(serializer, info)
        else:
            errors = []
            for path, node in iterate_over_django_errors(serializer.errors):
                if isinstance(node, ErrorDetail):
                    errors.append(ListErrorType(field=path, message=node, code=node.code))
            return cls(errors=errors)

    @classmethod
    def perform_mutate(cls, serializer, info):
        obj = serializer.save()

        kwargs = {}
        for f, field in serializer.fields.items():
            if not field.write_only:
                kwargs[f] = field.get_attribute(obj)

        return cls(errors=None, **kwargs)

    @classmethod
    def get_permissions(cls):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        return [permission() for permission in cls._meta.permission_classes]

    @classmethod
    def check_permissions(cls, request):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in cls.get_permissions():
            if not permission.has_permission(request, cls):
                raise GraphQLError(message=getattr(permission, 'message', None))

    @classmethod
    def check_object_permissions(cls, request, obj):
        """
        Check if the request should be permitted for a given object.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in cls.get_permissions():
            if not permission.has_object_permission(request, cls, obj):
                raise GraphQLError(message=getattr(permission, 'message', None))


def iterate_over_django_errors(dict_or_list, path=[]):
    if isinstance(dict_or_list, dict):
        iterator = dict_or_list.items()
    else:
        iterator = enumerate(dict_or_list)
    for k, v in iterator:
        if isinstance(dict_or_list, list):
            if all(isinstance(item, ErrorDetail) for item in dict_or_list):
                yield path, v
            else:
                yield path + [k], v
        if isinstance(v, (dict, list)):
            for k, v in iterate_over_django_errors(v, path + [k]):
                yield k, v
