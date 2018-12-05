import logging

from singleton_decorator import singleton

from dao.dao import AbstractPersister
from users.models import CustomMicroUser

@singleton
class DatabasePersister(AbstractPersister):
    def __init__(self, driver=None):
        super().__init__(driver)
        self.assign_callbacks_for_client(driver)
        self.driver.subscribe(self.get_channel)
        logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

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
            logging.info('Connected')
            # client.subscribe('TEST/#', qos=0)

        def _on_message(client, topic, payload, qos, properties):
            logging.info('RECV MSG: %s', payload)
            if topic == self.get_channel:
                user = self.get(deserialized=self._deserialize_object(payload))
                client.publish(self.get_channel_response, self._serialize_object(user), qos=qos)
                logging.info("Published to the response: %s. Message: %s", self.get_channel_response, self._serialize_object(user))

        def _on_disconnect(client, packet, exc=None):
            logging.info('Disconnected')

        def _on_subscribe(client, mid, qos):
            logging.info('SUBSCRIBED')

        client.on_connect = _on_connect
        client.on_message = _on_message
        client.on_disconnect = _on_disconnect
        client.on_subscribe = _on_subscribe

    def _process_result(self, object, callback):
        if callback is None:
            return object
        return callback(object)

