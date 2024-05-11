from typing import TYPE_CHECKING
# pip install customtkinter
from customtkinter import CTk, CTkLabel, CTkTextbox, CTkEntry, CTkButton, CTkFrame

if TYPE_CHECKING:
    from Client import Client


# noinspection PyProtectedMember
class Window:
    def __init__(self, client: "Client"):
        self.client = client
        self.root = CTk()
        self.root.title("局域网聊天房")
        # 名字行
        info_frame = CTkFrame(self.root)
        info_frame.grid(row=0, column=0, sticky="w")
        CTkLabel(info_frame, text="名字").grid(row=0, column=0)
        self.name_entry = CTkEntry(info_frame)
        self.name_entry.insert(0, self.client.username)
        self.name_entry.grid(row=0, column=1)
        self.name_entry.bind("<Return>", self.change_name)
        # 聊天框
        self.text_box = CTkTextbox(self.root, height=300)
        self.text_box._textbox["state"] = "disabled"
        self.text_box.grid(row=1, column=0, sticky="nsew")
        self.text_box.tag_config("red", foreground="red")
        # 输入框
        input_frame = CTkFrame(self.root)
        input_frame.grid(row=2, column=0)
        self.input_box = CTkEntry(input_frame)
        self.input_box.grid(row=0, column=0)
        self.input_box.bind("<Return>", self.input)
        self.enter_button = CTkButton(input_frame, text="发送", width=120, command=self.input)
        self.enter_button.grid(row=0, column=1)

    def print(self, text: str, tags=None):
        self.text_box._textbox["state"] = "normal"
        self.text_box.insert("end", text + "\n", tags)
        self.text_box._textbox["state"] = "disabled"

    def tip(self, text: str):
        self.print(text, "red")

    def set_name_entry(self, text: str):
        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, text)

    def change_name(self, _=None):
        self.client.rename(self.name_entry.get())

    def input(self, _=None):
        text = self.input_box.get()
        if text:
            self.client.chat(text)
            self.input_box.delete(0, "end")

    def mainloop(self):
        self.root.mainloop()
