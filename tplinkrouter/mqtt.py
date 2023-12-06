import asyncio
import json
import logging
from asyncio import QueueFull
from dataclasses import dataclass
from typing import Dict

import aiomqtt


@dataclass
class MQTTCommunicator:

    client: aiomqtt.Client
    state_message_queue: asyncio.Queue[Dict[str, str]]
    command_messsage_queue: asyncio.Queue[str]
    discovery_prefix = 'homeassistant'

    async def publish_state(self):
        while True:
            wifi_state = await self.state_message_queue.get()
            payload = json.dumps(wifi_state)
            await self.client.publish("tplinkrouter/wifi", payload=payload)
            logging.debug(f'sent message to mqtt with payload: {payload}')

    async def listen_to_command(self):
        async with self.client.messages() as messages:
            await self.client.subscribe("tplinkrouter/wifi/set")
            async for message in messages:
                try:
                    self.state_message_queue.put_nowait(message.payload)
                except QueueFull:
                    logging.warning('Command message queue is full')

    async def hass_discovery(self):
        hass_discovery_switch = {
            "name": "wifi",
            "state_topic": "tplinkrouter/wifi",
            "command_topic": "tplinkrouter/wifi/set",
            "unique_id": "wifi_switch",
            "value_template": "{{ value_json.Status }}",
            "payload_on": "Up",
            "payload_off": "Disabled",
            "icon": "mdi:wifi",
            "device": {
                "identifiers": [
                    "TD-W870"
                ],
                "manufacturer": "TPlink"
            }
        }
        await self.client.publish(
            f"{self.discovery_prefix}/switch/tplinkrouter/config",
            payload=json.dumps(hass_discovery_switch),
            retain=True
        )
        logging.info(f"hass discovery config sent: {hass_discovery_switch}")

