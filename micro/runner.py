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


# async def main(broker_host, token):
#     client = MQTTClient('asdfghjk')
#     client.on_message = client_id
#     client.on_connect = on_connect
#     client.set_auth_credentials(token, None)
#     await client.connect(broker_host, 1883, keepalive=60)
#     client.publish(TOPIC, 'Message payload', response_topic='RESPONSE/TOPIC')
#
#     await STOP.wait()
#     await client.disconnect()



async def main(broker_host, token, loop):
    global MQTTClient, logging, DatabasePersister, STOP
    dbclient = MQTTClient(os.environ.get('MQTT_CLIENT_ID'))

    # dbclient.on_connect = on_connect
    # dbclient.on_message = on_message
    # dbclient.on_disconnect = on_disconnect
    # dbclient.on_subscribe = on_subscribe

    dbclient.set_auth_credentials(token, None)
    await dbclient.connect(broker_host)

    queuePersist = DatabasePersister(dbclient)
    # user = await queuePersist.get(DjangoUser(id=1), after_get)


    # client.publish('TEST/TIME', str(time.time()), qos=1)

    await STOP.wait()
    await dbclient.disconnect()


# if __name__ == '__main__':
loop = asyncio.get_event_loop()

host = 'mqtt.flespi.io'
token = os.environ.get('MQTT_CLIENT_TOKEN')

loop.add_signal_handler(signal.SIGINT, ask_exit)
loop.add_signal_handler(signal.SIGTERM, ask_exit)

loop.run_until_complete(main(host, token, loop))
