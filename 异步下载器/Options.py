from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from io import FileIO
from urllib.parse import urlparse


@dataclass(eq=False)  # unsafe_hash在修改对象后移出dict时会报错
class Options:
    url = ""
    save_path = ""
    file_name = ""
    proxy = ""

    started = False
    file_size = -1
    download_size = 0
    finished = False
    failed = False

    def check(self):
        assert self.url, 0
        # 判断url是否合法
        parsed = urlparse(self.url)
        assert parsed.scheme in ("http", "https"), 3
        assert parsed.netloc, 3
        assert self.save_path, 1
        assert Path(self.save_path).is_dir(), 4
        assert self.file_name, 2
        if self.proxy:
            parsed = urlparse(self.proxy)
            assert parsed.scheme in ("http", "https"), 5
            assert parsed.netloc, 5

    def __hash__(self):
        return id(self)
