# 以防你不知道Python的特殊用法

## 海象运算符
3.9版本开始，Python引入了海象运算符  
给个代码就知道怎么用了
```python
print((a=1,))  # syntax error
print((a:=1,))  # (1)
```
从这就能看出来，:=既能赋值，也能返回值
```python
a = (b:=1) + 1
print(a, b)  # 输出2 1
```
### 实际案例
比如命令行按Q退出
```python
while (text := input("(按Q退出):")) != "Q":
    print(text)
```

## 新的泛型语法
自3.12开始，泛型可以不再依靠typing.TypeVar
```python
def add[T: (int ,str)](a: T, b: T) -> T:
    return a + b

class Proxy[T]:
    def __init__(self, obj: T):
        ...
```
不建议使用这个，因为太新了，网上都没几个人介绍

## 单例模式
通过重写__new__方法实现
```python
class Runtime:
    __i: 'Runtime' = None
    def __new__(cls, *args, **kwargs):
        if cls.__i is None:
            cls.__i = super().__new__(cls)
        return cls.__i
print(Runtime() is Runtime())  # True
```

## 模块的__getattr__方法
假如在模块中定义函数__getattr__，则会在模块中找不到的属性时调用这个方法
```python
# a.py
a = 1
def __getattr__(item):
    return 2
# b.py
from a import a, b, c, d
print(a, b, c, d)  # 1 2 2 2
```

## ...
省略号，你懂吧
```python
def shutdown():
    ...
```
和pass一个用法，但...是一个可以使用的值(`a=...`)，NumPy中，可用于省略某些维度。

## for else
for else语句，当for循环正常结束，会执行else中的代码
```python
for i in range(10):
    if i == 5:
        break
else:
    print("没有break")
```
同理，while和try也能else语句