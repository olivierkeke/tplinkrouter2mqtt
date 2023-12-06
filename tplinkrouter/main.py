import asyncio
import os
from argparse import ArgumentParser

import aiomqtt

from tplinkrouter.mqtt import MQTTCommunicator
from tplinkrouter.telnet import TelnetCommunicator


async def launch():
    parser = ArgumentParser(
        prog='tplinkrouter2mqtt',
        description='Gateway between tplinkrouter (telnet) and mqtt'
    )
    parser.add_argument('--tplink_username', default=os.environ.get("TPLINK_USERNAME"))
    parser.add_argument('--tplink_password', default=os.environ.get("TPLINK_PASSWORD"))
    parser.add_argument('--tplink_host', default=os.environ.get("TPLINK_HOST"))
    parser.add_argument('--tplink_port', default=os.environ.get("TPLINK_PORT"))
    parser.add_argument('--broker-url', default=os.environ.get("BROKER_URL"))

    args = parser.parse_args()
    telnet_communicator = TelnetCommunicator(
        username=args.tplink_username,
        password=args.tplink_password,
        host=args.tplink_host
    )
    async with aiomqtt.Client(args.broker_url) as client:
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
