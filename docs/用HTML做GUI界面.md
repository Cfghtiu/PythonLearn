# 用HTML做GUI界面
你熟悉几个GUI库？
- tkinter
- PyQt
- wxPython

写起来复杂吗？反正现在我都用AI写的，但如果是简单的输入框，你用另外一个库写起来会简单很多

### streamlit
**优点**：写起来最简单，仅用于页面，可展示pandas数据  
**缺点**：仅支持`streamlit`命令运行程序，难以嵌入进综合项目

看看一个登录页面吧
```python
import streamlit as st
st.title("用户登录")
# 表单
with st.form("login_form"):
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    # 记住密码和立即注册在一行
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("[立即注册](#)")
    with col2:
        remember = st.checkbox("记住密码")
    login_button = st.form_submit_button("登录")

# 处理登录逻辑
if login_button:
    if username and password:
        st.success(f"欢迎回来，{username}！")
    else:
        st.error("请输入用户名和密码")
```
写一个AI对话页面还是可以的

## nicegui
**优点**：可以嵌入进项目，代码更符合GUI风格  
**缺点**：相比`streamlit`，写起来比较复杂，页面需要手动美化，启动慢

看看一个登录页面吧
```python
from nicegui import ui

username = ui.input('用户名')
password = ui.input('密码', password=True)

with ui.row():
    remember = ui.checkbox('记住密码')
    ui.link('注册', '#')

def login():
    if username.value and password.value:
        ui.notify(f'欢迎 {username.value}')
    else:
        ui.notify("请输入用户名和密码")
        
ui.button('登录', on_click=login)
ui.run()
```

如果你希望将它嵌入进自己的程序，不再是网页，可以这样写
```python
from nicegui import app
def login():
    app.shutdown()
...  # 页面
if __name__ == '__main__':
    a = input("输入用户名：")
    username.value = a
    ui.run(reload=False, native=True)
    print(1)
```
这里输入用户名后创建窗口，关闭时候会打印1

nicegui和streamlit一样，本质都是页面，而nicegui的GUI界面依靠pywebview需要安装，用于显示基础元素还行，不能做太过复杂的东西  
更复杂的还是用老牌库好点
