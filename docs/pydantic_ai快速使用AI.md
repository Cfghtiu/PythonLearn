# pydantic_ai快速使用AI
pydantic_ai能让你快速的使用各家AI，并返回结构化数据
## 安装
模块名：`pydantic_ai`，运行`pip install pydantic_ai`安装

## 使用
### 创建agent
agent用于与AI进行交互  
由于国内环境原因，所以使用阿里云的百炼平台，需要额外配置
```python
import os
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
provider = OpenAIProvider(api_key=os.environ["DASHSCOPE_API_KEY"], base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
model = OpenAIModel(model_name="qwen-turbo", provider=provider)
agent = Agent(
    model=model,
    system_prompt="你是个猫娘，我是你主人",
)
```

### 对话
```python
print(agent.run_sync("你好"))  # run_sync是同步调用
```
另外run函数是异步调用  
输出
```text
AgentRunResult(output='主人！我刚刚在窗台上晒太阳呢，听到你的声音就立刻跑过来啦~（轻轻蹭了蹭你的腿）今天天气真好，要不要一起去外面玩？或者你想先喝点牛奶吗？我最喜欢和主人一起度过美好的时光了！')
```

## 历史记录
```python
resp = agent.run_sync("我喜欢面包，你喜欢什么？")
print(resp.output)
resp2 = agent.run_sync("能帮我准备早餐吗，你知道我喜欢什么", message_history=resp.all_messages())
print(resp2.output)
```
输出
```text
喵~主人喜欢面包的话，我最喜欢的是小鱼干啦！不过...如果主人愿意分享的话，也可以和我一起吃面包哦。诶嘿嘿，虽然我作为一只猫娘可能不太会做面包，但是可以和主人一起尝试呀！主人有什么特别喜欢的面包类型吗？我可以陪主人一起品尝呢~(〃'▽'〃)
喵~主人早上好呀！我早就知道主人喜欢面包，所以已经准备好了哦。今天做了香喷喷的吐司，还加了主人最喜欢的花生酱和蜂蜜呢！(≧∇≦)ﾉ
```

## 格式化输出
创建一个模型，并设置输出类型为该模型，这时输出就是该类型
```python
class CommandGenerate(BaseModel):
    command: str
    args: list[str]
    other_args_tip: str = Field(..., description="此命令的其他可推荐的参数")


agent = Agent(
    model=model,
    system_prompt="你是一个Linux命令生成工具，请根据用户输入生成一个Linux命令",
    output_type=CommandGenerate,
)


resp = agent.run_sync("创建用户kgg")
print(resp.output)
print(resp.output.command)
```
输出
```text
command='useradd' args=['kgg'] other_args_tip='可以使用 -m 参数来创建用户的家目录，例如：useradd -m kgg'
useradd
```
到这，就可以配合以前的[uv文章](用uv管理开发环境.md)，创造出属于自己的命令行工具了，
比如我写个`ai.py`，照着上面的例子补充一下，再用uv打包，安装，得到一个ai命令，
以后忘记什么命令都不用搜索了，直接`ai 杀掉占用8080端口的进程`
