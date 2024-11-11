import tkinter as tk
import self_library as lib


def Select_Cover_Form(cdb_name: str, cards: list[lib.Card]) -> list[lib.Card]:
    """創建選擇覆蓋文件面板"""
    lang, _ = lib.Get_Globals()
    root = tk.Tk()
    root.title(lang["select_cover.root.title"])
    root.iconbitmap("data/anyway_is_ico.ico")

    tk.Label(root, text=lang["select_cover.root.info"] % cdb_name).grid(
        row=0, column=0, padx=10, pady=10, columnspan=10
    )

    next_row = 1
    items_lst: list[list[lib.Check_Card]] = [[]]
    page_ind: tk.IntVar = tk.IntVar(value=0)

    # 翻頁按鈕
    if len(cards) > 20:

        def Page_Change(isnext: bool):
            ind = page_ind.get()
            # hide
            for item in items_lst[ind]:
                item.button.grid_remove()
            # get ind
            ind = max(0, min(ind + (1 if isnext else -1), (len(cards) - 1) // 20))
            # show
            for item in items_lst[ind]:
                item.button.grid()

            page_ind.set(ind)

        lib.Creat_Button(
            root, lang["select_cover.button.pre"], lambda: Page_Change(False)
        ).grid(row=next_row, column=0, padx=10, pady=10)
        lib.Creat_Button(
            root, lang["select_cover.button.next"], lambda: Page_Change(True)
        ).grid(row=next_row, column=1, padx=10, pady=10)
        next_row += 1

    # 創建勾選框
    for card in cards:
        info = f"{card.cm} : {card.name}"
        check_var = tk.BooleanVar(value=False)
        check_button = lib.Creat_Checkbutton(root, info, check_var)
        if len(items_lst[-1]) == 20:
            items_lst.append([])

        lst_len = len(items_lst[-1])
        check_button.grid(
            row=(lst_len % 10) + next_row + 1, column=lst_len // 10, sticky="w"
        )
        items_lst[-1].append(lib.Check_Card(check_button, check_var, card))

        if len(items_lst) > 1:
            check_button.grid_remove()

    # '當前頁全選', '當前頁全取消' 按鈕
    def Change_All(change_var: bool):
        for item in items_lst[page_ind.get()]:
            item.button.select() if change_var else item.button.deselect()
            item.var.set(change_var)

    next_row += 1 + min(len(items_lst[0]), 10)

    lib.Creat_Button(
        root, lang["select_cover.button.all_select"], lambda: Change_All(True)
    ).grid(row=next_row, column=0, padx=10, pady=10)
    lib.Creat_Button(
        root, lang["select_cover.button.all_cancel"], lambda: Change_All(False)
    ).grid(row=next_row, column=1, padx=10, pady=10)

    # '確認' 按鈕
    def Enter():
        root.quit()
        root.destroy()

    lib.Creat_Button(root, lang["select_cover.button.confirm"], Enter).grid(
        row=next_row + 1, column=0, padx=10, pady=10
    )

    root.mainloop()
    # 處理返回值
    res_lst = []
    for item_lst in items_lst:
        for item in item_lst:
            if item.var.get():
                res_lst.append(item.card)

    return res_lst
