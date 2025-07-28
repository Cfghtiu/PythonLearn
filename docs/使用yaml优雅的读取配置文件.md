# 使用yaml优雅的读取配置文件

## yaml格式
yaml长这样
```yaml
name: "KGG"
age: 18
info:
  host: "your home"
  email: "xkgt@qq.com"
permissions:
  - "admin"
  - "user"
  - "666"
```
熟悉python的人可以看到这种缩进和格式很像dict

## 使用yaml
### 安装库
读取yaml格式的包名叫`pyyaml`，可通过`pip install pyyaml`安装
### 读取yaml格式
```python
string = """
name: "KGG"
info:
  host: "your home"
permissions:
  - "admin"
"""

import yaml
print(yaml.safe_load(string))
```
这里的string也可以是打开的文件  
这时候输出就是`{'name': 'KGG', 'info': {'host': 'your home'}, 'permissions': ['admin']}`

此外，看到safe_load就知道肯定还有个load方法，safe_load其实就是load(stream, SafeLoader)  
如果你需要其他Loader(比如可以执行代码的UnsafeLoader或支持1.1版本的FullLoader)，
可以直接用unsafe_load或full_load方法，或者load方法

## 优雅的使用配置
仅仅是这样读取还不够，在Pycharm中无法使用补全，可能会导致各种错误  
为了解决这个问题，我们可以使用其他库，又或者先简单的可以在代码内定义一个“结构”

首先，在python中定义配置的结构
```python
config = dict(
    name=str(),  # 这里如果不加括号，到时候补全时会提示缺少self
    password=str(),
    info=dict(
        host=str(),
        email=str()
    ),
    permissions=list[str]()
)
```
然后，覆盖
```python
config.update(yaml.safe_load(string))
```
这样无论是"name"还是upper，都可以被补全
```python
print(config["name"].upper())
```
但这样仍然有个问题，那就是对yaml数据没有校验，说不定文件的数据格式和我们要求的不一样呢？  
这时候就不能简单的靠dict定义格式了(不过说实话我挺喜欢这种写法，因为代码少，看着爽啊！)

## 使用dataclass+dacite或pydantic做数据校验
dataclass支持规范数据格式，且可设置默认值，但不支持校验数据类型，也不支持递归反序列化，而dacite作为轻量级的反序列化库，弥补了dataclass的缺点  
pydantic拥有dataclass+dacite的特性，还支持自定义(比如范围值)校验，但是是第三方库，常常用于web框架  

如果使用dataclass+dacite，我们需要安装一个`dacite`库`pip install dacite`，用于将dict转换成dataclass
```python
from dataclasses import dataclass
import dacite

@dataclass
class ConfigInfo:
    host: str

@dataclass
class Config:
    name: str
    info: ConfigInfo
    permissions: list[str]

import yaml
config = dacite.from_dict(Config, yaml.safe_load(string))
print(config.info.host)
# 序列化
from dataclasses import asdict
print(asdict(config))
```
如果使用pydantic，那结构的定义也差不多
```python
from pydantic import BaseModel

class ConfigInfo(BaseModel):
    host: str

class Config(BaseModel):
    name: str
    info: ConfigInfo
    permissions: list[str]

config = Config(**yaml.safe_load(string))
print(config.info.host)
# 序列化
print(config.dict())
```