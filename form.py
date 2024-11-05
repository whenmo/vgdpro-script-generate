import tkinter as tk
from tkinter import BooleanVar, IntVar, messagebox


class Item:
    def __init__(self, button: tk.Checkbutton, var: BooleanVar, card: dict):
        self.button = button
        self.var = var
        self.card = card


def Select_Cover(lang: dict, cards: list[dict]):
    """創建選擇覆蓋文件面板"""
    root = tk.Tk()
    root.title(lang["form.root.title"])
    tk.Label(root, text=lang["form.root.info"]).grid(
        row=0, column=0, padx=10, pady=10, columnspan=10
    )

    next_row = 1
    items_lst: list[list[Item]] = [[]]
    page_ind: IntVar = IntVar(value=0)

    # 翻頁按鈕
    if len(cards) > 20:

        def Page_Change(isnext: bool):
            ind = page_ind.get()
            # hide
            for item in items_lst[ind]:
                # check_button["button"].grid_remove()
                item.button.grid_remove()
            # get ind
            ind = max(0, min(ind + (1 if isnext else -1), (len(cards) - 1) // 20))
            # show
            for item in items_lst[ind]:
                item.button.grid()

            page_ind.set(ind)

        tk.Button(
            root,
            text=lang["form.button.pre"],
            command=lambda: Page_Change(False),
            width=15,
        ).grid(row=next_row, column=0, padx=10, pady=10)
        tk.Button(
            root,
            text=lang["form.button.next"],
            command=lambda: Page_Change(True),
            width=15,
        ).grid(row=next_row, column=1, padx=10, pady=10)

        next_row += 1

    # 創建勾選框
    for card in cards:
        info = f"{card["cm"]} : {card["name"]}"
        check_var = BooleanVar(value=False)
        check_button = tk.Checkbutton(root, text=info, variable=check_var)
        if len(items_lst[-1]) == 20:
            items_lst.append([])

        lst_len = len(items_lst[-1])
        check_button.grid(
            row=(lst_len % 10) + next_row + 1, column=lst_len // 10, sticky="w"
        )
        items_lst[-1].append(Item(check_button, check_var, card))
        # item_lst[-1].append({"button": check_button, "var": check_var, "card": card})

        if len(items_lst) > 1:
            check_button.grid_remove()

    # '當前頁全選', '當前頁全取消' 按鈕
    def Change_All(change_lst: list[Item], change_var: bool):
        for item in change_lst:
            if change_var:
                item.button.select()
            else:
                item.button.deselect()
            item.var.set(change_var)

    next_row += 1 + min(len(items_lst[0]), 10)

    tk.Button(
        root,
        text=lang["form.button.all_select"],
        command=lambda: Change_All(items_lst[page_ind.get()], True),
        width=15,
    ).grid(row=next_row, column=0, padx=10, pady=10)

    tk.Button(
        root,
        text=lang["form.button.all_cancel"],
        command=lambda: Change_All(items_lst[page_ind.get()], False),
        width=15,
    ).grid(row=next_row, column=1, padx=10, pady=10)

    # '確認' 按鈕
    def Enter():
        root.quit()
        root.destroy()

    tk.Button(root, text=lang["form.button.confirm"], command=Enter, width=15).grid(
        row=next_row + 1, column=0, padx=10, pady=10
    )

    root.mainloop()
    # 處理返回值
    res_lst = []
    for item_lst in items_lst:
        for item in item_lst:
            if item.var.get():
                res_lst.append(item.card)

    messagebox.showinfo("成功", f"已選共計 {len(res_lst)} 個檔案")
    return res_lst


"""
# 測試用數據
cards = [
    {"name": "is name1", "cm": "1.lua"},
    {"name": "is name2", "cm": "2.lua"},
    {"name": "is name3", "cm": "3.lua"},
    {"name": "is name4", "cm": "4.lua"},
    {"name": "is name5", "cm": "5.lua"},
    {"name": "is name6", "cm": "6.lua"},
    {"name": "is name7", "cm": "7.lua"},
    {"name": "is name8", "cm": "8.lua"},
    {"name": "is name9", "cm": "9.lua"},
    {"name": "is name10", "cm": "10.lua"},
    {"name": "is name11", "cm": "11.lua"},
    {"name": "is name12", "cm": "12.lua"},
    {"name": "is name13", "cm": "13.lua"},
    {"name": "is name14", "cm": "14.lua"},
    {"name": "is name15", "cm": "15.lua"},
    {"name": "is name16", "cm": "16.lua"},
    {"name": "is name17", "cm": "17.lua"},
    {"name": "is name18", "cm": "18.lua"},
    {"name": "is name19", "cm": "19.lua"},
    {"name": "is name20", "cm": "20.lua"},
    {"name": "is name21", "cm": "21.lua"},
]
Select_Cover(cards)
"""
