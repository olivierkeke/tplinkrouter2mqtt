import asyncio
import logging
import os
from argparse import ArgumentParser

import aiomqtt

from tplinkrouter.mqtt import MQTTCommunicator
from tplinkrouter.telnet import TelnetCommunicator

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


async def launch():
    parser = ArgumentParser(
        prog='tplinkrouter2mqtt',
        description='Gateway between tplinkrouter (telnet) and mqtt'
    )
    parser.add_argument('--tplink_username', default=os.environ.get("TPLINK_USERNAME"))
    parser.add_argument('--tplink_password', default=os.environ.get("TPLINK_PASSWORD"))
    parser.add_argument('--tplink_host', default=os.environ.get("TPLINK_HOST"))
    parser.add_argument('--tplink_port', default=os.environ.get("TPLINK_PORT"))
    parser.add_argument('--mqtt_host', default=os.environ.get("MQTT_HOST"))
    parser.add_argument('--mqtt_port', type=int, default=os.environ.get("MQTT_PORT"))
    parser.add_argument('--mqtt_username', default=os.environ.get("MQTT_USERNAME"))
    parser.add_argument('--mqtt_password', default=os.environ.get("MQTT_PASSWORD"))

    args = parser.parse_args()
    logging.info(f'Connecting to mqtt broker {args.mqtt_host}')
    telnet_communicator = TelnetCommunicator(
        username=args.tplink_username,
        password=args.tplink_password,
        host=args.tplink_host
    )
    async with aiomqtt.Client(
            hostname=args.mqtt_host,
            port=args.mqtt_port,
            username=args.mqtt_username,
            password=args.mqtt_password
    ) as client:
        mqtt_communicator = MQTTCommunicator(
            client=client,
            state_message_queue=telnet_communicator.state_message_queue,
            command_messsage_queue=telnet_communicator.command_messsage_queue
        )
        await mqtt_communicator.hass_discovery()
        await asyncio.gather(
            telnet_communicator.run(),
            mqtt_communicator.publish_state(),
            mqtt_communicator.listen_to_command(),
            )


if __name__ == '__main__':
    asyncio.run(launch())
