import json
import tkinter as tk
from tkinter import filedialog, messagebox
from form import Get_Data, Creat_Button, Creat_Checkbutton
from generate import Generate_File

if __name__ == "__main__":
    """創建主介面"""
    lang, data = Get_Data()
    change_config_dict = {}

    # 創建主窗口
    root = tk.Tk()
    root.title(lang["main.root.title"])
    root.iconbitmap("data/anyway_is_ico.ico")

    # 路徑 txt
    def Save_Path(event):
        if path_txt.edit_modified():
            path_txt.edit_modified(False)
            data["path"] = path_txt.get("1.0", "end-1c")
            with open("data/data.json", "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

    path_txt = tk.Text(root, width=60, height=1)
    path_txt.grid(row=0, column=0, padx=10, pady=10, columnspan=3)
    path_txt.bind("<<Modified>>", Save_Path)
    path_txt.insert(tk.END, data["path"])

    # '生成'按鈕
    def load_Generate_File():
        Generate_File(path_txt.get("1.0", "end-1c"))

    change_config_dict["button.generate"] = Creat_Button(
        root, "main.button.generate", load_Generate_File
    )
    change_config_dict["button.generate"].grid(row=1, column=0, padx=10, pady=10)

    def select_path(open_method: str):
        """選擇檔案 並以其路徑覆蓋 path_txt (取消選擇則不覆蓋
        Args:
            open_method (str): 選擇打開的類型
        """
        file_path = getattr(filedialog, open_method)()
        if len(file_path) > 0:
            path_txt.delete("1.0", "end")
            path_txt.insert("1.0", file_path)

    # '選擇檔案'按鈕
    change_config_dict["button.select_cdb"] = Creat_Button(
        root, "main.button.select_cdb", lambda: select_path("askopenfilename")
    )
    change_config_dict["button.select_cdb"].grid(row=1, column=1, padx=10, pady=10)
    # '選擇資料夾'按鈕
    change_config_dict["button.select_file"] = Creat_Button(
        root, "main.button.select_file", lambda: select_path("askdirectory")
    )
    change_config_dict["button.select_file"].grid(row=1, column=2, padx=10, pady=10)

    # 函數生成處理 groupbox
    group_func_decision = tk.LabelFrame(
        root, text=lang["main.LabelFrame.func_decision"], padx=10, pady=10
    )
    group_func_decision.grid(row=3, column=0, padx=10, pady=10, sticky="n")
    change_config_dict["LabelFrame.func_decision"] = group_func_decision

    # 'con', 'cos', 'tg', 'op' 勾選框
    def Gnerate_Func_Decision(typ: str):
        data["gnerate_" + typ] = "1" if func_decision_dict[typ].get() else "0"
        with open("data/data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    func_decision_dict: dict[str, tk.BooleanVar] = {}
    for ind, key in enumerate(["con", "cos", "tg", "op"]):
        func_decision_dict[key] = tk.BooleanVar(value=data["gnerate_" + key] == "1")
        tk.Checkbutton(
            change_config_dict["LabelFrame.func_decision"],
            text=key,
            variable=func_decision_dict[key],
            command=lambda k=key: Gnerate_Func_Decision(k),
        ).grid(row=ind // 2, column=ind % 2, sticky="w")

    # '生成函數大綱' 勾選框
    func_decision_dict["func"] = tk.BooleanVar(value=data["gnerate_func"] == "1")
    checkbutton_func_decision = tk.Checkbutton(
        change_config_dict["LabelFrame.func_decision"],
        text=lang["main.checkbutton.gnerate_func"],
        variable=func_decision_dict["func"],
        command=lambda: Gnerate_Func_Decision("func"),
    )
    checkbutton_func_decision.grid(row=2, column=0, columnspan=2, sticky="w")
    change_config_dict["checkbutton.gnerate_func"] = checkbutton_func_decision

    # 重複項目處理 groupbox
    group_repeat_decision = tk.LabelFrame(
        root, text=lang["main.LabelFrame.repeat_decision"], padx=10, pady=10
    )
    group_repeat_decision.grid(row=3, column=1, padx=10, pady=10, sticky="n")
    change_config_dict["LabelFrame.repeat_decision"] = group_repeat_decision

    # '總是覆蓋檔案', '總是跳過檔案' 勾選框
    def Select_File_Decision(typ: str):
        data["repeat_decision"] = "ask"
        if repeat_decision_dict[typ].get():
            data["repeat_decision"] = typ
            typ = "skip" if typ == "cover" else "cover"
            repeat_decision_dict[typ].set(False)
        with open("data/data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    repeat_decision_dict: dict[str, tk.BooleanVar] = {}
    for row, key in enumerate(["cover", "skip"]):
        repeat_decision_dict[key] = tk.BooleanVar(value=data["repeat_decision"] == key)
        checkbutton = Creat_Checkbutton(
            change_config_dict["LabelFrame.repeat_decision"],
            "main.checkbutton." + key,
            repeat_decision_dict[key],
            lambda k=key: Select_File_Decision(k),
        )
        checkbutton.grid(row=row, column=0)
        change_config_dict["checkbutton." + key] = checkbutton
        
    # 字體轉換
    def Lang_Change():
        lang, data = Get_Data()
        data["lang"] = "zh_tw" if data["lang"] == "zh_cn" else "zh_cn"
        with open("data/data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        lang, data = Get_Data()
        # 改語言
        root.title(lang["main.root.title"])
        for key, item in change_config_dict.items():
            item.config(text=lang["main." + key])

    button_lang_change = Creat_Button(root, "main.button.lang_change", Lang_Change)
    button_lang_change.grid(row=3, column=2, padx=10, pady=10, sticky="n")
    change_config_dict["button.lang_change"] = button_lang_change

    # 啟動主循環
    root.mainloop()
