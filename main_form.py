import tkinter as tk
from tkinter import filedialog, messagebox
from generate import Generate_File


def main():
    # 創建主窗口
    root = tk.Tk()
    root.title("VG自動代碼生成器")

    # 路徑 txt
    path_txt = tk.Text(root, width=60, height=1)
    path_txt.grid(row=0, column=0, padx=10, pady=10, columnspan=3)

    # '生成'按鈕
    generate_button = tk.Button(
        root,
        text="生成",
        command=lambda: Generate_File(path_txt, repeat_item_decision),
        width=15,
    )
    generate_button.grid(row=1, column=0, padx=10, pady=10, sticky="w")

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
        text="選擇檔案(cdb",
        command=lambda: select_path("askopenfilename"),
        width=15,
    ).grid(row=1, column=1, padx=10, pady=10, sticky="w")

    # '選擇資料夾'按鈕
    tk.Button(
        root, text="選擇資料夾", command=lambda: select_path("askdirectory"), width=15
    ).grid(row=1, column=2, padx=10, pady=10, sticky="w")

    # 重複項目處理 groupbox
    group_repeat_item_decision = tk.LabelFrame(
        root, text="重複項目處理", padx=10, pady=10
    )
    group_repeat_item_decision.grid(
        row=3, column=0, padx=10, pady=10, columnspan=3, sticky="w"
    )

    repeat_item_decision = {
        "cover": tk.BooleanVar(value=True),
        "skip": tk.BooleanVar(value=False),
        "ask": tk.BooleanVar(value=False),
    }

    def Select_File_Decision(typ: str):
        if not repeat_item_decision[typ].get():
            repeat_item_decision["ask"].set(True)
            return
        repeat_item_decision["cover"].set(False)
        repeat_item_decision["skip"].set(False)
        repeat_item_decision["ask"].set(False)
        repeat_item_decision[typ].set(True)

    # '總是覆蓋檔案', '總是跳過檔案', '每個都詢問我' 勾選框
    def Create_Checkbutton(text: str, typ: str, column: int):
        checkbutton = tk.Checkbutton(
            group_repeat_item_decision,
            text=text,
            variable=repeat_item_decision[typ],
            command=lambda: Select_File_Decision(typ),
        )
        checkbutton.grid(row=0, column=column)

    Create_Checkbutton("總是覆蓋檔案", "cover", 0)
    Create_Checkbutton("總是跳過檔案", "skip", 1)
    Create_Checkbutton("每個都詢問我", "ask", 2)

    # 啟動主循環
    root.mainloop()


if __name__ == "__main__":
    main()
