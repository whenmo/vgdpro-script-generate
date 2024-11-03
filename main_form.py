import tkinter as tk
from tkinter import filedialog
from generate import Generate_File

# 創建主窗口
root = tk.Tk()
root.title("VG自動代碼生成器")

path_txt = tk.Text(root, width=60, height=1)
path_txt.grid(row=0, column=0, padx=10, pady=10, columnspan=10)

generate_button = tk.Button(
    root, text="生成", command=lambda: Generate_File(path_txt), width=15
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


tk.Button(
    root, text="選擇檔案(cdb", command=lambda: select_path("askopenfilename"), width=15
).grid(row=1, column=1, padx=10, pady=10, sticky="w")

tk.Button(
    root, text="選擇資料夾", command=lambda: select_path("askdirectory"), width=15
).grid(row=1, column=2, padx=10, pady=10, sticky="w")

# 啟動主循環
root.mainloop()
