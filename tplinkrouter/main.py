import asyncio
import logging
import os
from argparse import ArgumentParser
from typing import Union

import aiomqtt

from tplinkrouter.mqtt import MQTTCommunicator
from tplinkrouter.telnet import TelnetCommunicator

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


def parse_log(log_level: Union[str, int]) -> int:
    if isinstance(log_level, int):
        return log_level
    elif isinstance(log_level, str):
        return eval(f'logging.{log_level}')
    else:
        raise ValueError(f'{log_level} is not a valid log level')

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
    parser.add_argument('--log_level', type=parse_log,
                        default=os.environ.get("LOG_LEVEL"),
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'])

    args = parser.parse_args()
    if args.log_level:
        logging.basicConfig()
        logging.getLogger().setLevel(args.log_level)
        logging.info(f'log level set to {logging.getLevelName(args.log_level)}')
    logging.info(f'Connecting to mqtt broker {args.mqtt_host}')
    telnet_communicator = TelnetCommunicator(
        username=args.tplink_username,
        password=args.tplink_password,
        host=args.tplink_host
    )
    await telnet_communicator.launch()
    client = aiomqtt.Client(
            hostname=args.mqtt_host,
            port=args.mqtt_port,
            username=args.mqtt_username,
            password=args.mqtt_password
    )
    mqtt_communicator = MQTTCommunicator(
        client=client,
        telnet_communicator=telnet_communicator
    )
    await asyncio.gather(
        mqtt_communicator.publish_state(),
        mqtt_communicator.listen_to_command(),
    )


if __name__ == '__main__':
    asyncio.run(launch())
