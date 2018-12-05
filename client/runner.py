import asyncio
import os
import signal
import logging

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

from gmqtt import Client as MQTTClient
# import gmqtt

# gmqtt also compatibility with uvloop
import uvloop

from client.dao.queue import QueuePersister
from users.models import CustomMicroUser

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


STOP = asyncio.Event()

# client = MQTTClient(os.environ.get('MQTT_CLIENT_ID'))


def ask_exit(*args):
    STOP.set()


def after_get(user):
    logging.info('Got user: %s', user.get_full_name())
    return user


async def main(broker_host, token, loop):
    global MQTTClient, QueuePersister, CustomMicroUser, logging, after_get
    # from gmqtt import Client as MQTTClientCustom
    logging.info("Client ID %s", os.environ.get('MQTT_CLIENT_ID'))
    client = MQTTClient(os.environ.get('MQTT_CLIENT_ID'))

    # client.on_connect = on_connect
    # client.on_message = on_message
    # client.on_disconnect = on_disconnect
    # client.on_subscribe = on_subscribe

    client.set_auth_credentials(token, None)
    await client.connect(broker_host)

    queuePersist = QueuePersister(client, loop)
    user = await queuePersist.get(CustomMicroUser(pk=1), after_get)


    # client.publish('TEST/TIME', str(time.time()), qos=1)

    await STOP.wait()
    await client.disconnect()


# if __name__ == '__main__':
loop = asyncio.get_event_loop()

host = 'mqtt.flespi.io'

logging.info("Client token %s", os.environ.get('MQTT_CLIENT_TOKEN'))
token = os.environ.get('MQTT_CLIENT_TOKEN')

loop.add_signal_handler(signal.SIGINT, ask_exit)
loop.add_signal_handler(signal.SIGTERM, ask_exit)

loop.run_until_complete(main(host, token, loop))
