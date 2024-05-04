from typing import Union, Generator, Optional

from dashscope.api_entities.dashscope_response import Message, Role
import dashscope


class ChatException(Exception):
    """通义千问异常类"""
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code


class QianWen:
    """通义千问对话类"""
    def __init__(
            self,
            messages: Optional[list[Message]] = None,
            model: Optional[str] = None,
            api_key: Optional[str] = None, **kwargs
    ):
        """
        初始化
        :param messages: 聊天记录
        :param model: 模型
        :param kwargs: chat方法中预定的其他参数
        """
        self.messages = messages or []
        self.model = model or dashscope.Generation.Models.qwen_turbo
        self.api_key = api_key
        self.kwargs = kwargs

    def chat(self, message: str, stream: bool = False, **kwargs) -> Union[str, Generator[str, None, None]]:
        resp = dashscope.Generation.call(self.model, message, messages=self.messages, stream=stream, api_key=self.api_key, **self.kwargs, **kwargs)
        if resp.status_code != 200:
            raise ChatException(resp.status_code, resp.message)
        if not stream:
            result = resp.output.text
            self.messages.append(Message(Role.USER, message))
            self.messages.append(Message(Role.ASSISTANT, result))
            return result
        else:
            def generate():
                for r in resp:
                    r = r.output.text
                    text = r
                    yield r
                self.messages.append(Message(Role.USER, message))
                self.messages.append(Message(Role.ASSISTANT, text))
            return generate()

    @classmethod
    def set_global_access_key(cls, ak):
        dashscope.api_key = ak


if __name__ == '__main__':
    qianwen = QianWen()
    for i in qianwen.chat("我早上吃了面包", stream=True):
        print("\r" + i, end="", flush=True)
    print()
    print()
    print(qianwen.chat("这样健康吗"))
