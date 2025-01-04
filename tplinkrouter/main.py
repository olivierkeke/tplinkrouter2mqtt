import asyncio
import logging

import aiomqtt
from typing import Union

from tplinkrouter.mqtt import TpLinkRouterToMQTTCommunicator
from tplinkrouter.telnet import TelnetCommunicator
from tplinkrouter.settings import Settings


def parse_log(log_level: Union[str, int]) -> int:
    if isinstance(log_level, int):
        return log_level
    elif isinstance(log_level, str):
        return eval(f'logging.{log_level}')
    else:
        raise ValueError(f'{log_level} is not a valid log level')


async def launch():
    settings = Settings()
    logging.basicConfig()
    logging.getLogger().setLevel(parse_log(settings.log_level))
    logging.info('Connecting to mqtt broker %s', settings.mqtt.host)
    telnet_communicator = TelnetCommunicator(
        username=settings.tplink.username,
        password=settings.tplink.password,
        host=settings.tplink.host,
        port=settings.tplink.port
    )
    client = aiomqtt.Client(
                hostname=settings.mqtt_host,
                port=settings.mqtt_port,
                username=settings.mqtt_username,
                password=settings.mqtt_password
        )
    mqtt_communicator = TpLinkRouterToMQTTCommunicator(
        client=client,
        telnet_communicator=telnet_communicator
    )
    while True:
        try:
            logging.info("launching MQTT listening and publishing task")
            async with mqtt_communicator:
                await asyncio.gather(
                    mqtt_communicator.publish_state(),
                    mqtt_communicator.listen_to_command(),
                )
            logging.info("MQTT listening and publishing task terminated")
        except:
            logging.warning("Connection to telnet or mqtt server lost; Reconnecting in %i seconds ...", settings.delay_before_reconnection)
            await asyncio.sleep(settings.delay_before_reconnection)


if __name__ == '__main__':
    asyncio.run(launch())
