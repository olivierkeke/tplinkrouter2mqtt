import asyncio
import json
import logging
from asyncio import QueueFull
from dataclasses import dataclass
from typing import Dict

import aiomqtt

from .telnet import TelnetCommunicator
from .tplink_config import WIFI_ON_CMD, WIFI_OFF_CMD, QSS_ON_CMD, QSS_OFF_CMD


@dataclass
class MQTTCommunicator:

    telnet_communicator: TelnetCommunicator
    client: aiomqtt.Client
    discovery_prefix = 'homeassistant'

    async def publish_state(self):
        while True:
            wifi_state = await self.telnet_communicator.state_message_queue.get()
            payload = json.dumps(wifi_state)
            await self.client.publish("tplinkrouter/wifi", payload=payload)
            logging.debug(f'sent message to mqtt with payload: {payload}')

    async def listen_to_command(self):
        async with self.client.messages() as messages:
            await self.client.subscribe("tplinkrouter/wifi/set")
            async for message in messages:
                logging.debug(f'received command with payload: {message.payload}')
                try:
                    self.telnet_communicator.command_messsage_queue.put_nowait(message.payload)
                except QueueFull:
                    logging.warning('Command message queue is full')

    async def hass_discovery(self):
        device = {
            "name": f'TPLink {self.telnet_communicator.serial}',
            "model": f'tplink_{self.telnet_communicator.serial}',
            "identifiers": [
                self.telnet_communicator.serial
            ],
            "manufacturer": "TPlink"
        }
        hass_discovery_switch = {
            "name": "wifi",
            "state_topic": "tplinkrouter/wifi",
            "command_topic": "tplinkrouter/wifi/set",
            "unique_id": "wifi_switch",
            "value_template": "{{ value_json.Status }}",
            "state_on": "Up",
            "state_off": "Disabled",
            "payload_on": WIFI_ON_CMD,
            "payload_off": WIFI_OFF_CMD,
            "icon": "mdi:wifi",
            "device": device
        }
        await self.client.publish(
            f"{self.discovery_prefix}/switch/{device['model']}/config",
            payload=json.dumps(hass_discovery_switch),
            retain=True
        )
        hass_discovery_qss = {
            "name": "QSS",
            "state_topic": "tplinkrouter/wifi",
            "command_topic": "tplinkrouter/wifi/set",
            "unique_id": "qss_switch",
            "value_template": "{{ value_json.QSS }}",
            "state_on": "Enable",
            "state_off": "Disabled",
            "payload_on": QSS_ON_CMD,
            "payload_off": QSS_OFF_CMD,
            "icon": "mdi:wifi",
            "device": device
        }
        await self.client.publish(
            f"{self.discovery_prefix}/switch/{device['model']}/config",
            payload=json.dumps(hass_discovery_qss),
            retain=True
        )
        logging.info(f"hass discovery config sent: {hass_discovery_switch}")

