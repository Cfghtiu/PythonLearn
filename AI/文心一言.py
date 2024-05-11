from typing import Union, Optional, Generator

import qianfan


# 文心一言没有定义异常类，因为我不想登录千帆平台看文档了


class YiYan:
    """文心一言对话类"""
    def __init__(
            self, messages: Optional[qianfan.Messages] = None,
            chat_comp: Optional[qianfan.ChatCompletion] = None,
            model: Optional[str] = None,
            access_key: Optional[str] = None,
            secret_key: Optional[str] = None,
            **kwargs
    ):
        """
        初始化，如果传入了chat_comp，就不用再传入messages外的其他参数了
        :param messages: 历史记录
        :param chat_comp: ChatCompletion，如果为None，则根据接下来的其他参数构建ChatCompletion
        :param model: 模型
        :param access_key: 密钥
        :param secret_key: 密钥
        :param kwargs: 其他用于构建ChatCompletion的参数
        """
        self.chat_comp = chat_comp or qianfan.ChatCompletion(model=model, ak=access_key, sk=secret_key, **kwargs)
        self.messages = messages or qianfan.Messages()

    def chat(self, message: str, stream: bool = False, **kwargs) -> Union[str, Generator[str, None, None]]:
        self.messages.append(message)
        resp = self.chat_comp.do(self.messages, stream=stream, **kwargs)
        if not stream:
            result = resp.body['result']
            self.messages.append(result, qianfan.Role.Assistant)
            return result
        else:
            def generate():
                text = ""
                for r in resp:
                    r = r.body['result']
                    text += r
                    yield r
                self.messages.append(text, qianfan.Role.Assistant)
            return generate()

    @classmethod
    def set_global_access_key(cls, ak):
        qianfan.AccessKey(ak)

    @classmethod
    def set_global_secret_key(cls, sk):
        qianfan.SecretKey(sk)


if __name__ == '__main__':
    yiyan = YiYan()
    for i in yiyan.chat("我早上吃了面包", stream=True):
        print(i, end="", flush=True)
    print()
    print()
    print(yiyan.chat("这样健康吗"))
