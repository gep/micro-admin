import secrets
from abc import ABC, abstractmethod

from django.core import serializers


class AbstractPersister(ABC):
    qos_level = 2

    create_channel = 'customuser2/create/request'
    update_channel = 'customuser2/update/request'
    delete_cjannel = 'customuser2/delete/request'
    get_channel = 'customuser2/get/request'

    get_channel_response = 'customuser2/get/response'

    object_request_status_requested = 1
    object_request_status_responsed = 2

    def __init__(self, driver):
        self.driver = driver

    @abstractmethod
    def create(self, object, callback):
        pass

    @abstractmethod
    def update(self, object, callback):
        pass

    @abstractmethod
    def delete(self, object, callback):
        pass

    @abstractmethod
    def get(self, object, callback):
        pass

    def _serialize_object(self, object):
        return serializers.serialize("json", [object], fields=('name', 'get_persist_hash'))

    def _deserialize_object(self, data):
        for user in serializers.deserialize("json", data):
            return user

    def _generate_hash(self):
        return secrets.token_urlsafe(16)