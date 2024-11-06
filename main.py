import tkinter as tk
from tkinter import messagebox, filedialog
import json
import generate


# 獲取全局變數
with open("data/data.json", "r", encoding="utf-8") as file:
    DATA: dict = json.load(file)
with open(f"data/{DATA['lang']}.json", "r", encoding="utf-8") as file:
    LANG: dict = json.load(file)


def Creat_Button(root: tk.Tk, txt: str, func):
    return tk.Button(root, text=LANG[txt], command=func, width=15)


if __name__ == "__main__":
    # 創建主窗口
    root = tk.Tk()
    root.title(LANG["main.root.title"])

    # 路徑 txt
    def Save_Path(event):
        if path_txt.edit_modified():
            path_txt.edit_modified(False)
            DATA["path"] = path_txt.get("1.0", "end-1c")
            with open("data/data.json", "w", encoding="utf-8") as file:
                json.dump(DATA, file, ensure_ascii=False, indent=4)

    path_txt = tk.Text(root, width=60, height=1)
    path_txt.grid(row=0, column=0, padx=10, pady=10, columnspan=3)
    path_txt.bind("<<Modified>>", Save_Path)
    path_txt.insert(tk.END, DATA["path"])

    # '生成'按鈕
    def load_Generate_File():
        generate.Generate_File(path_txt.get("1.0", "end-1c"), DATA["repeat_decision"])

    Creat_Button(root, "main.button.generate", load_Generate_File).grid(
        row=1, column=0, padx=10, pady=10
    )

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
    Creat_Button(
        root, "main.button.select_cdb", lambda: select_path("askopenfilename")
    ).grid(row=1, column=1, padx=10, pady=10)
    # '選擇資料夾'按鈕
    Creat_Button(
        root, "main.button.select_file", lambda: select_path("askdirectory")
    ).grid(row=1, column=2, padx=10, pady=10)

    # 重複項目處理 groupbox
    group_repeat_decision = tk.LabelFrame(
        root, text=LANG["main.LabelFrame.repeat_decision"], padx=10, pady=10
    )
    group_repeat_decision.grid(row=3, column=0, padx=10, pady=10, sticky="n")

    # '總是覆蓋檔案', '總是跳過檔案' 勾選框
    def Select_File_Decision(typ: str):
        DATA["repeat_decision"] = "ask"
        if repeat_decision_dict[typ].get():
            DATA["repeat_decision"] = typ
            typ = "skip" if typ == "cover" else "cover"
            repeat_decision_dict[typ].set(False)
        with open("data/data.json", "w", encoding="utf-8") as file:
            json.dump(DATA, file, ensure_ascii=False, indent=4)

    repeat_decision_dict: dict[str, tk.BooleanVar] = {}
    for row, key in enumerate(["cover", "skip"]):
        repeat_decision_dict[key] = tk.BooleanVar(value=DATA["repeat_decision"] == key)
        tk.Checkbutton(
            group_repeat_decision,
            text=LANG["main.checkbutton." + key],
            variable=repeat_decision_dict[key],
            command=lambda k=key: Select_File_Decision(k),
        ).grid(row=row, column=0)

    # 函數生成處理 groupbox
    group_func_decision = tk.LabelFrame(
        root, text=LANG["main.LabelFrame.func_decision"], padx=10, pady=10
    )
    group_func_decision.grid(row=3, column=1, padx=10, pady=10, sticky="n")

    # 'con', 'cos', 'tg', 'op' 勾選框
    def Gnerate_Func_Decision(typ: str):
        DATA["gnerate_" + typ] = "1" if func_decision_dict[typ].get() else "0"
        with open("data/data.json", "w", encoding="utf-8") as file:
            json.dump(DATA, file, ensure_ascii=False, indent=4)

    func_decision_dict: dict[str, tk.BooleanVar] = {}
    for ind, key in enumerate(["con", "cos", "tg", "op"]):
        func_decision_dict[key] = tk.BooleanVar(value=DATA["gnerate_" + key] == "1")
        tk.Checkbutton(
            group_func_decision,
            text=key,
            variable=func_decision_dict[key],
            command=lambda k=key: Gnerate_Func_Decision(k),
        ).grid(row=ind // 2, column=ind % 2, sticky="w")

    # '生成函數大綱' 勾選框
    func_decision_dict["gnerate_func"] = tk.BooleanVar(
        value=DATA["gnerate_func"] == "1"
    )
    tk.Checkbutton(
        group_func_decision,
        text=LANG["main.checkbutton.gnerate_func"],
        variable=func_decision_dict["gnerate_func"],
        command=lambda: Gnerate_Func_Decision("func"),
    ).grid(row=2, column=0, columnspan=2, sticky="w")

    # 字體轉換
    def Lang_Change():
        with open("data/data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        DATA["lang"] = "zh_tw" if DATA["lang"] == "zh_cn" else "zh_cn"
        with open("data/data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        messagebox.showinfo(LANG["message.success"], LANG["message.info.lang_change"])

    Creat_Button(root, "main.button.lang_change", Lang_Change).grid(
        row=3, column=2, padx=10, pady=10, sticky="n"
    )

    # 啟動主循環
    root.mainloop()
