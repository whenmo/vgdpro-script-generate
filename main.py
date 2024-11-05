import tkinter as tk
from tkinter import messagebox, filedialog
import json
import generate


# 獲取全局變數
with open("data/data.json", "r", encoding="utf-8") as file:
    DATA: dict = json.load(file)
with open(f"data/{DATA['lang']}.json", "r", encoding="utf-8") as file:
    LANG: dict = json.load(file)


def main():
    # 創建主窗口
    root = tk.Tk()
    root.title(LANG["main.root.title"])

    # 路徑 txt
    path_txt = tk.Text(root, width=60, height=1)
    path_txt.grid(row=0, column=0, padx=10, pady=10, columnspan=3)

    # '生成'按鈕
    def load_Generate_File():
        generate.Generate_File(path_txt.get("1.0", "end-1c"), DATA["repeat_decision"])

    tk.Button(
        root, text=LANG["main.button.generate"], command=load_Generate_File, width=15
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
        text=LANG["main.button.select_cdb"],
        command=lambda: select_path("askopenfilename"),
        width=15,
    ).grid(row=1, column=1, padx=10, pady=10, sticky="w")

    # '選擇資料夾'按鈕
    tk.Button(
        root,
        text=LANG["main.button.select_file"],
        command=lambda: select_path("askdirectory"),
        width=15,
    ).grid(row=1, column=2, padx=10, pady=10, sticky="w")

    # 重複項目處理 groupbox
    group_repeat_decision = tk.LabelFrame(
        root, text=LANG["main.LabelFrame.repeat_decision"], padx=10, pady=10
    )
    group_repeat_decision.grid(
        row=3, column=0, padx=10, pady=10, columnspan=3, sticky="w"
    )

    # '總是覆蓋檔案', '總是跳過檔案' 勾選框
    def Select_File_Decision(typ: str):
        DATA["repeat_decision"] = "ask"
        if decision_dict[typ].get():
            DATA["repeat_decision"] = typ
            typ = "skip" if typ == "cover" else "cover"
            decision_dict[typ].set(False)
        with open("data/data.json", "w", encoding="utf-8") as file:
            json.dump(DATA, file, ensure_ascii=False, indent=4)

    decision_dict: dict[str, tk.BooleanVar] = {}
    for col, key in enumerate(["cover", "skip"]):
        decision_dict[key] = tk.BooleanVar(value=DATA["repeat_decision"] == key)
        tk.Checkbutton(
            group_repeat_decision,
            text=LANG["main.checkbutton." + key],
            variable=decision_dict[key],
            command=lambda k=key: Select_File_Decision(k),
        ).grid(row=0, column=col)

    # 字體轉換
    def Lang_Change():
        with open("data/data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        DATA["lang"] = "zh_tw" if DATA["lang"] == "zh_cn" else "zh_cn"
        with open("data/data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        messagebox.showinfo(LANG["message.success"], LANG["main.button.lang_change"])

    tk.Button(
        root,
        text="繁體 <-> 简体",
        command=Lang_Change,
        width=15,
    ).grid(row=3, column=2, padx=10, pady=10, sticky="w")

    # 啟動主循環
    root.mainloop()


if __name__ == "__main__":
    main()
