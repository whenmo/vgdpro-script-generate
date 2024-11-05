import tkinter as tk
from tkinter import Text, BooleanVar, filedialog, messagebox
import json, os
from generate import Generate_File


def main(lang: dict):
    # 創建主窗口
    root = tk.Tk()
    root.title(lang["main.root.title"])

    # 路徑 txt
    path_txt = tk.Text(root, width=60, height=1)
    path_txt.grid(row=0, column=0, padx=10, pady=10, columnspan=3)

    # '生成'按鈕
    def load_Generate_File():
        with open("data/data.json", "r", encoding="utf-8") as file:
            decision = json.load(file)["repeat_decision"]
        Generate_File(
            lang=lang, path=path_txt.get("1.0", "end-1c"), repeat_decision=decision
        )

    tk.Button(
        root, text=lang["main.button.generate"], command=load_Generate_File, width=15
    ).grid(row=1, column=0, padx=10, pady=10, sticky="w")

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
    tk.Button(
        root,
        text=lang["main.button.select_cdb"],
        command=lambda: select_path("askopenfilename"),
        width=15,
    ).grid(row=1, column=1, padx=10, pady=10, sticky="w")

    # '選擇資料夾'按鈕
    tk.Button(
        root,
        text=lang["main.button.select_file"],
        command=lambda: select_path("askdirectory"),
        width=15,
    ).grid(row=1, column=2, padx=10, pady=10, sticky="w")

    # 重複項目處理 groupbox
    group_repeat_decision = tk.LabelFrame(
        root, text=lang["main.LabelFrame.repeat_decision"], padx=10, pady=10
    )
    group_repeat_decision.grid(
        row=3, column=0, padx=10, pady=10, columnspan=3, sticky="w"
    )

    # '總是覆蓋檔案', '總是跳過檔案' 勾選框
    def Select_File_Decision(typ: str):
        with open("data/data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        if repeat_decision[typ].get():
            data["repeat_decision"] = typ
            _typ = "skip" if typ == "cover" else "cover"
            repeat_decision[_typ].set(False)
        else:
            data["repeat_decision"] = "ask"
        with open("data/data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    repeat_decision: dict[str, BooleanVar] = {}
    for col, key in enumerate(["cover", "skip"]):
        with open("data/data.json", "r", encoding="utf-8") as file:
            var = json.load(file)["repeat_decision"] == key
        repeat_decision[key] = BooleanVar(value=var)
        tk.Checkbutton(
            group_repeat_decision,
            text=lang["main.checkbutton." + key],
            variable=repeat_decision[key],
            command=lambda k=key: Select_File_Decision(k),
        ).grid(row=0, column=col)

    # 字體轉換
    def Lang_Change():
        with open("data/data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        data["lang"] = "zh_tw" if data["lang"] == "zh_cn" else "zh_cn"
        with open("data/data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        messagebox.showinfo(lang["message.success"], lang["main.button.lang_change"])

    tk.Button(
        root,
        text="繁體 <-> 简体",
        command=Lang_Change,
        width=15,
    ).grid(row=3, column=2, padx=10, pady=10, sticky="w")

    # 啟動主循環
    root.mainloop()


if __name__ == "__main__":
    with open("data/data.json", "r", encoding="utf-8") as file:
        data: json = json.load(file)
    with open(f"data/{data['lang']}.json", "r", encoding="utf-8") as file:
        lang = json.load(file)
    main(lang)
