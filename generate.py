import os, sqlite3, json, re
from tkinter import messagebox
from form import Select_Cover_Form, Get_Globals, Card

with open("data/constant.json", "r", encoding="utf-8") as file:
    loc_dic: dict = json.load(file)["loc"]


def File_Generation_Manager(path: str) -> None:
    """根據路徑讀取並生成檔案"""
    lang, data = Get_Globals()
    # get paths
    script_path, cdb_paths = Get_Paths(path)
    os.makedirs(script_path, exist_ok=True)
    # load cdbs
    for cdb_path in cdb_paths:
        # ganerate
        show_res: str = ""
        cover_cards: list[Card] = []
        not_cover: bool = data["repeat_decision"] != "cover"
        not_skip: bool = data["repeat_decision"] != "skip"
        for card in Load_Cdb_Data(script_path, cdb_path):
            # skip chk
            if not_cover and os.path.exists(card.path):
                if not_skip:
                    cover_cards.append(card)
                continue
            # generate file
            show_res += Generate_Lua_File(card)

        if cover_cards:
            for card in Select_Cover_Form(os.path.basename(cdb_path), cover_cards):
                show_res += Generate_Lua_File(card)

        messagebox.showinfo(
            lang["message.success"],
            lang["message.generate_success"]
            % (script_path, os.path.basename(cdb_path), show_res, show_res.count("\n")),
        )


def Get_Paths(path: str) -> tuple[str, list[str]]:
    """獲取 script 絕對路徑以及 cdb 絕對路徑列表"""
    lang, _ = Get_Globals()
    # 路徑是 .cdb 文件
    if path.endswith(".cdb"):
        return os.path.join(os.path.dirname(path), "script"), [path]
    # 路徑不是合法目錄
    if not os.path.isdir(path):
        messagebox.showerror(lang["message.error"], lang["message.not_legal"])
        return "", []
    # 初始化空列表，替換 Windows 路徑分隔符
    cdb_paths = []
    path = path.replace("/", "\\")
    try:
        cdb_paths = [
            os.path.join(path, file)
            for file in os.listdir(path)
            if file.endswith(".cdb")
        ]
    except FileNotFoundError:
        messagebox.showerror(lang["message.error"], lang["message.not_exist"])
    except PermissionError:
        messagebox.showerror(lang["message.error"], lang["message.not_permissions"])
    if not cdb_paths:
        messagebox.showerror(lang["message.error"], lang["message.not_cdb"])

    return os.path.join(path, "script"), cdb_paths


def Load_Cdb_Data(script_path: str, cdb_path: str) -> list[Card]:
    """加載 cdb 文件中的數據"""
    lang, _ = Get_Globals()
    cdb_data: list[Card] = []
    try:
        with sqlite3.connect(cdb_path) as cdb:
            cdb_cursor = cdb.cursor()
            cdb_cursor.execute("SELECT * FROM texts;")
            cdb_data = [Card(texts, script_path) for texts in cdb_cursor.fetchall()]
    except Exception as e:
        messagebox.showerror(
            lang["message.error"],
            lang["message.cdb_load_failed"] % os.path.basename(cdb_path),
        )
    return cdb_data


def Generate_Lua_File(card: Card) -> str:
    """生成 lua 文件並返回生成文件名"""
    _, data = Get_Globals()
    # get initial
    eff_count = 1
    initial, func = "", ""
    lines: str = card.desc.split("\n")
    for line in lines:
        eff_line, func_lst = Get_Line_Lua(data, eff_count, line)
        if eff_line.endswith("\n"):
            eff_line = eff_line[:-1]
        initial += f"\t--{line.strip()}\n\t{eff_line}\n"
        if data["gnerate_func"] == "1":
            func += f"{Get_Func_Lua(eff_count, func_lst)}\n"
        eff_count += 1

    # generate Lua
    lua = f"""--{card.name}\nlocal cm, m, o = GetID()\nfunction cm.initial_effect(c)\n\tvgf.VgCard(c)\n{initial}end\n{func}"""
    # generate file
    with open(card.path, "w", encoding="utf-8") as lua_file:
        lua_file.write(lua)
    return card.cm + "\n"


def Get_Func_Lua(eff_count: int, func_lst: list) -> str:
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


def Get_Loc(pros: str) -> str:
    _loc = [var for key, var in loc_dic.items() if key in pros]
    return "+".join(_loc) if _loc else "nil"


def Get_Val(eff: str) -> str:
    match = re.search(r"[+-]\d+", eff)
    if match:
        return int(match.group())
    return "val"
