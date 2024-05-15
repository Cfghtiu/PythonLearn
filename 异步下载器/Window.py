import subprocess
from pathlib import Path
from urllib.parse import urlparse

from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QFormLayout, QHBoxLayout, QFileDialog, QStackedWidget
from qfluentwidgets import (
    TabBar, StrongBodyLabel, CaptionLabel, LineEdit,
    ProgressBar, HyperlinkLabel, PushButton, TabCloseButtonDisplayMode,
    Flyout, IndeterminateProgressBar, TeachingTip, InfoBarIcon, TeachingTipTailPosition)

from Options import Options


# noinspection PyTypeChecker
class Window(QWidget):
    """窗口，只负责窗口逻辑"""

    def __init__(self):
        super().__init__()
        self._default_save_path = str(Path.home() / "Downloads")

        # 输入表单
        self.frame = QFrame(self)
        self.tab_bar = TabBar(self)
        self.url_line = LineEdit()
        self.save_line = LineEdit()
        self.save_line.setText(self._default_save_path)
        self.file_line = LineEdit()
        self.proxy_line = LineEdit()
        # 选择文件夹按钮
        self.select_label = HyperlinkLabel("选择")
        self.download_button = PushButton()
        self.open_save_button = PushButton("打开文件夹")
        # 进度条
        self.progress_bar_stack = QStackedWidget()
        self.progress_bar = ProgressBar(useAni=True)
        self.indeterminate_progress_bar = IndeterminateProgressBar(start=False)
        # 绑定信号，设置ui
        self.bind_signals()
        self.setup_ui()

        self.add_tab()

    def start_download(self, options: Options):
        raise NotImplementedError()

    def stop_download(self, options: Options):
        raise NotImplementedError()

    def on_download_button_clicked(self):
        options = self.tab_bar.currentTab().routeKey()
        self.save_option(options)
        if not options.finished:  # 没完成就是下载按钮，完成了就是打开按钮
            if not options.started:  # 没开始就是下载按钮，开始了就是停止按钮
                try:
                    options.check()
                except AssertionError as e:
                    reason = e.args[0]
                    if reason == 0:
                        self.tip(self.url_line, "链接呢？", "我要下什么啊啊啊啊？")
                    elif reason == 1:
                        self.tip(self.save_line, "保存路径呢？", "我要存到哪里啊啊啊啊？")
                    elif reason == 2:
                        self.tip(self.file_line, "文件名呢？", "我要叫什么啊啊啊啊？")
                    elif reason == 3:
                        self.tip(self.url_line, "网址？", "你管这叫网址？")
                    elif reason == 4:
                        self.tip(self.save_line, "保存路径？", "您这保存路径是文件夹吗？")
                    elif reason == 5:
                        self.tip(self.proxy_line, "代理？", "代理得是一个http地址:端口？")
                else:
                    try:
                        self.start_download(options)
                    except Exception as e:
                        self.tip(self.download_button, "下载失败", str(e))
            else:
                self.stop_download(options)
        else:
            subprocess.run(f"start {Path(options.save_path, options.file_name)}", shell=True)
        self.load_option(options)

    def tip(self, target, title, content):
        Flyout.create(
            title=title,
            content=content,
            target=target,
            parent=self
        )

    def teaching_tip(self, target, title, content):
        TeachingTip.create(
            target=target,
            icon=InfoBarIcon.SUCCESS,
            title=title,
            content=content,
            isClosable=True,
            tailPosition=TeachingTipTailPosition.BOTTOM,
            duration=7000,
            parent=self
        )

    def on_tab_bar_clicked(self, index):
        """只在点击tab时触发，保存当前选项"""
        options = self.tab_bar.currentTab().routeKey()
        self.save_option(options)

    def on_change_tab(self, index):
        """在每次切换tab时都会调用，即便是通过remove_tab切换到的"""
        options = self.tab_bar.currentTab().routeKey()
        self.load_option(options)
        return options

    def update_option(self):
        self.load_option(self.tab_bar.currentTab().routeKey())

    def load_option(self, options: Options):
        self.url_line.setText(options.url)
        self.save_line.setText(options.save_path or self._default_save_path)
        self.file_line.setText(options.file_name)
        self.proxy_line.setText(options.proxy)
        if options.finished:
            self.download_button.setText("打开文件")
        else:
            self.download_button.setText("开始下载" if not options.started else "停止下载")

    def save_option(self, options: Options):
        options.url = self.url_line.text()
        options.save_path = self.save_line.text()
        options.file_name = self.file_line.text()
        options.proxy = self.proxy_line.text()

    def add_tab(self) -> Options:
        old = self.tab_bar.currentTab()
        if old:
            self.save_option(old.routeKey())

        options = Options()
        self.tab_bar.addTab(options, "新建下载项")
        self.tab_bar.setCurrentTab(options)
        if len(self.tab_bar.items) != 1:  # 允许关闭选项
            self.tab_bar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.ALWAYS)
        self.on_change_tab(self.tab_bar.currentIndex())

    def remove_tab(self, index) -> Options:
        options = self.tab_bar.tabItem(index).routeKey()
        self.tab_bar.removeTab(index)
        if len(self.tab_bar.items) == 1:  # 禁止关闭选项
            self.tab_bar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.NEVER)
        self.on_change_tab(self.tab_bar.currentIndex())
        if options.started:  # 如果已经启动
            self.stop_download(options)
            self.tip(self, "停止下载", f"关闭了{options.file_name}下载项目")
        return options

    def update_progress_bar(self):
        options = self.tab_bar.currentTab().routeKey()
        if options.failed:  # 失败
            self.progress_bar.setCustomBarColor("red", "red")
            if options.file_size == 0:  # 如果是未知文件大小，就设置一般进度条
                self.progress_bar_stack.setCurrentWidget(self.progress_bar)
                self.progress_bar.setVal(options.file_size // 2)
        elif options.finished:  # 完成就是满进度条
            self.progress_bar_stack.setCurrentWidget(self.progress_bar)
            self.progress_bar.setVal(options.file_size)
        else:  # 进行中
            self.progress_bar.setCustomBarColor(QColor(), QColor())
            self.indeterminate_progress_bar.setCustomBarColor(QColor(), QColor())

            if options.file_size != -1:  # -1代表没开始下
                if options.file_size == 0:  # 0代表未知文件大小
                    self.progress_bar_stack.setCurrentWidget(self.indeterminate_progress_bar)
                    self.indeterminate_progress_bar.start()
                else:  # 有文件大小
                    self.indeterminate_progress_bar.stop()
                    self.progress_bar_stack.setCurrentWidget(self.progress_bar)
                    self.progress_bar.setMaximum(options.file_size)
                    self.progress_bar.setValue(options.download_size)
            else:
                self.indeterminate_progress_bar.stop()  # 没开始下
                self.progress_bar_stack.setCurrentWidget(self.indeterminate_progress_bar)
                self.progress_bar.setValue(0)

    # noinspection PyUnresolvedReferences
    def bind_signals(self):
        self.tab_bar.tabAddRequested.connect(self.add_tab)
        self.tab_bar.tabCloseRequested.connect(self.remove_tab)
        self.tab_bar.currentChanged.connect(self.on_change_tab)
        self.tab_bar.tabBarClicked.connect(self.on_tab_bar_clicked)
        self.url_line.textChanged.connect(self.on_url_line_text_changed)
        self.select_label.clicked.connect(self.on_select_label_clicked)
        self.file_line.textChanged.connect(self.on_file_line_text_changed)
        self.open_save_button.clicked.connect(self.on_open_save_button_clicked)
        self.download_button.clicked.connect(self.on_download_button_clicked)

    def setup_ui(self):
        self.setMinimumWidth(400)
        self.setWindowTitle("下崽器 - by 233星空xt")
        self.setWindowIcon(QIcon("icon.ico"))
        self.setStyleSheet("""
            Window{background: white}
            QFrame{
                background: rgb(242,242,242);
                border-radius: 8px;
            }
        """)
        self.tab_bar.setTabMaximumWidth(120)
        self.tab_bar.setMovable(True)
        self.tab_bar.setTabShadowEnabled(True)
        self.tab_bar.setScrollable(True)
        self.tab_bar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.NEVER)
        # 表单
        form_layout = QFormLayout(self.frame)
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(30)
        form_layout.addRow(StrongBodyLabel("下载地址"), self.url_line)

        save_layout = QHBoxLayout()
        save_layout.setSpacing(5)
        save_layout.addWidget(self.save_line)
        save_layout.addWidget(self.select_label)
        form_layout.addRow(StrongBodyLabel("保存路径"), save_layout)

        form_layout.addRow(CaptionLabel("文件名"), self.file_line)
        form_layout.addRow(CaptionLabel("代理"), self.proxy_line)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.open_save_button)
        form_layout.addRow(button_layout)

        self.progress_bar_stack.addWidget(self.progress_bar)
        self.progress_bar_stack.addWidget(self.indeterminate_progress_bar)
        form_layout.addRow(self.progress_bar_stack)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tab_bar)
        layout.addWidget(self.frame)

    def on_open_save_button_clicked(self):
        subprocess.run(f'explorer /select, {Path(self.save_line.text(), self.file_line.text())}')

    def on_file_line_text_changed(self, text):
        if text:
            self.tab_bar.currentTab().setText(text)
        else:
            self.tab_bar.currentTab().setText("新建下载项")

    def on_select_label_clicked(self):
        self.save_line.setText(QFileDialog.getExistingDirectory(self).replace("/", "\\"))

    def on_url_line_text_changed(self, text):
        result = urlparse(text)
        if all([result.scheme, result.netloc, result.path]) and not self.file_line.text():
            filename = result.path.split("/")[-1]
            self.file_line.setText(filename)
