from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings

from .action import CreateActionMixin
from .actionable import CreateActionableMixin

from tbs_core_db.models import AttributeGroup, Attribute

import logging
class CreateModelMixin:
    def perform_create(self, serializer, attribute_group):
        return serializer.save(attribute_group=attribute_group)

    def create(self, request, *args, **kwargs):
        attribute_group = AttributeGroup.objects.get(pk=kwargs['attribute_group_pk'])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_attribute = self.perform_create(serializer, attribute_group)
        new_actionable = self.create_actionable(new_attribute)
        self.create_action(new_actionable, "create",  "AttributeAction",user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class UpdateModelMixin(update_mixin.UpdateModelMixin):
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        new_action = self.create_actionable(instance)
        self.create_action(new_action, "update",  "AttributeAction",user=request.user)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response({"sku": "update successfully"}, status=status.HTTP_200_OK)

class DestroyModelMixin(delete_mixin.DestroyModelMixin):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        self.remove_attribute_sku(instance)
        new_actionable = self.create_actionable(instance)
        self.create_action(new_actionable, "delete", "AttributeAction",user=request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def remove_attribute_sku(self, instance):
        instance.sku_set.clear()