import asyncio
import pathlib
from types import FunctionType

import aiofiles
from PyQt5.QtCore import QThread, pyqtSignal, pyqtBoundSignal
from httpx import AsyncClient

from Downloader import Downloader
from Options import Options
from Window import Window


class LoopThread(QThread):
    def __init__(self, loop):
        super().__init__()
        self.loop = loop

    def run(self):
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()


class Client(Window):
    """包含下载逻辑的qt客户端"""
    execute_signal: pyqtBoundSignal = pyqtSignal(FunctionType)

    def __init__(self):
        super().__init__()
        self.loop = asyncio.new_event_loop()
        self.loop_thread = LoopThread(self.loop)
        self.loop_thread.start()
        self.downloader_map: dict[Options, Downloader] = {}
        self.update_progress_bar_timer_id = self.startTimer(120)

    def start_download(self, options: Options):
        client = AsyncClient(proxies=options.proxy or None, timeout=50, verify=False)
        downloader = Downloader(loop=self.loop, http_client=client)
        self.downloader_map[options] = downloader
        asyncio.run_coroutine_threadsafe(self.start_and_monitor(downloader, options), self.loop)
        options.started = True

    def on_change_tab(self, index):
        super().on_change_tab(index)
        self.update_progress_bar()

    async def start_and_monitor(self, downloader, options):
        path = pathlib.Path(options.save_path, options.file_name)
        options.download_size = 0
        options.failed = False
        try:
            async with downloader:
                options.file_size = await downloader.get_content_length_async(options.url, follow_redirects=True)
                async with aiofiles.open(path, "wb") as file:
                    async for chunk, offset, length in downloader.download_async(options.url, follow_redirects=True):
                        await file.seek(offset)
                        await file.write(chunk)
                        options.download_size += length
        except Exception as e:
            import traceback
            traceback.print_exc()
            if not isinstance(e, RuntimeError):  # 如果http客户端被关闭(只有下载暂停时才是)，则是RuntimeError
                tab = self.tab_bar.tab(options)
                if tab is not None:
                    e_str = str(e)
                    self.execute_signal.emit(lambda: self.tip(tab, "下载失败", e_str))
                options.failed = True
            options.started = False
            path.unlink(missing_ok=True)
            self.execute_signal.emit(
                lambda: (self.update_progress_bar(), self.update_option()))  # 分开提交会导致第二个提交的任务不会执行？？？
        else:
            options.finished = True
            options.started = False
            tab = self.tab_bar.tab(options)
            if tab is not None:
                self.execute_signal.emit(
                    lambda: (self.teaching_tip(tab, "下载完成", options.file_name), self.update_option()))
            else:
                self.execute_signal.emit(self.update_option)
        finally:
            self.downloader_map.pop(options)

    def timerEvent(self, a0):
        if a0.timerId() == self.update_progress_bar_timer_id:
            self.update_progress_bar()
            a0.accept()
        else:
            super().timerEvent(a0)

    def stop_download(self, options: Options):
        downloader = self.downloader_map.pop(options)
        downloader.close(False)
        options.started = False

    def bind_signals(self):
        super().bind_signals()
        self.execute_signal.connect(lambda x: x())

    def closeEvent(self, a0):
        for downloader in self.downloader_map.values():
            downloader.close(False)
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.loop_thread.wait()
