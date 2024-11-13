import tkinter as tk
from tkinter import ttk
import self_library as lib


def Find_Func_Form():
    """創建函數查找面板"""
    lang, _ = lib.Get_Globals()
    lang = lang["find_func"]
    # 創建主窗口
    root = tk.Tk()
    root.title(lang["root.title"])
    root.iconbitmap("data/anyway_is_ico.ico")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    # frame 1
    frame_1 = tk.Frame(root, relief="flat", borderwidth=1, padx=10, pady=10)
    frame_1.grid(row=0, column=0, sticky="nsew")
    frame_1.grid_rowconfigure(2, weight=1)
    frame_1.grid_columnconfigure(0, weight=1)

    # 查詢 txt
    def Search(event: tk.Event):
        if not search_txt.edit_modified():
            return
        search_txt.edit_modified(False)
        search_key = search_txt.get("1.0", "end-1c")
        funcs_show = [funcs for funcs in funcs_datas if funcs.Match(search_key)]
        for item in find_view.get_children():
            find_view.delete(item)
        for ind, funcs in enumerate(funcs_show):
            find_view.insert("", tk.END, iid=ind, values=[funcs.name, funcs.func])

    search_txt = tk.Text(frame_1, relief="solid", height=1)
    search_txt.grid(row=0, column=0, sticky="nsew")
    search_txt.bind("<<Modified>>", Search)

    # 複製時選項 groupbox
    group_copy_decision = tk.LabelFrame(
        frame_1, text=lang["LabelFrame.copy_decision"], padx=10, pady=10
    )
    group_copy_decision.grid(row=1, column=0, pady=10, sticky="we")

    # '可省略參數以nil代替'按鈕
    nil_to_nil = tk.BooleanVar(value=False)
    nil_to_nil_button = tk.Checkbutton(
        group_copy_decision,
        text=lang["checkbutton.nil_to_nil"],
        variable=nil_to_nil,
        height=1,
    )
    nil_to_nil_button.grid(row=0, column=0, sticky="w")

    # '有默認值參數以nil代替'按鈕
    default_to_nil = tk.BooleanVar(value=False)
    default_to_nil_button = tk.Checkbutton(
        group_copy_decision,
        text=lang["checkbutton.default_to_nil"],
        variable=default_to_nil,
        height=1,
    )
    default_to_nil_button.grid(row=0, column=1, sticky="w")

    # '直到是非nil為止刪除最後的參數'按鈕
    delete_nil = tk.BooleanVar(value=False)
    delete_nil_button = tk.Checkbutton(
        group_copy_decision,
        text=lang["checkbutton.delete_nil"],
        variable=delete_nil,
        height=1,
    )
    delete_nil_button.grid(row=0, column=2, sticky="w")

    # 搜索列表
    def Click_Table(event: tk.Event):
        """顯示函數細節"""
        if find_view.identify("region", event.x, event.y) != "cell":
            return  # 如果點擊的是單元格
        if not (row_id := find_view.identify_row(event.y)).isdigit():
            return
        func_data: lib.Funcs = funcs_show[int(row_id)]  # 獲取對應的函數資料
        info_name_txt.delete(0, "end")
        info_name_txt.insert("end", func_data.Get_Func_Line())
        info_res_txt.config(
            text=lang["Label.res_type"] + func_data.res or lang["Label.no_res"]
        )
        func_data.Insert_Param(param_view)
        info_txt.delete("1.0", "end")
        info_txt.insert("1.0", func_data.info)

    def Copy_Table(event: tk.Event):
        """複製到剪貼版"""
        if find_view.identify("region", event.x, event.y) != "cell":
            return  # 如果點擊的是單元格
        if not (row_id := find_view.identify_row(event.y)[3:]).isdigit():
            return
        func_data: lib.Funcs = funcs_show[int(row_id) - 1]  # 獲取對應的函數資料
        root.clipboard_clear()  # 清空剪貼板
        root.clipboard_append(
            func_data.Get_Func_Line(
                nil_to_nil.get(), default_to_nil.get(), delete_nil.get()
            )
        )

    find_view = ttk.Treeview(frame_1, columns=("info", "func"), show="headings")
    find_view.grid(row=2, column=0, sticky="nsew")
    find_view.heading("info", text=lang["find_view.info"], anchor="w")
    find_view.heading("func", text=lang["find_view.func"], anchor="w")
    find_view.column("info", width=250, anchor="w", stretch=False)
    find_view.column("func", width=180, anchor="w")
    find_view.bind("<ButtonRelease-1>", Click_Table)
    find_view.bind("<Double-1>", Copy_Table)

    # 獲取數據並初始化
    funcs_datas: list[lib.Funcs] = Load_Func()
    for ind, funcs in enumerate(funcs_show := funcs_datas):
        find_view.insert("", tk.END, iid=ind, values=[funcs.name, funcs.func])

    # 提示文字
    tk.Label(frame_1, text=lang["Label.hint"]).grid(row=3, column=0, sticky="w")

    # frame 2
    frame_2 = tk.Frame(root, relief="flat", borderwidth=1, padx=10)
    frame_2.grid(row=0, column=1, sticky="nsew")
    frame_2.grid_rowconfigure(4, weight=1)
    frame_2.grid_columnconfigure(0, weight=1)

    # info 名稱 txt
    info_name_txt = tk.Entry(frame_2, relief="solid", width=80)
    info_name_txt.grid(row=0, column=0, pady=10, sticky="nsew")
    info_name_txt.bind("<<Modified>>", block_edit)

    # info 參數類型提示
    info_typ_hint = tk.Label(frame_2, text=lang["Label.type_hint"], anchor="e")
    info_typ_hint.grid(row=1, column=0, sticky="w")

    # info 參數列表
    param_view = ttk.Treeview(
        frame_2, columns=("name", "type", "default", "info"), show="headings", height=1
    )
    param_view.grid(row=2, column=0, pady=5, sticky="nsew")
    param_view.heading("name", text=lang["param_view.name"], anchor="w")
    param_view.heading("type", text=lang["param_view.type"], anchor="w")
    param_view.heading("default", text=lang["param_view.default"], anchor="w")
    param_view.heading("info", text=lang["param_view.info"], anchor="w")
    param_view.column("name", width=60, anchor="w", stretch=False)
    param_view.column("type", width=60, anchor="w", stretch=False)
    param_view.column("default", width=80, anchor="w")
    param_view.column("info", width=300, anchor="w")

    # info 返回值
    info_res_txt = tk.Label(frame_2, text=lang["Label.res_type"], anchor="w")
    info_res_txt.grid(row=3, column=0, sticky="w")

    # info 函數詳解
    info_txt = tk.Text(frame_2, width=50, height=10, relief="solid")
    info_txt.grid(row=4, column=0, pady=10, sticky="nsew")
    info_txt.bind("<Key>", block_edit)

    root.mainloop()


def Load_Func() -> list[lib.Funcs]:
    """獲取數據"""
    data: list[lib.Funcs] = []
    temp_data: lib.Funcs = None
    with open("data/functions.txt", "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("@name"):
                if temp_data:
                    data.append(temp_data)
                temp_data = lib.Funcs(line.strip().split(" ", 1)[1])
            elif line.startswith("@function"):
                temp_data.Set_Func(line.strip().split(" ", 1)[1])
            elif line.startswith("@param"):
                temp_data.Set_Param_Detail(line.strip().split(" ", 1)[1])
            elif line.startswith("@return"):
                temp_data.res = line.strip().split(" ", 1)[1]
            elif line[0] not in ("=", "\n"):
                temp_data.info += line
        if temp_data:
            data.append(temp_data)
    return data


def block_edit(event):
    "禁用 info 的編輯功能"
    return "break"


# Find_Func_Form()
