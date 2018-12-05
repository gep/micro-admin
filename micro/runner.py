import asyncio
import os
import signal
import logging

from gmqtt import Client as MQTTClient

# gmqtt also compatibility with uvloop
import uvloop

from dao.database import DatabasePersister
from users.models import CustomMicroUser

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

STOP = asyncio.Event()


def ask_exit(*args):
    STOP.set()


async def main(broker_host, token, loop):
    global MQTTClient, logging, DatabasePersister, STOP
    logging.info("Client ID %s", os.environ.get('MQTT_CLIENT_ID'))
    dbclient = MQTTClient(os.environ.get('MQTT_CLIENT_ID'))

    dbclient.set_auth_credentials(token, None)

    persister = DatabasePersister(dbclient, broker_host)
    await persister.connect()

    await STOP.wait()
    await dbclient.disconnect()


# if __name__ == '__main__':
loop = asyncio.get_event_loop()

host = 'mqtt.flespi.io'
token = os.environ.get('MQTT_CLIENT_TOKEN')

loop.add_signal_handler(signal.SIGINT, ask_exit)
loop.add_signal_handler(signal.SIGTERM, ask_exit)

loop.run_until_complete(main(host, token, loop))
