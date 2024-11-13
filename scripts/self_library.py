import json
import tkinter
import os
import re
from tkinter import ttk


def Get_Globals() -> tuple[dict, dict]:
    """更新語言文件 LANG 以及全局變數 DATA"""
    with open("data/data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    with open(f"data/{data['lang']}.json", "r", encoding="utf-8") as file:
        lang = json.load(file)
    return lang, data


def Creat_Checkbutton(root: tkinter.Tk, txt: str, var, func="") -> tkinter.Checkbutton:
    """創建勾選按鈕"""
    return tkinter.Checkbutton(root, text=txt, variable=var, command=func)


def Creat_Button(root: tkinter.Tk, txt: str, func="") -> tkinter.Button:
    """創建按鈕"""
    return tkinter.Button(root, text=txt, command=func, width=15)


class Card:
    """cdb 資料轉化"""

    def __init__(self, texts: list[str], script_path: str):
        self.cm: str = f"c{texts[0]}.lua"
        self.name: str = texts[1]
        self.desc: str = texts[2]
        self.path: str = os.path.join(script_path, f"c{texts[0]}.lua")


class Check_Card:
    """用於選擇覆蓋文件使用"""

    def __init__(
        self, button: tkinter.Checkbutton, var: tkinter.BooleanVar, card: Card
    ):
        self.button: tkinter.Checkbutton = button
        self.var: tkinter.BooleanVar = var
        self.card: Card = card


class Funcs:
    """functions.txt 資料轉化"""

    def __init__(self, name_line: str = ""):
        # 普通指令卡的发动
        self.name = name_line
        self.func: str = ""
        self.param: dict = {}
        self.res: str = ""
        self.info: str = ""

    def Set_Func(self, func_line: str):
        # vgd.SpellActivate(c, m*, op*, cost*, con*)
        match = re.match(r"([\w\.]+)\(([^)]*)\)", func_line)
        self.func = match.group(1)  # vgd.SpellActivate
        for name in match.group(2).split(", "):  # c, m*, op*, cost*, con*
            name = name[:-1] if (nilable := "*" in name) else name
            self.param[name] = {"nilable": nilable}

    def Set_Param_Detail(self, param_line: str):
        # m=c:GetOriginalCode() N 储存提示脚本的卡号
        name, typ, info = param_line.strip().split(" ", 2)
        default = ""
        if "=" in name:
            name, default = name.split("=")
        self.param[name]["type"] = typ
        self.param[name]["default"] = default
        self.param[name]["info"] = info

    def Get_Func_Line(
        self,
        nil_to_nil: bool = False,
        default_to_nil: bool = False,
        delete_nil: bool = False,
    ) -> str:
        func_line = self.func + "("
        temp_val = ""
        for name, val in self.param.items():
            if val["nilable"] and nil_to_nil or default_to_nil and val["default"]:
                temp_val += "nil, "
                continue
            func_line += temp_val + name + ", "
            temp_val = ""
        if not delete_nil:
            func_line += temp_val
        return func_line[:-2] + ")"

    def Match(self, find_str: str) -> bool:
        if find_str in self.name:
            return True
        find_str = find_str.lower()
        if find_str in self.func.lower():
            return True
        return False

    def Insert_Param(self, param_view: ttk.Treeview):
        param_view.config(height=len(self.param.keys()))
        for item in param_view.get_children():
            param_view.delete(item)
        for name, param in self.param.items():
            param_typ = param["type"] + ("|nil" if param["nilable"] else "")
            param_default = (
                param["default"] or "nil" if param["nilable"] else "此欄位必填"
            )
            param_view.insert(
                "", "end", values=[name, param_typ, param_default, param["info"]]
            )
