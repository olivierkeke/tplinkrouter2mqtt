import asyncio
import json
import logging
from asyncio import QueueFull, Task
from dataclasses import dataclass
from functools import cached_property
from typing import Dict, Optional

import telnetlib3
from threading import Timer

from telnetlib3 import TelnetReader, TelnetWriter

from .tplink_config import REFRESH_CMD, frame_to_dict, GET_SERIAL_CMD, serial_pattern


@dataclass
class TelnetCommunicator:

    username: str
    password: str
    host: str
    state_message_queue: asyncio.Queue[Dict[str, str]] = asyncio.Queue()
    command_messsage_queue: asyncio.Queue[str] = asyncio.Queue()
    reader: Optional[TelnetReader] = None
    writer: Optional[TelnetWriter] = None
    serial: Optional[str] = None
    listen_task: Optional[Task] = None
    update_task: Optional[Task] = None

    async def listen_command(self):
        if self.command_messsage_queue is not None:
            while True:
                cmd = await self.command_messsage_queue.get()
                logging.debug(f"writing command: {cmd.decode()}")
                self.writer.write(f'{cmd.decode()}\n')

    async def update(self):
        while True:
            self.writer.write(f'{REFRESH_CMD}\n')
            while True:
                outp = await self.reader.read(1024)
                frame = frame_to_dict(outp)
                if frame:
                    try:
                        logging.debug(f"wifi_frame: {json.dumps(frame)}")
                        try:
                            self.state_message_queue.put_nowait(frame)
                        except QueueFull:
                            logging.warning('State message queue is full')
                    except TypeError:
                        logging.debug(f"malformed frame: {frame}")
                    break
                else:
                    logging.debug(f"receive unknown message: {outp}")
            await asyncio.sleep(10)

    async def get_serial(self) -> str:
        self.writer.write(f'{GET_SERIAL_CMD}\n')
        while True:
            outp = await self.reader.read(1024)
            if 'serialNumber' in outp:
                result = serial_pattern.search(outp)
                return result.group(1)

    async def authenticate(self):
        while True:
            # read stream until '?' mark is found
            outp = await self.reader.read(1024)
            if not outp:
                # End of File
                break
            elif 'username:' in outp:
                # reply all questions with 'y'.
                self.writer.write(f'{self.username}\n')
            elif 'password:' in outp:
                self.writer.write(f'{self.password}\n')
            elif 'Welcome' in outp:
                break
            else:
                logging.debug(f"receive unknown message: {outp}")

    async def launch(self):
        self.reader, self.writer = await telnetlib3.open_connection(self.host, 23)
        logging.info(f'connected to telnet server {self.host}')
        await self.authenticate()
        logging.info(f'authenticated to telnet server {self.host}')
        self.serial = await self.get_serial()
        logging.info(f'device serial: {self.serial}')
        self.listen_task = asyncio.create_task(self.listen_command())
        self.update_task = asyncio.create_task(self.update())
        logging.info(f'telnet communicator launched')

    async def close(self):
        if self.listen_task is not None:
            self.listen_task.cancel()
        if self.update_task is not None:
            self.update_task.cancel()
        self.writer.write('logout\n')
        await self.writer.protocol.waiter_closed
