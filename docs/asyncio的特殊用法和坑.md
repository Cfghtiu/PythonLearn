# asyncio的特殊用法和坑
##  坑1: 不关闭资源，导致运行结束时报错
结合httpx可以做到异步获取网页内容
```python
import asyncio
import httpx

async def main():
    client = httpx.AsyncClient()
    resp = await client.get("https://www.baidu.com")
    print(resp.text)

asyncio.run(main())
```
httpx.AsyncClient在使用完后应该关闭，否则就会出现`RuntimeError: Event loop is closed`  
正确做法应该是`async with httpx.AsyncClient() as client:`
又或者在函数结束的时候调用`await client.aclose()`

## 坑2: 同步代码向事件循环添加任务
我们需要一个线程来运行任务，并等待返回结果
```python
import asyncio
import threading
import time

def thread_task(future):
    time.sleep(1)
    future.set_result(1)
    print("thread task done")

async def main():
    future = asyncio.Future()
    threading.Thread(target=thread_task, args=(future, )).start()
    await future
    print(future.result())


asyncio.run(main())
```
如果运行这个代码，将永远不会停下来，因为线程设置result后没有通知事件循环，事件循环就一直等待。  
修复方法是将当前事件循环`loop`传给线程，线程通过`loop.call_soon_threadsafe(method, *args)`添加任务到事件循环中  
于是上方代码可以改几行
```python
import asyncio
import threading
import time

def thread_task(future, loop):
    time.sleep(1)
    loop.call_soon_threadsafe(future.set_result, 1)
    print("thread task done")

async def main():
    future = asyncio.Future()
    threading.Thread(target=thread_task, args=(future, asyncio.get_running_loop())).start()
    await future
    print(future.result())

asyncio.run(main())
```
## 坑3：没创建任务导致异步=同步
假如现在有个数据需要异步处理，于是执行下面代码
```python
import asyncio

async def task_add(x, y):
    await asyncio.sleep(1)
    print(x + y)

async def main():
    l = [(1, 2), (5, 6)]
    for x, y in l:
        await task_add(x, y)

asyncio.run(main())
```
上面代表并不会同时启动两个任务，而是顺序执行，因为没有创建任务，所以`task_add`被同步调用了  
正确做法是通过`asyncio.create_task(task_add(x, y))`，如果需要获取结果，可以通过下面代码
```python
import asyncio

async def task_add(x, y):
    await asyncio.sleep(1)
    return x + y

async def main():
    l = [(1, 2), (5, 6)]
    tasks = []
    for x, y in l:
        tasks.append(asyncio.create_task(task_add(x, y)))
    print(await asyncio.gather(*tasks))  # [3, 11]

asyncio.run(main())
```

## 特殊用法1：在另一个线程运行事件循环
我们需要一个线程来运行loop，然后给loop添加任务，最后关闭，代码如下
```python
import asyncio
import threading
import time

async def task():
    asyncio.set_event_loop(loop)  # 如果有多个线程运行loop，此方法用于设置当前线程的loop，避免隐藏错误
    await asyncio.sleep(1)
    print(1)

# 创建loop，并运行在线程中，run_forever会在遇到stop时停止，此时线程也结束
loop = asyncio.new_event_loop()
loop_thread = threading.Thread(target=loop.run_forever, daemon=True)
loop_thread.start()
# asyncio.run_coroutine_threadsafe用于将协程对象加入loop
asyncio.run_coroutine_threadsafe(task(), loop)
time.sleep(2)
# loop.call_soon_threadsafe用于在loop中运行callback
loop.call_soon_threadsafe(loop.stop)
loop_thread.join()
# 只能在stop后才能关闭loop
loop.close()
```