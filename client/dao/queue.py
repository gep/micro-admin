import logging
import sys
sys.path.append('/usr/src/app')

import async_timeout as async_timeout

from dao.dao import AbstractPersister
from singleton_decorator import singleton
import asyncio

@singleton
class QueuePersister(AbstractPersister):
    def __init__(self, driver, loop=None):
        super().__init__(driver)
        self._get_requests = {}
        self._create_requests = {}
        self._delete_requests = {}
        self._update_requests = {}

        self._wait_timeout = 15
        self._async_sleep = 0.01

        logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)
        self.assign_callbacks_for_client(driver)
        self.driver.subscribe(self.get_channel_response)

        self.loop = loop

    def create(self, object, after):
        self.driver.publish(self.create_channel, self._serialize_object(object), qos=self.qos_level)
        self._create_requests[object.get_persist_hash] = self.object_request_status_requested

    def update(self, object, after):
        self.driver.publish(self.update_channel, self._serialize_object(object), qos=self.qos_level)
        self._update_requests[object.get_persist_hash] = self.object_request_status_requested

    def delete(self, object, after):
        self.driver.publish(self.delete_cjannel, self._serialize_object(object), qos=self.qos_level)
        self._delete_requests[object.get_persist_hash] = self.object_request_status_requested

    async def get(self, object, after):
        payload  = self._serialize_object(object)
        persist_hash = self._generate_hash()
        logging.info("Object hash: %s", persist_hash)
        self.driver.publish(self.get_channel, payload, qos=self.qos_level, user_property=('persist_hash', persist_hash))
        logging.info('Published to %s. Id: %s. Payload: %s', self.get_channel, object.id, payload)
        self._get_requests[persist_hash] = {'status': self.object_request_status_requested}
        return await self._wait('get', object, persist_hash, after)

    async def _wait(self, type, object, persist_hash, after):
        try:
            await asyncio.wait_for(self._get_object_from_response(type, object, persist_hash, after), timeout=self._wait_timeout)
        except asyncio.TimeoutError:
            logging.error("Timeout!")

    async def _get_object_from_response(self, type, object, persist_hash, after):
        got_response = False
        while not got_response:
            if type == 'get' and self._get_requests[persist_hash]['status'] == self.object_request_status_requested:
                await asyncio.sleep(self._async_sleep, loop=self.loop)
            else:
                got_response = True
                object = self._get_requests[persist_hash]['object']
        return after(object)

    def set_get_status(self, status, persist_hash, object):
        self._get_requests[persist_hash] = {'status': status, 'object': object}

    def assign_callbacks_for_client(self, client):
        def _on_connect(client, flags, rc, properties):
            logging.info('Client Connected')
            # client.subscribe('TEST/#', qos=0)

        def _on_message(client, topic, payload, qos, properties):
            logging.info('RECV MSG: %s. Properties: %s', payload, properties)
            if topic == self.get_channel_response:
                user = self._deserialize_object(payload)
                self.set_get_status(self.object_request_status_responsed, dict(properties['user_property'])['persist_hash'], user.object)

        def _on_disconnect(client, packet, exc=None):
            logging.info('Client Disconnected')

        def _on_subscribe(client, mid, qos):
            logging.info('Client Subscribed')

        client.on_connect = _on_connect
        client.on_message = _on_message
        client.on_disconnect = _on_disconnect
        client.on_subscribe = _on_subscribe