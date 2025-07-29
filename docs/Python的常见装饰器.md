# Python的常见装饰器
## 缓存: cache, lru_cache
缓存装饰器，用于缓存函数的返回值，下次调用时，会先从缓存中获取结果，如果缓存中不存在，则调用函数，并将结果缓存起来。  
cache和lru_cache的区别在于lru_cache会抛弃旧的缓存，因为cache就是lru_cache(maxsize=None)

```python
import time
from functools import lru_cache

@lru_cache(maxsize=5)
def calculate(n):
    time.sleep(1)  # 模拟耗时操作
    print(n)

calculate(1)
calculate(1)  # 这里不会打印1，因为会返回缓存中的结果，没调用函数
calculate(2)
```

## 上下文管理: contextmanager
用于将函数包装成上下文管理器，可以用with语句来使用
```python
from contextlib import contextmanager

@contextmanager
def db() -> Session:
    session = Session()
    try:
        yield session
        session.commit()  # 自动提交
    except Exception:
        session.rollback()  # 出错自动回滚
    finally:
        session.close()  # 关闭session

with db() as session:
    session.add(...)
```

## 属性: property
在类中定义属性，属性的getter和setter和deleter方法

```python
import datetime

class Person:
    age: int = 5

    @property
    def birth_year(self) -> int:
        return datetime.date.today().year - self.age
    
    @birth_year.setter
    def birth_year(self, value: int):
        self.age = datetime.date.today().year - value

p = Person()
print(p.birth_year)
p.birth_year = 2000
print(p.age)
```
另外functools里还有个cached_property，相当于有缓存的property


## 函数装饰: warps
用于创建名字注释和其他函数一样的函数
```python
from functools import wraps
import time

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} took {end - start} seconds")
        return result
    return wrapper

@timeit
def calculate(n):
    ...

print(calculate)  # <function calculate at 0x0196AA00>
```
如果不使用warps呢？那么打印的结果就是<function timeit.<locals>.wrapper at ...>


## 类方法: classmethod
用于定义类的方法，类方法第一个参数是cls，表示类本身
```python
class AA:
    @classmethod
    def pt(cls):
        print(cls)

AA.pt()  # 打印class
AA().pt()  # 一样，打印class
```

## 静态方法: staticmethod
和类方法很像，但没有必要的参数
```python
class BB:
    @staticmethod
    def pt():
        print("?")

BB.pt()  # 打印问号
BB().pt()  # 打印问号
```

## 退出前清理: atexit.register
在Python退出前执行清理工作
```python
import atexit

@atexit.register
def cleanup():
    print("Cleaning up...")
```
最后会打印Cleaning up...

## overload
假如你的函数的调用有两种方法，可以用overload讲解一下
```python
from typing import overload

@overload
def func(arg1: int): ...

@overload
def func(arg1: float, arg2: float): ...

def func(*args):  # 具体实现
    return args
```
这时候在调用func时，IDE会提示两种调用方法
```text
形参未填
可能的被调用方:
func(arg1: int)
func(arg1: float, arg2: float) 
```
