from httpx import Client, AsyncClient
from typing import Union, Optional
import random
import hashlib


def md5(s):
    return hashlib.md5(s.encode("utf-8")).hexdigest()


class TranslationException(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def _join_result(result: dict) -> str:
    if 'error_code' in result:
        raise TranslationException(result['error_code'], result['error_msg'])
    return "\n".join(i['dst'] for i in result['trans_result'])


class BaiduTranslator:
    URL = "https://fanyi-api.baidu.com/api/trans/vip/translate"

    def __init__(self, app_id, app_key, from_="auto", to="zh", http_client: Union[Client, AsyncClient] = None):
        self.__app_id = app_id
        self.__app_key = app_key
        self.from_ = from_
        self.to = to
        self.http_client = http_client or Client(default_encoding="utf-8")

    def _build_params(self, query, from_, to):
        salt = str(random.randint(32768, 65536))
        return {
            "q": query,
            "from": from_ or self.from_,
            "to": to or self.to,
            "appid": self.__app_id,
            "salt": salt,
            "sign": md5(self.__app_id + query + salt + self.__app_key)
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


async def main():
    import os
    t = BaiduTranslator(os.environ["APP_ID"], os.environ["APP_KEY"], http_client=AsyncClient())
    print(await t.translate_text_async("hello world"))


if __name__ == '__main__':
    import asyncio
    asyncio.get_event_loop().run_until_complete(main())
