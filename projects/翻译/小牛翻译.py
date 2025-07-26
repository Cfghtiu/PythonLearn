from typing import Union, Optional

from httpx import Client, AsyncClient


class TranslationException(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


class NiuTranslator:
    URL = "https://api.niutrans.com/NiuTransServer/translation"

    def __init__(self, api_key, from_="auto", to="zh", http_client: Union[Client, AsyncClient] = None):
        self.__api_key = api_key
        self.from_ = from_
        self.to = to
        self.http_client = http_client or Client(default_encoding="utf-8")

    def _build_params(self, query, from_, to):
        return {
            "src_text": query,
            "from": from_ or self.from_,
            "to": to or self.to,
            "apikey": self.__api_key
        }

    def translate(self, query: str, from_: Optional[str] = None, to: Optional[str] = None) -> dict:
        assert isinstance(self.http_client, Client)
        return self.http_client.post(self.URL, params=self._build_params(query, from_, to)).json()

    async def translate_async(self, query, from_: Optional[str] = None, to: Optional[str] = None) -> dict:
        assert isinstance(self.http_client, AsyncClient)
        return (await self.http_client.post(self.URL, params=self._build_params(query, from_, to))).json()

    def translate_text(self, query: str, from_: Optional[str] = None, to: Optional[str] = None) -> str:
        result = self.translate(query, from_, to)
        return result['tgt_text']

    async def translate_text_async(self, query: str, from_: Optional[str] = None, to: Optional[str] = None) -> str:
        result = await self.translate_async(query, from_, to)
        return result['tgt_text']


if __name__ == '__main__':
    import os
    t = NiuTranslator(os.environ["API_KEY"])
    print(t.translate("nice!"))
