import typer
import logging
import asyncio
from functools import partial


async def handle_conn(target_ip: str, target_port: int, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    conn_addr = writer.get_extra_info('peername')
    conn_addr = f"{conn_addr[0]}:{conn_addr[1]}"
    # 连接目标地址
    try:
        target_reader, target_writer = await asyncio.open_connection(target_ip, target_port)
        logging.info(f"{conn_addr}已连接{target_ip}:{target_port}")
    except ConnectionRefusedError as e:  # 连接出错时
        logging.error(f"{conn_addr}连接{target_ip}:{target_port}被拒绝:{e}")
        return
    # 转发
    try:
        await asyncio.gather(
            forward(reader, target_writer),
            forward(target_reader, writer)
        )
    except EOFError:  # 关闭连接时
        logging.info(f"{conn_addr}已断开")
    except Exception as e:  # 转发出错时
        import traceback
        traceback.print_exc()
        logging.error(f"{conn_addr}与{target_ip}:{target_port}通信异常:{e}")
    finally:
        target_writer.close()
        writer.close()


async def forward(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    while True:
        data = await reader.read(1024)
        if not data:
            await writer.drain()
            raise EOFError
        writer.write(data)


async def main(
    bind_port: int = typer.Argument(min=1, max=65535),
    target_ip: str = typer.Argument(metavar="IP"),
    target_port: int = typer.Argument(min=1, max=65535),
    bind_ip: str = typer.Option("0.0.0.0", metavar="IP")
):
    """端口转发程序"""
    handler = partial(handle_conn, target_ip, target_port)
    async with await asyncio.start_server(handler, bind_ip, bind_port) as server:
        logging.info(f"开始监听 {bind_ip}:{bind_port}")
        await server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    from functools import wraps
    # 方法包装，让typer能够运行协程，这种写法比较神奇，推荐只在个人项目中使用
    typer.run(wraps(main)(lambda *args, **kwargs: asyncio.run(main(*args, **kwargs))))
