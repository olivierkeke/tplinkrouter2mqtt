import json
import logging
from asyncio import QueueFull
from dataclasses import dataclass

import aiomqtt
from aiomqtt import Message

from .telnet import TelnetCommunicator
from .tplink_config import WIFI_ON_CMD, WIFI_OFF_CMD, QSS_ON_CMD, QSS_OFF_CMD


@dataclass
class TpLinkRouterToMQTTCommunicator:

    telnet_communicator: TelnetCommunicator
    client: aiomqtt.Client
    discovery_prefix = 'homeassistant'
    interval = 5

    async def publish_state(self):
        while True:
            wifi_state = await self.telnet_communicator.state_message_queue.get()
            payload = json.dumps(wifi_state)
            logging.debug("received message from telnet communicator: %s", payload)
            await self.client.publish("tplinkrouter/wifi", payload=payload)
            logging.debug("sent message to mqtt with payload: %s", payload)


    async def listen_to_command(self):
        await self.client.subscribe("tplinkrouter/wifi/set")
        await self.client.subscribe("homeassistant/status")
        async for message in self.client.messages:
            message: Message
            logging.debug("received message with payload: %s on topic %s", message.payload, message.topic)
            if message.topic.matches("tplinkrouter/wifi/set"):
                try:
                    self.telnet_communicator.command_messsage_queue.put_nowait(message.payload)
                except QueueFull:
                    logging.warning('Command message queue is full')
            elif message.topic.matches("homeassistant/status"):
                logging.debug("received hass status %s", message.payload)
                if message.payload == b'online':
                    await self.send_hass_discovery()
            

    async def send_hass_discovery(self):
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
            f"{self.discovery_prefix}/switch/{device['model']}_wifi/config",
            payload=json.dumps(hass_discovery_switch)
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
            f"{self.discovery_prefix}/switch/{device['model']}_qss/config",
            payload=json.dumps(hass_discovery_qss)
        )
        hass_discovery_ssid = {
            "name": "SSID",
            "state_topic": "tplinkrouter/wifi",
            "unique_id": "ssid_sensor",
            "value_template": "{{ value_json.SSID }}",
            "icon": "mdi:wifi",
            "device": device
        }
        await self.client.publish(
            f"{self.discovery_prefix}/sensor/{device['model']}_ssid/config",
            payload=json.dumps(hass_discovery_ssid)
        )
        hass_discovery_secmode = {
            "name": "SecMode",
            "state_topic": "tplinkrouter/wifi",
            "unique_id": "secmode_sensor",
            "value_template": "{{ value_json.SecMode }}",
            "icon": "mdi:wifi",
            "device": device
        }
        await self.client.publish(
            f"{self.discovery_prefix}/sensor/{device['model']}_secmode/config",
            payload=json.dumps(hass_discovery_secmode)
        )
        hass_discovery_bandwidth = {
            "name": "bandWidth",
            "state_topic": "tplinkrouter/wifi",
            "unique_id": "secmode_sensor",
            "value_template": "{{ value_json.andWidth }}",
            "icon": "mdi:wifi",
            "device": device
        }
        await self.client.publish(
            f"{self.discovery_prefix}/sensor/{device['model']}_bandwidth/config",
            payload=json.dumps(hass_discovery_bandwidth)
        )
        logging.info("hass discovery config sent")

    async def __aenter__(self):
        await self.telnet_communicator.__aenter__()
        await self.client.__aenter__()

    async def __aexit__(self, exc_type, exc, tb):
        await self.client.__aexit__(exc_type, exc, tb)
        await self.telnet_communicator.__aexit__(exc_type, exc, tb)
