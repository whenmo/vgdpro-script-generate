import os
import sqlite3
from tkinter import BooleanVar, messagebox
from form import Select_Cover


# 生成 lua
def Get_Loc(pros: str):
    loc_typ_dic = {
        "V": "LOCATION_VZONE",
        "R": "LOCATION_RZONE",
        # "V/R": "LOCATION_MZONE",
        "G": "LOCATION_GZONE",
        "灵魂": "LOCATION_OVERLAY",
        "弃牌区": "LOCATION_DROP",
        "手牌": "LOCATION_HAND",
    }

    _loc = "nil"
    for loc_typ in loc_typ_dic.keys():
        if loc_typ in pros:
            _loc += "+" + loc_typ_dic[loc_typ]

    return _loc[4:] if len(_loc) > 3 else _loc


def Get_Pro(pros: str):
    loc = Get_Loc(pros)
    count = "1" if "【1回合1次】" in pros else "nil"

    pro_typ_dic = {
        "【起】": f"vgd.EffectTypeIgnition(c, m, {loc}, op, cost, con, tg, {count}, property)",
        "【自】": f"vgd.EffectTypeTrigger(c, m, {loc}, typ, code, op, cost, con, tg, {count}, property)",
        "【永】": "",
    }

    _pro = ""
    for pro_typ in pro_typ_dic.keys():
        if pro_typ in pros:
            _pro = pro_typ_dic[pro_typ]

    return _pro


def Get_Line_Lua(line: str):
    """根據 line(1列 生成 (此處輸出不加縮進以及換行符號"""
    _str = ""
    if "：" not in line:
        return _str
    pros, eff = line.split("：", 1)
    return Get_Pro(pros)


def Generate_Lua_File(card: dict):
    # get initial
    initial = ""
    lines = card["desc"].split("\n")
    for i, line in enumerate(lines):
        initial += f"\t--{line}\n"
        if i == len(lines) - 1:
            initial += "\n"
        initial += f"\t{Get_Line_Lua(line)}\n"
    # generate Lua
    lua = f"""--{card["name"]}\nlocal cm, m, o = GetID()\nfunction cm.initial_effect(c)\n\tvgf.VgCard(c)\n{initial}end"""
    # generate file
    with open(card["path"], "w", encoding="utf-8") as lua_file:
        lua_file.write(lua)
    return card["cm"] + "\n"


def Find_File_Cdb(path: str):
    cdb_files, find_path = [], False
    path = path.replace("/", "\\")
    try:
        for file in os.listdir(path):
            find_path = True
            if file.endswith(".cdb"):  # 檢查是否為檔案
                cdb_files.append(os.path.join(path, file))  # 獲取完整路徑
    except FileNotFoundError:
        messagebox.showerror("錯誤", "指定的目錄不存在")
        return
    except PermissionError:
        messagebox.showerror("錯誤", "沒有訪問權限")

    if find_path and len(cdb_files) == 0:
        messagebox.showerror("錯誤", "指定的目錄不存在cdb檔案")
    return cdb_files


def Generate_File(txt_component, repeat_item_decision_dic: dict[str, BooleanVar]):
    path: str = txt_component.get("1.0", "end-1c")
    # chk path
    if not (os.path.isdir(path) or path.endswith(".cdb")):
        messagebox.showerror("錯誤", "指定的路徑不是 cdb 檔案也不是資料夾")
        return

    # get path cdbs
    cdb_files: list[str] = [path] if path.endswith(".cdb") else Find_File_Cdb(path)

    # get repeat item decision
    repeat_item_decision = next(
        (key for key, var in repeat_item_decision_dic.items() if var.get()), "ask"
    )

    # load cdbs
    for cdb_path in cdb_files:
        # get script_path from cdb_path
        script_path = os.path.join(os.path.dirname(cdb_path), "script")
        if not os.path.exists(script_path):  # 如果資料夾不存在，則創建它
            os.makedirs(script_path)

        # load cdb with cdb_path
        cdb_data: list[dict] = []
        with sqlite3.connect(cdb_path) as cdb:
            cdb_cursor = cdb.cursor()
            cdb_cursor.execute("SELECT * FROM texts;")  # 讀 texts
            for texts in cdb_cursor.fetchall():
                cdb_data.append(
                    {
                        "cm": f"c{texts[0]}.lua",
                        "name": texts[1],
                        "desc": texts[2],
                        "path": os.path.join(script_path, f"c{texts[0]}.lua"),
                    }
                )
        show_res = ""
        cover_cards: list[dict] = []
        for card in cdb_data:
            # skip chk
            if repeat_item_decision != "cover" and os.path.exists(card["path"]):
                if repeat_item_decision != "skip":
                    cover_cards.append(card)
                continue
            # generate file
            show_res += Generate_Lua_File(card)

        if len(cover_cards) > 0:
            for card in Select_Cover(cover_cards):
                show_res += Generate_Lua_File(card)

        messagebox.showinfo(
            "成功",
            f"{script_path}\n已在以上目錄中生成 :\n{show_res}共計 {show_res.count("\n")} 個檔案",
        )
