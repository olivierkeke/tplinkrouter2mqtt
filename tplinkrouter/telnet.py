import asyncio
import json
import logging
from asyncio import QueueFull
from dataclasses import dataclass
from typing import Dict

import telnetlib3
from threading import Timer

from telnetlib3 import TelnetReader, TelnetWriter

from .tplink_config import REFRESH_CMD, frame_to_dict


@dataclass
class TelnetCommunicator:

    username: str
    password: str
    host: str
    state_message_queue: asyncio.Queue[Dict[str, str]] = asyncio.Queue()
    command_messsage_queue: asyncio.Queue[str] = asyncio.Queue()

    async def shell(self, reader: TelnetReader, writer: TelnetWriter):
        while True:
            # read stream until '?' mark is found
            outp = await reader.read(1024)
            if not outp:
                # End of File
                break
            elif 'username:' in outp:
                # reply all questions with 'y'.
                writer.write(f'{self.username}\n')
            elif 'password:' in outp:
                writer.write(f'{self.password}\n')
            elif 'CLI exited after timing out' in outp:
                timer.stop()
                writer.write('\n')
            elif 'Welcome' in outp:
                asyncio.create_task(self.listen_command(writer))
            else:
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
                else:
                    logging.debug(f"receive unknown message: {outp}")
            if 'TP-LINK(conf)#' in outp:
                def func():
                    writer.write(f'{REFRESH_CMD}\n')
                timer = Timer(10, func)
                timer.start()

            # display all server output
            #logging.debug(f"receive message: {outp}")

        # EOF
        #print()

    async def listen_command(self, writer: TelnetWriter):
        if self.command_messsage_queue is not None:
            while True:
                cmd = await self.command_messsage_queue.get()
                writer.write(f'{cmd}\n')

    async def run(self):
        reader, writer = await telnetlib3.open_connection(self.host, 23, shell=self.shell)
        await writer.protocol.waiter_closed
