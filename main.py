import tkinter
from tkinter import ttk
from PIL import Image
from PIL import ImageTk

configPath = "config/config.json"
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if os.path.exists(configPath):
    configBytes = open(configPath, "rb").read()
    import json

    config = json.loads(configBytes)
else:
    config = {}
# loading window
theme = config.get("THEME", "默认主题")
if theme == "默认主题":
    root = tkinter.Tk()
else:
    from ttkbootstrap import Style

    style = Style()  # darkly cyborg minty
    root = style.master
    style.theme_use(theme)
try:
    import ctypes

    # 获取屏幕的缩放因子
    ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
    # 设置程序缩放

    # 告诉操作系统使用程序自身的dpi适配
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root.tk.call("tk", "scaling", ScaleFactor / 75)
    s = ttk.Style()
    # s.theme_use('classic')

    # Add the rowheight
    s.configure("Treeview", rowheight=20 * ScaleFactor // 100)
except:
    print("高清缩放失败")

root.geometry("1x1")
# root.iconify()
root.overrideredirect(True)
root.update()
iconPath = "config/ico.ico"
image = Image.open(iconPath)
image = ImageTk.PhotoImage(image)


# img = tkinter.PhotoImage(file=iconPath)
class LoadingframeWidget(ttk.Frame):
    def __init__(self, master=None, **kw):
        super(LoadingframeWidget, self).__init__(master, **kw)
        self.imageLabel = ttk.Label(self)
        self.imageLabel.configure(text=" ", image=image)
        self.imageLabel.pack(side="left")
        label2 = ttk.Label(self)
        label2.configure(font="{黑体} 24 {}", text="背包编辑工具启动中...")
        label2.pack(side="left")
        self.configure(height=200, width=200)
        self.pack(expand="true", side="top")


loadingWin = tkinter.Toplevel(root)
loadingFrame = LoadingframeWidget(loadingWin)
loadingWin.title("loading")
# loadingWin.geometry('300x100')
loadingWin.resizable(False, False)
# loadingWin.attributes('-topmost',True)
loadingWin.overrideredirect(True)
loadingWin.update()
loadingWin.update_idletasks()
loadingWin.geometry(
    "+%d+%d"
    % (
        loadingWin.winfo_screenwidth() // 2 - loadingWin.winfo_width() // 2,
        loadingWin.winfo_screenheight() // 2 - loadingWin.winfo_height() // 2,
    )
)
loadingWin.update()
loadingWin.update_idletasks()


def load_callback():
    loadingWin.attributes("-topmost", False)
    loadingWin.destroy()


if __name__ == "__main__":
    import dnfpkgtool.__main__ as main

    main.run(load_callback, root)
