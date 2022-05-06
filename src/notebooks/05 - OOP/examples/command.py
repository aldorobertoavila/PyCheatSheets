import asyncio
import os
import time

from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime

import aiofiles
import cv2
import dotenv

from aiohttp import ClientSession


class Command(ABC):

    @abstractmethod
    async def execute(self, **kwargs):
        pass

    @abstractmethod
    async def redo(self):
        pass

    @abstractmethod
    async def undo(self):
        pass


@dataclass
class ImageCommand(Command):
    paths: list[str] = field(default_factory=list)

    @abstractmethod
    async def process_image(self, image: cv2.Mat) -> cv2.Mat:
        pass

    async def execute(self):
        self.images = [cv2.imread(path) for path in self.paths]

        for image, path in zip(self.images, self.paths):
            new_image = await self.process_image(image)
            cv2.imwrite(path, new_image)

    async def redo(self):
        await self.execute()

    async def undo(self):
        for image, path in zip(self.images, self.paths):
            cv2.imwrite(path, image)


@dataclass
class ConvertColorCommand(ImageCommand):
    code: int = field(default_factory=int)

    async def process_image(self, image: cv2.Mat) -> cv2.Mat:
        return cv2.cvtColor(image, self.code)


@dataclass
class BlurCommand(ImageCommand):
    ksize: tuple[int, int] = field(default_factory=tuple)
    sigma_x: int = field(default_factory=int)

    async def process_image(self, image: cv2.Mat) -> cv2.Mat:
        return cv2.GaussianBlur(image, self.ksize, self.sigma_x)


@dataclass
class ResizeCommand(ImageCommand):
    dimensions: tuple[int, int] = field(default_factory=tuple)

    async def process_image(self, image: cv2.Mat) -> cv2.Mat:
        return cv2.resize(image, self.dimensions)


@dataclass
class FetchCommand(Command):
    paths: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)

    async def fetch(self, url: str, session: ClientSession):
        async with session.get(url) as response:
            return await response.read()

    async def write(self, path: str, buf: bytes):
        async with aiofiles.open(path, mode='wb') as file:
            await file.write(buf)

    async def execute(self):
        async with ClientSession() as session:
            responses = [self.fetch(url, session) for url in self.urls]
            buffers = await asyncio.gather(*responses)
            files = [self.write(path, buf)
                     for path, buf in zip(self.paths, buffers)]
            await asyncio.gather(*files)

    async def redo(self):
        await self.execute()

    async def undo(self):
        for path in self.paths:
            os.remove(path)


@dataclass
class CommandController:
    undo_stack: deque = field(default_factory=deque)
    redo_stack: deque = field(default_factory=deque)

    async def execute(self, command) -> None:
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

    paths = [ f'{folder}/{today()}-{n}.jpg' for n in range(120, 136) ]
    urls = [ f'https://picsum.photos/id/{n}/1000/1000' for n in range(120, 136) ]

    fetch = FetchCommand(paths, urls)
    color = ConvertColorCommand(paths, cv2.COLOR_BGR2GRAY)
    resize = ResizeCommand(paths, (750, 750))
    blur = BlurCommand(paths, (5, 5), cv2.BORDER_CONSTANT)

    await controller.execute(fetch)
    await controller.execute(color)
    await controller.execute(resize)
    await controller.execute(blur)
    time.sleep(5)
    await controller.undo()
    await controller.undo()
    await controller.undo()
    await controller.undo()
    time.sleep(5)
    await controller.redo()
    await controller.redo()
    await controller.redo()
    await controller.redo()


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
