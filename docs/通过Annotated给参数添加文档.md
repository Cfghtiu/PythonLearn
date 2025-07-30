# 通过Annotated给参数添加文档
如果你不小心点进FastAPI这个类的源码，就会看到Annotated的影子
```python
debug: Annotated[
    bool,
    Doc(
        """
        Boolean indicating if debug tracebacks should be returned on server
        errors.
        """
    ),
] = False,
```
将参数的说明写在类型注解中，这样函数的注释可以专注的讲解函数的作用，而不是介绍参数的作用

## Annotated用法
新版本可以从typing中导入，旧版本需要安装typing_extensions
```python
from typing import Annotated

def openf(file: Annotated[str, ".zip suffix"]):
    """打开zip文件"""
```
虽然这个注释本身不会改变函数的作用，但是比起在函数注释中写参数作用，这个注释会更清晰

比起用井号注释，Annotated还有个特点是可以获取中括号里面的内容
```python
class GameArguments:
    """游戏参数，默认全无"""
    resolution_width: Annotated[int, "游戏窗口宽度"] = -1
    resolution_height: Annotated[int, "游戏窗口高度"] = -1
    quickPlayPath: Annotated[str, "快速游玩路径"] = ""
    quickPlaySingleplayer: Annotated[str, "单人快速游玩参数"] = ""
    quickPlayMultiplayer: Annotated[str, "多人快速游玩参数"] = ""
    quickPlayRealms: Annotated[str, "领域快速游玩参数"] = ""
    is_demo_user: Annotated[bool, "是否为演示用户"] = False

from inspect import get_annotations
anno = get_annotations(GameArguments)  # 3.9版本直接GameArguments.__annotations__
for k, v in anno.items():
    print(f'{k}: type={v.__args__[0].__name__}, desc={v.__metadata__[0]}')
```
输出
```text
resolution_width: type=int, desc=游戏窗口宽度
resolution_height: type=int, desc=游戏窗口高度
quickPlayPath: type=str, desc=快速游玩路径
quickPlaySingleplayer: type=str, desc=单人快速游玩参数
quickPlayMultiplayer: type=str, desc=多人快速游玩参数
quickPlayRealms: type=str, desc=领域快速游玩参数
is_demo_user: type=bool, desc=是否为演示用户
```

## 与pydantic配合
需要验证age的时候，可以使用Annotated，或者直接age = Field(ge=18)
```python
from typing import Annotated
from pydantic import BaseModel, Field

class UserCreateSchema(BaseModel):
    username: str
    age: Annotated[int, Field(ge=18)]

UserCreateSchema(username="asdasd", age=0)
```
这里要求age大于等于18，但输入是0时就会出错
```text
pydantic.error_wrappers.ValidationError: 1 validation error for UserCreateSchema
age
  ensure this value is greater than or equal to 18 (type=value_error.number.not_ge; limit_value=18)
```

## 与fastapi配合
自动依赖注入，比手动`db: Session = Depends(get_db)`方便
```python
from typing import Annotated
from fastapi import FastAPI, Depends

DbDependency = Annotated[Session, Depends(get_db)]

@app.post("p")
def p(db: DbDependency):
    ...
```