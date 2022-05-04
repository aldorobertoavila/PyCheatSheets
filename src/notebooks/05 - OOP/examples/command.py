import asyncio
import os

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime

import aiofiles
import aiohttp
import dotenv


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
class FetchCommand():
    urls: list[tuple[str, str]]

    async def fetch(self, session, url):
        async with session.get(url) as response:
            await response.read()

    async def write(self, path, buf):
        async with aiofiles.open(path, mode='wb') as file:
            await file.write(buf)

    async def execute(self):
        async with aiohttp.ClientSession() as session:
            paths, urls = self.urls
            responses = [self.fetch(session, url) for url in urls]
            buffers = await asyncio.gather(*responses)
            files = [self.write(path, buf) for path, buf in zip(paths, buffers)]
            await asyncio.gather(*files)

    async def redo(self):
        pass

    async def undo(self):
        pass


@dataclass
class CommandController:
    undo: deque = field(default_factory=deque)
    redo: deque = field(default_factory=deque)

    async def execute(self, command: Command) -> None:
        await command.execute()
        self.redo.clear()
        self.undo.append(command)

    async def redo(self) -> None:
        if not self.redo:
            return
        command = self.redo.pop()
        await command.execute()
        self.undo.append(command)

    async def undo(self) -> None:
        if not self.undo:
            return
        command = self.undo.pop()
        await command.undo()
        self.redo.append(command)


def today():
    return f'{datetime.now():%Y-%m-%d-%H-%M-%S%z}'


async def main():
    dotenv.load_dotenv()
    controller = CommandController()
    
    folder = os.getenv('TEMP_FOLDER')

    await controller.execute(FetchCommand([
        (f'{folder}/{today()}-{1075}.jpg', 'https://picsum.photos/id/1075/1000/1000'),
        (f'{folder}/{today()}-{1065}.jpg', 'https://picsum.photos/id/1065/1000/1000'),
        (f'{folder}/{today()}-{1055}.jpg', 'https://picsum.photos/id/1055/1000/1000'),
        (f'{folder}/{today()}-{1045}.jpg', 'https://picsum.photos/id/1045/1000/1000'),
    ]))

if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
