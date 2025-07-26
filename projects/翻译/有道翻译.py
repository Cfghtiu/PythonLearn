from httpx import Client, AsyncClient
from typing import Union, Optional
import random
import hashlib
import time


def sha256(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class TranslationException(Exception):
    def __init__(self, code):
        super().__init__(f"错误码:{code}")
        self.code = code


def _join_result(result: dict) -> str:
    if 'errorCode' in result:
        raise TranslationException(result['errorCode'])
    return "\n".join(i['dst'] for i in result['trans_result'])


class YouDaoTranslator:
    URL = "https://openapi.youdao.com/api"

    def __init__(self, app_id, app_key, from_="auto", to="zh", http_client: Union[Client, AsyncClient] = None):
        self.__app_id = app_id
        self.__app_key = app_key
        self.from_ = from_
        self.to = to
        self.http_client = http_client or Client(default_encoding="utf-8")

    def _build_params(self, query, from_, to):
        salt = str(random.randint(32768, 65536))
        cur_time = str(int(time.time()))
        print(cur_time)
        if len(query) < 20:
            input_ = query
        else:
            input_ = query[:10] + str(len(query)) + query[-10:]
        return {
            "q": query,
            "from": from_ or self.from_,
            "to": to or self.to,
            "appKey": self.__app_id,
            "salt": salt,
            "sign": sha256(self.__app_id + input_ + salt + cur_time + self.__app_key),
            "signType": "v3",
            "curtime": cur_time
        }

    def translate(self, query: str, from_: Optional[str] = None, to: Optional[str] = None) -> dict:
        assert isinstance(self.http_client, Client)
        return self.http_client.get(self.URL, params=self._build_params(query, from_, to)).json()

    async def translate_async(self, query, from_: Optional[str] = None, to: Optional[str] = None) -> dict:
        assert isinstance(self.http_client, AsyncClient)
        return (await self.http_client.get(self.URL, params=self._build_params(query, from_, to))).json()

    def translate_text(self, query: str, from_: Optional[str] = None, to: Optional[str] = None) -> str:
        result = self.translate(query, from_, to)
        return _join_result(result)

    async def translate_text_async(self, query: str, from_: Optional[str] = None, to: Optional[str] = None) -> str:
        result = await self.translate_async(query, from_, to)
        return _join_result(result)


if __name__ == '__main__':
    import os
    t = YouDaoTranslator(os.environ["APP_ID"], os.environ["APP_KEY"])
    print(t.translate("hello world\nlet's say again"))
    print(t.translate_text("nice to meet you"))
