import logging

from singleton_decorator import singleton

from dao.dao import AbstractPersister
from users.models import CustomMicroUser

@singleton
class DatabasePersister(AbstractPersister):
    def __init__(self, driver=None, host=None):
        super().__init__(driver)
        logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
        self.assign_callbacks_for_client(self.driver)
        self.host = host

    async def connect(self):
        await self.driver.connect(self.host, )

    def create(self, object, callback=None):
        object.save()
        return self._process_result(object, callback)

    def update(self, object, callback):
        object.save()
        return self._process_result(object, callback)

    def delete(self, object, callback):
        object.delete()
        return self._process_result(object, callback)

    def get(self, deserialized, callback=None):
        logging.info("Received USEEERRR %s", deserialized)
        users = CustomMicroUser.objects.filter(pk=deserialized.object.pk)
        return self._process_result(users[0], callback)

    def assign_callbacks_for_client(self, client):
        def _on_connect(client, flags, rc, properties):
            client.subscribe(self.get_channel)
            logging.info('Connected and subscribed')

        def _on_message(client, topic, payload, qos, properties):
            logging.info('RECEIVED A MSG: %s. Properties: %s', payload, properties)
            if topic == self.get_channel:
                user = self.get(deserialized=self._deserialize_object(payload))
                client.publish(self.get_channel_response, self._serialize_object(user), qos=qos, user_property=('persist_hash', dict(properties['user_property'])['persist_hash']))
                logging.info("Published to the response: %s. Message: %s", self.get_channel_response, self._serialize_object(user))

        def _on_disconnect(client, packet, exc=None):
            logging.info('Disconnected')

        def _on_subscribe(client, mid, qos):
            logging.info('SUBSCRIBED %s', mid)

        client.on_connect = _on_connect
        client.on_message = _on_message
        client.on_disconnect = _on_disconnect
        client.on_subscribe = _on_subscribe

    def _process_result(self, object, callback):
        if callback is None:
            return object
        return callback(object)

