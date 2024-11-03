import tkinter as tk


def Select_Yes_No(info: str = "選擇是或否"):
    # 創建是否選擇窗口
    root = tk.Tk()
    root.title("替換或跳過文件")
    tk.Label(root, text=info).grid(row=0, column=0, padx=10, pady=10, columnspan=10)

    res = tk.BooleanVar(value=False)

    def select(is_yes: bool):
        res.set(is_yes)
        root.quit()
        root.destroy()

    tk.Button(root, text="覆蓋", command=lambda: select(False), width=10).grid(
        row=1, column=0, padx=10, pady=10
    )

    tk.Button(root, text="跳過", command=lambda: select(True), width=10).grid(
        row=1, column=1, padx=10, pady=10
    )

    # 啟動主循環
    root.mainloop()
    return res.get()
