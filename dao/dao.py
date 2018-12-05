import secrets
from abc import ABC, abstractmethod

from django.core import serializers


class AbstractPersister(ABC):
    qos_level = 2

    create_channel = 'customuser/create/request'
    update_channel = 'customuser/update/request'
    delete_cjannel = 'customuser/delete/request'
    get_channel = 'customuser/get/request'

    get_channel_response = 'customuser/get/response'

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
        object.set_persist_hash(secrets.token_urlsafe(16))
        return serializers.serialize("json", [object], fields=('id', 'name', '_persist_hash'))

    def _deserialize_object(self, data):
        for user in serializers.deserialize("json", data):
            return user

