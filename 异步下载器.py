import asyncio
import io
import threading
from queue import Queue
from typing import Union, Optional, AsyncGenerator, Generator
from urllib.parse import urlparse

from httpx import AsyncClient


class Downloader:
    """异步下载器"""
    def __init__(self,
                 http_client: Optional[AsyncClient] = None,
                 max_workers: int = 30,
                 worker_min_download_size=1024 * 1024,
                 loop: Optional[asyncio.AbstractEventLoop] = None):
        """
        异步下载器，在创建时会开启一个线程，用于异步下载文件
        :param http_client: 异步Http客户端
        :param max_workers: 最大工作任务数
        :param worker_min_download_size: 每个工作任务最少下载大小
        :param loop: 事件循环，如果不指定则创建一个新事件循环，并在新线程中运行
        """
        self.http_client = http_client or AsyncClient()
        self.max_workers = max_workers
        self.worker_min_download_size = worker_min_download_size
        self.thread: Optional[threading.Thread] = None
        if loop:
            self.loop = loop
        else:
            self.loop = asyncio.new_event_loop()
            self.thread = threading.Thread(target=self.loop.run_forever, daemon=True)
            self.thread.start()

    def close(self):
        self.loop.stop()
        # await self.http_client.aclose()
        self.loop.run_until_complete(self.http_client.aclose())

    def get(self, url: str, **kwargs) -> bytes:
        cache = io.BytesIO()
        self.save(url, file=cache, **kwargs)
        return cache.getvalue()

    async def get_async(self, url: str, **kwargs) -> bytes:
        cache = io.BytesIO()
        await self.save_async(url, file=cache, **kwargs)
        return cache.getvalue()

    def save(self, url: str, file: Union[io.IOBase, str, None] = None, **kwargs):
        if file is None:
            file = urlparse(url).path.split("/")[-1]
        if isinstance(file, str):
            file = open(file, "wb")
        with file:
            for chunk, offset, length in self.download(url, **kwargs):
                file.seek(offset)
                file.write(chunk)

    async def save_async(self, url: str, file: Union[io.IOBase, str, None] = None, **kwargs):
        import aiofiles
        if file is None:
            file = urlparse(url).path.split("/")[-1]
        if isinstance(file, str):
            file = aiofiles.open(file, "wb")
        async with file:
            async for chunk, offset, length in self._download(url, **kwargs):
                file.seek(offset)
                await file.write(chunk)

    def download(self, url: str, **kwargs) -> Generator[tuple[bytes, int, int], None, None]:
        queue = Queue()

        async def enqueue():
            async for value in self.download_async(url, **kwargs):
                queue.put(value)
            queue.put(None)

        asyncio.run_coroutine_threadsafe(enqueue(), self.loop)
        while True:
            i = queue.get()
            if i is None:
                break
            yield i

    async def download_async(self, url: str, **kwargs) -> AsyncGenerator[tuple[bytes, int, int], None]:
        """
        异步下载给定url数据，如果响应头中包含Content-Length，则将数据分成多个任务下载
        :param url: 下载地址
        :param kwargs: http_client请求时的其他参数，注意：如果参数中包含headers，那么headers里面不能包含Range字段
        :return: 一个异步生成器
        """
        headers = kwargs.get("headers", {})
        assert "Range" not in headers, ValueError("Range header is not allowed")
        content_length = await self.get_content_length_async(url, **kwargs)
        if content_length == 0:
            async for value in self._download(url, None):
                yield value
            return
        # 计算最大下载工作数
        worker_count = content_length // self.worker_min_download_size
        if content_length % self.worker_min_download_size != 0:
            worker_count += 1
        worker_count = min(worker_count, self.max_workers)

        async def enqueue(g: AsyncGenerator):
            """一个简单的将生成器中的值放入队列中的函数"""
            async for value in g:
                await queue.put(value)

        queue = asyncio.Queue()
        # 将文件分割成工作任务，并启动异步下载任务
        tasks = []
        for i in range(worker_count):
            start = i * content_length // worker_count
            end = (i + 1) * content_length // worker_count
            range_ = (start, end)
            task = asyncio.run_coroutine_threadsafe(enqueue(self._download(url, range_)), self.loop)
            tasks.append(task)
        # 等待所有异步下载任务完成
        over_count = 0
        while worker_count != over_count:
            get = await queue.get()
            if get is None:
                over_count += 1
            else:
                yield get

    def get_content_length(self, url: str, **kwargs):
        content_length = asyncio.run_coroutine_threadsafe(self.get_content_length_async(url, **kwargs), self.loop).result()
        return content_length

    async def get_content_length_async(self, url: str, **kwargs):
        try:
            headers = (await self.http_client.head(url, **kwargs)).headers
            content_length = int(headers.get("Content-Length", 0))
        except KeyError:
            content_length = 0
        return content_length

    async def _download(self, url: str, range_: Optional[tuple[int, int]], **kwargs) -> AsyncGenerator[Optional[tuple[bytes, int, int]], None]:
        offset = 0
        if range_:
            headers = kwargs.setdefault("headers", {})
            headers["Range"] = f"bytes={range_[0]}-{range_[1]}"
            offset = range_[0]
        async with self.http_client.stream("GET", url, **kwargs) as response:
            async for chunk in response.aiter_bytes(1024 * 1024):
                length = len(chunk)
                yield chunk, offset, length
                offset += length
        yield None


if __name__ == '__main__':
    import tqdm
    downloader = Downloader()
    u = "http://127.0.0.1/LocalSend.exe"
    size = downloader.get_content_length(u)
    t = tqdm.tqdm(total=size)
    g = downloader.download(u)
    for c, o, l in g:
        t.update(l)

