import asyncio
import os
import time

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime

import aiofiles
import dotenv

from aiohttp import ClientSession

class Command(ABC):

    @abstractmethod
    async def execute(self):
        pass

    @abstractmethod
    async def redo(self):
        pass

    @abstractmethod
    async def undo(self):
        pass


@dataclass
class FetchCommand(Command):
    pictures: list[tuple[str, str]]

    async def fetch(self, url: str, session: ClientSession):
        start = time.time()
        async with session.get(url) as response:
            payload = await response.read()
            millis = 1e3 * (time.time() - start)
            length = len(payload) / 1e3
            print(f'{url} {millis:.2f}ms {length:.2f}kB')
            return payload

    async def write(self, path: str, buf: bytes):
        start = time.time()
        async with aiofiles.open(path, mode='wb') as file:
            await file.write(buf)
            filename = os.path.basename(path)
            millis = 1e3 * (time.time() - start)
            length = len(buf) / 1e3
            print(f'{filename} {millis:.2f}ms {length:.2f}kB')

    async def execute(self):
        async with ClientSession() as session:
            paths, urls = zip(*self.pictures)
            responses = [self.fetch(url, session) for url in urls]
            buffers = await asyncio.gather(*responses)
            files = [self.write(path, buf) for path, buf in zip(paths, buffers)]
            await asyncio.gather(*files)

    async def redo(self):
        pass

    async def undo(self):
        pass


@dataclass
class CommandController:
    undo_stack: deque = field(default_factory=deque)
    redo_stack: deque = field(default_factory=deque)

    async def execute(self, command: Command) -> None:
        await command.execute()
        self.redo_stack.clear()
        self.undo_stack.append(command)

    async def redo(self) -> None:
        if not self.redo_stack:
            return
        command = self.redo_stack.pop()
        await command.execute()
        self.undo_stack.append(command)

    async def undo(self) -> None:
        if not self.undo_stack:
            return
        command = self.undo_stack.pop()
        await command.undo()
        self.redo_stack.append(command)


async def main():
    dotenv.load_dotenv()
    folder = os.getenv('COMMAND_FOLDER')
    controller = CommandController()
    
    def today():
        return f'{datetime.now():%Y-%m-%d-%H-%M-%S%z}'

    await controller.execute(FetchCommand([
        (f'{folder}/{today()}-{1075}.jpg', 'https://picsum.photos/id/1075/1000/1000'),
        (f'{folder}/{today()}-{1065}.jpg', 'https://picsum.photos/id/1065/1000/1000'),
        (f'{folder}/{today()}-{1055}.jpg', 'https://picsum.photos/id/1055/1000/1000'),
        (f'{folder}/{today()}-{1045}.jpg', 'https://picsum.photos/id/1045/1000/1000')
    ]))

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
