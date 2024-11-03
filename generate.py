import os
import sqlite3
from tkinter import messagebox
from form import Select_Yes_No


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


def Get_Pro(pros: str, loc: str, count: str):
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

    # get loc
    loc = Get_Loc(pros)

    # get count
    count = "1" if "【1回合1次】" in pros else "nil"

    return Get_Pro(pros, loc, count)


def Get_Lua(name: str, text: str):
    initial = ""
    lines = text.split("\n")
    for i in range(len(lines)):
        line = lines[i]
        initial += f"\t--{line}\n"
        if i == len(lines) - 1:
            initial += "\n"
        initial += f"\t{Get_Line_Lua(line)}\n"

    return f"""--{name}
local cm, m, o = GetID()
function cm.initial_effect(c)
\tvgf.VgCard(c)
{initial}end    
"""
    # initial 最後有換行符, 因此 end 不換行


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


def Generate_File(txt_component):
    path: str = txt_component.get("1.0", "end-1c")
    # chk path
    if not (os.path.isdir(path) or path.endswith(".cdb")):
        messagebox.showerror("錯誤", "指定的路徑不是 cdb 檔案也不是資料夾")
        return

    # get path cdbs
    cdb_files: list[str] = [path] if path.endswith(".cdb") else Find_File_Cdb(path)

    # load cdbs
    for cdb_path in cdb_files:
        cdb_data: list[dict] = []
        # load cdb with cdb_path
        with sqlite3.connect(cdb_path) as cdb:
            cdb_cursor = cdb.cursor()
            cdb_cursor.execute("SELECT * FROM texts;")  # 讀 texts
            for texts in cdb_cursor.fetchall():
                cdb_data.append({"id": texts[0], "name": texts[1], "desc": texts[2]})

        # get script_path from cdb_path
        script_path = os.path.join(os.path.dirname(cdb_path), "script")
        if not os.path.exists(script_path):  # 如果資料夾不存在，則創建它
            os.makedirs(script_path)

        create_str = ""
        creats = []
        for data in cdb_data:
            cm = f"c{data["id"]}.lua"
            cm_path = os.path.join(script_path, cm)

            if os.path.exists(cm_path) and Select_Yes_No(
                f"以下檔案已經存在\n{cm}"
            ):
                continue

            with open(cm_path, "w", encoding="utf-8") as lua_file:
                lua_file.write(Get_Lua(data["name"], data["desc"]))
            create_str += cm + "\n"
            creats.append(cm)
        messagebox.showinfo(
            "成功",
            f"{script_path}\n已在以上目錄中生成 :\n{create_str}共計 {len(creats)} 個檔案",
        )

    # messagebox.showinfo("成功", "已生成")
