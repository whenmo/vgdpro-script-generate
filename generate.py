import os, sqlite3
from tkinter import messagebox
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


def Get_Cdb_File(lang: dict, path: str):
    # chk path
    if path.endswith(".cdb"):
        return [path]
    elif not os.path.isdir(path):
        messagebox.showerror(lang["message.error"], lang["message.error.not_legal"])
        return []
    # get file paths
    cdb_files, find_path = [], False
    path = path.replace("/", "\\")
    try:
        for file in os.listdir(path):
            find_path = True
            if file.endswith(".cdb"):  # 檢查是否為檔案
                cdb_files.append(os.path.join(path, file))  # 獲取完整路徑
    except FileNotFoundError:
        messagebox.showerror(lang["message.error"], lang["message.error.not_exist"])
    except PermissionError:
        messagebox.showerror(
            lang["message.error"], lang["message.error.not_permissions"]
        )
    if find_path and len(cdb_files) == 0:
        messagebox.showerror(lang["message.error"], lang["message.error.not_cdb"])
    return cdb_files


def Generate_File(lang: dict, path: str, repeat_decision: str):
    # load cdbs
    for cdb_path in Get_Cdb_File(lang, path):
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
            if repeat_decision != "cover" and os.path.exists(card["path"]):
                if repeat_decision != "skip":
                    cover_cards.append(card)
                continue
            # generate file
            show_res += Generate_Lua_File(card)

        if len(cover_cards) > 0:
            for card in Select_Cover(lang, cover_cards):
                show_res += Generate_Lua_File(card)

        messagebox.showinfo(
            lang["message.success"],
            lang["message.generate_success"]
            % (script_path, show_res, show_res.count("\n")),
            # f"{script_path}\n已在以上目錄中生成 :\n{show_res}共計 {show_res.count("\n")} 個檔案",
        )
