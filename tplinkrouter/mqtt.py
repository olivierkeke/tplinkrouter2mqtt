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
            await self.client.publish("tplinkrouter/wifi", payload=json.dumps(wifi_state))

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
            "payload_off": "Disable"
        }
        await self.client.publish(
            f"{self.discovery_prefix}/switch/tplinkrouter/config",
            payload=json.dumps(hass_discovery_switch),
            retain=True
        )

