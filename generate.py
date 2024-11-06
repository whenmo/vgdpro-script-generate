import os, sqlite3, json, re
from tkinter import messagebox
from form import Select_Cover_Form, Get_Data


# 生成 lua
with open("data/constant.json", "r", encoding="utf-8") as file:
    loc_dic: dict = json.load(file)["loc"]


def Get_Loc(pros: str) -> str:
    _loc = [var for key, var in loc_dic.items() if key in pros]
    return "+".join(_loc) if _loc else "nil"


def Get_Val(eff: str) -> str:
    match = re.search(r"[+-]\d+", eff)
    if match:
        return int(match.group())
    return "val"


def Get_Line_Lua(data: dict, eff_count: int, line: str) -> tuple[str, list]:
    """根據 line(1列 生成 (此處輸出"不加"縮進以及換行符號"""
    _str = ""
    if "：" not in line:
        return _str, []
    pros, eff = line.split("：", 1)

    # get value
    typ = "EFFECT_TYPE_SINGLE" if "这个单位" in eff else "EFFECT_TYPE_FIELD"
    loc = Get_Loc(pros)
    count = "1" if "【1回合1次】" in pros else "nil"
    val = Get_Val(eff)
    con = f"cm.con{eff_count}" if data["gnerate_con"] == "1" else "nil"
    cos = f"cm.cos{eff_count}" if data["gnerate_cos"] == "1" else "nil"
    tg = f"cm.tg{eff_count}" if data["gnerate_tg"] == "1" else "nil"
    op = f"cm.op{eff_count}" if data["gnerate_op"] == "1" else "nil"

    def Set_Func_Lst(*funcs: str) -> list[str]:
        return [func for func in funcs if data["gnerate_" + func] == "1"]

    # 起 / 自
    pro_typ_dic = {
        "【起】": f"vgd.EffectTypeIgnition(c, m, {loc}, {op}, {cos}, {con}, {tg}, {count}, property, stringid)",
        "【自】": f"vgd.EffectTypeTrigger(c, m, {loc}, {typ}, code, {op}, {cos}, {con}, {tg}, {count}, property, stringid)",
    }
    for key, var in pro_typ_dic.items():
        if key in pros:
            return var, Set_Func_Lst("con", "cos", "tg", "op")

    # 永
    targetrange_chk = "" if typ == "EFFECT_TYPE_SINGLE" else ", loc_self, loc_op"
    pro_typ_dic = {
        "永": f"vgd.EffectTypeContinuous(c, m, {loc}, {typ}, code, {val}, {con}, {tg}{targetrange_chk})",
        "永力": f"vgd.EffectTypeContinuousChangeAttack(c, m, {loc}, {typ}, {val}, {con}, {tg}{targetrange_chk})",
        "永盾": f"vgd.EffectTypeContinuousChangeDefense(c, m, {typ}, {val}, {con}, {tg}{targetrange_chk})",
        "永暴": f"vgd.EffectTypeContinuousChangeStar(c, m, {typ}, {val}, {con}, {tg}{targetrange_chk})",
    }
    eff_line = ""
    if "【永】" in pros:
        if "力量" in eff:
            eff_line += f"{pro_typ_dic["永力"]}\n"
        if "盾护" in eff:
            eff_line += f"{pro_typ_dic["永盾"]}\n"
        if "☆" in eff:
            eff_line += f"{pro_typ_dic["永暴"]}\n"
        if len(eff_line) > 0:
            return eff_line, Set_Func_Lst("con", "tg")
        return f"{pro_typ_dic["永"]}\n", Set_Func_Lst("con", "tg")

    return "", []


def Get_Func_Lua(data: dict, eff_count: int, func_lst: list) -> str:
    """根據 func_lst 生成 (此處輸出"不加"縮進以及換行符號"""
    if len(func_lst) == 0:
        return ""
    Func_dict = {
        "con": f"function cm.con{eff_count}(e,tp,eg,ep,ev,re,r,rp)\n\treturn\nend",
        "cos": f"function cm.cos{eff_count}(e,tp,eg,ep,ev,re,r,rp,chk)\n\tif chk==0 then return end\n\nend",
        "tg": f"function cm.tg{eff_count}(e,tp,eg,ep,ev,re,r,rp,chk)\n\tif chk==0 then return end\n\nend",
        "op": f"function cm.op{eff_count}(e,tp,eg,ep,ev,re,r,rp)\n\nend",
    }
    func_line = f"--e{eff_count}"
    for func in func_lst:
        func_line += f"\n{Func_dict[func]}"

    return func_line


def Generate_Lua_File(card: dict) -> str:
    lang, data = Get_Data()
    # get initial
    eff_count = 1
    initial, func = "", ""
    lines: str = card["desc"].split("\n")
    for line in lines:
        eff_line, func_lst = Get_Line_Lua(data, eff_count, line)
        if eff_line.endswith("\n"):
            eff_line = eff_line[:-1]
        initial += f"\t--{line.strip()}\n\t{eff_line}\n"
        if data["gnerate_func"] == "1":
            func += f"{Get_Func_Lua(data, eff_count, func_lst)}\n"
        eff_count += 1

    # generate Lua
    lua = f"""--{card["name"]}\nlocal cm, m, o = GetID()\nfunction cm.initial_effect(c)\n\tvgf.VgCard(c)\n{initial}end\n{func}"""
    # generate file
    with open(card["path"], "w", encoding="utf-8") as lua_file:
        lua_file.write(lua)
    return card["cm"] + "\n"


def Get_Cdb_File(path: str) -> list[str]:
    lang, data = Get_Data()
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


def Generate_File(path: str) -> None:
    lang, data = Get_Data()
    messagebox.showinfo(data["gnerate_con"], data["gnerate_cos"])
    messagebox.showinfo(data["gnerate_tg"], data["gnerate_op"])
    # load cdbs
    for cdb_path in Get_Cdb_File(path):
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
        show_res: str = ""
        cover_cards: list[dict] = []
        repeat_decision: str = data["repeat_decision"]
        for card in cdb_data:
            # skip chk
            if repeat_decision != "cover" and os.path.exists(card["path"]):
                if repeat_decision != "skip":
                    cover_cards.append(card)
                continue
            # generate file
            show_res += Generate_Lua_File(card)

        if len(cover_cards) > 0:
            for card in Select_Cover_Form(os.path.basename(cdb_path), cover_cards):
                show_res += Generate_Lua_File(card)

        messagebox.showinfo(
            lang["message.success"],
            lang["message.generate_success"]
            % (script_path, os.path.basename(cdb_path), show_res, show_res.count("\n")),
        )
