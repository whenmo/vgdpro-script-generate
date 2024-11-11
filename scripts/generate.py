import os, sqlite3, json, re
import self_library as lib
from tkinter import messagebox
from form_select_cover import Select_Cover_Form

with open("data/constant.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    loc_dic: dict = data["loc"]
    cos_dic: dict = data["cos"]


def File_Generation_Manager(path: str) -> None:
    """根據路徑讀取並生成檔案"""
    lang, data = lib.Get_Globals()
    script_path = os.path.join(os.path.dirname(path), "script")
    os.makedirs(script_path, exist_ok=True)
    # load cdbs
    for cdb_path in Get_Paths(path):
        # ganerate
        show_res: str = ""
        repeat_cards: list[lib.Card] = []
        for card in Load_Cdb_Data(script_path, cdb_path):
            # skip chk
            if os.path.exists(card.path):
                repeat_cards.append(card)
            else:
                # generate file
                show_res += f"{Generate_Lua_File(card)}\n"

        if repeat_cards and data["repeat_decision"] != "skip":
            if data["repeat_decision"] != "cover":
                repeat_cards = Select_Cover_Form(
                    os.path.basename(cdb_path), repeat_cards
                )
            for card in repeat_cards:
                show_res += f"{Generate_Lua_File(card)}\n"

        messagebox.showinfo(
            lang["message.success"],
            lang["message.generate_success"]
            % (script_path, os.path.basename(cdb_path), show_res, show_res.count("\n")),
        )


def Get_Paths(path: str) -> list[str]:
    """獲取 script 絕對路徑以及 cdb 絕對路徑列表"""
    lang, _ = lib.Get_Globals()
    # 路徑是 .cdb 文件
    if path.endswith(".cdb"):
        return [path]
    # 路徑不是合法目錄
    if not os.path.isdir(path):
        messagebox.showerror(lang["message.error"], lang["message.not_legal"])
        return []
    # 初始化空列表，替換 Windows 路徑分隔符
    cdb_paths = []
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

    return cdb_paths


def Load_Cdb_Data(script_path: str, cdb_path: str) -> list[lib.Card]:
    """加載 cdb 文件中的數據"""
    lang, _ = lib.Get_Globals()
    cdb_data: list[lib.Card] = []
    try:
        with sqlite3.connect(cdb_path) as cdb:
            cdb_cursor = cdb.cursor()
            cdb_cursor.execute("SELECT * FROM texts;")
            cdb_data = [lib.Card(texts, script_path) for texts in cdb_cursor.fetchall()]
    except Exception as e:
        messagebox.showerror(
            lang["message.error"],
            lang["message.cdb_load_failed"] % os.path.basename(cdb_path),
        )
    return cdb_data


def Generate_Lua_File(card: lib.Card) -> str:
    """生成 lua 文件並返回生成文件名"""
    _, data = lib.Get_Globals()
    # get initial
    eff_count = 1
    initial, func = "", ""
    lines: str = card.desc.split("\n")
    for line in lines:
        eff_line, func_line = Get_Line_Lua(data, eff_count, line)
        if eff_line.endswith("\n"):
            eff_line = eff_line[:-1]
        initial += f"\t--{line.strip()}\n\t{eff_line}\n"
        if func_line and data["gnerate_func"] == "1":
            func += f"{func_line}\n"
        eff_count += 1

    # generate Lua
    lua = f"""--{card.name}\nlocal cm, m, o = GetID()\nfunction cm.initial_effect(c)\n\tvgf.VgCard(c)\n{initial}end\n{func}"""
    # generate file
    with open(card.path, "w", encoding="utf-8") as lua_file:
        lua_file.write(lua)
    return card.cm


def Get_Func_Lua(data: dict, eff_count: int, funcs: list[str]) -> str:
    """根據 func_lst 生成 (此處輸出"不加"縮進以及換行符號"""
    funcs = [
        match.group(1) for func in funcs if (match := re.match(r"cm\.(\w+).\d*", func))
    ]
    funcs = [func for func in funcs if data[f"gnerate_{func}"] == "1"]
    if not funcs:
        return ""
    Func_dict = {
        "con": f"function cm.con{eff_count}(e,tp,eg,ep,ev,re,r,rp)\n\treturn\nend",
        "cos": f"function cm.cos{eff_count}(e,tp,eg,ep,ev,re,r,rp,chk)\n\tif chk==0 then return end\n\nend",
        "tg": f"function cm.tg{eff_count}(e,tp,eg,ep,ev,re,r,rp,chk)\n\tif chk==0 then return end\n\nend",
        "op": f"function cm.op{eff_count}(e,tp,eg,ep,ev,re,r,rp)\n\nend",
    }
    func_line = f"--e{eff_count}"
    for func in funcs:
        func_line += f"\n{Func_dict[func]}"
    return func_line


def Get_Line_Lua(data: dict, eff_count: int, line: str) -> tuple[str, list[str]]:
    """根據 line(1列 生成 (此處輸出"不加"縮進以及換行符號"""
    empty_str = ""
    # 特殊關鍵字 檢測
    if eff_line := Keyword_Ckeck(line):
        return eff_line, empty_str
    # 無特殊關鍵字
    if "：" not in line:
        return empty_str, empty_str
    pros, eff = line.split("：", 1)
    # get value
    typ = "EFFECT_TYPE_SINGLE" if "这个单位" in eff else "EFFECT_TYPE_FIELD"
    loc = Get_Loc(pros)
    count = "1" if "【1回合1次】" in pros else "nil"
    con, cos, tg, op = Get_Func(eff_count, data, eff)

    # 起 / 自
    pro_typ_dic = {
        "【起】": f"vgd.EffectTypeIgnition(c, m, {loc}, {op}, {cos}, {con}, {tg}, {count}, property, stringid)",
        "【自】": f"vgd.EffectTypeTrigger(c, m, {loc}, {typ}, code, {op}, {cos}, {con}, {tg}, {count}, property, stringid)",
    }
    for key, var in pro_typ_dic.items():
        if key in pros:
            return var, Get_Func_Lua(data, eff_count, [con, cos, tg, op])

    # 永
    if "【永】" in pros:
        func_line = Get_Func_Lua(data, eff_count, [con, tg])
        return Get_Continuous(eff, loc, typ, con, tg), func_line

    return empty_str, empty_str


def Keyword_Ckeck(line: str) -> str:
    if line.startswith("【超限舞装】-"):
        return "vgd.OverDress(c, code_or_func)"
    elif line.startswith("【交织超限舞装】-"):
        return "vgd.XOverDress(c, code_or_func)"
    elif line.startswith("舞装加身-"):
        return "vgd.DressUp(c,code)"
    elif line.startswith("【反抗舞装】-"):
        return " "
    elif line.startswith("【协奏舞装】-"):
        return " "
    return ""


def Get_Loc(pros: str) -> str:
    locs_lst: list = re.findall(r"\【(.*?)\】", pros)
    locs: str = locs_lst[-2] if locs_lst[-1] == "1回合1次" else locs_lst[-1]
    locs_lst = locs.split("/")
    locs = [loc_dic[loc] for loc in locs_lst if loc in loc_dic]
    return "+".join(locs) if locs else "nil"


def Get_Func(eff_count: int, data: dict, eff: str) -> tuple[str, str, str, str]:
    eff = eff.split("。")[0]
    con = f"cm.con{eff_count}" if data["gnerate_con"] == "1" else "nil"
    cos = Get_Cos(eff_count, data["gnerate_cos"] == "1", eff)
    tg = f"cm.tg{eff_count}" if data["gnerate_tg"] == "1" else "nil"
    op = f"cm.op{eff_count}" if data["gnerate_op"] == "1" else "nil"
    return con, cos, tg, op


def Get_Cos(eff_count: int, chk: bool, eff: str) -> str:
    default_cos = f"cm.cos{eff_count}"
    if not (match := re.search(r"【费用】\[(.*?)\]", eff)):
        return default_cos if chk else "nil"
    cos_lst = []
    for cost in match.group(1).split("，"):
        if "横置" in cost:
            cos_lst.append("vgf.ChangePosDefence()")
            continue
        if "退场" in cost:
            leave_filter = cost[1:-2]
            leave_filter = "" if leave_filter == "这个单位" else leave_filter
            cos_lst.append("vgf.LeaveFieldCost(%s)" % leave_filter)
            continue
        find = False
        for key, cosf in cos_dic.items():
            if key in cost and (match_num := re.search(r"\d+", cost)):
                cos_lst.append(cosf % match_num.group(0))
                find = True
                break
        if not (default_cos in cos_lst or find):
            cos_lst.append(default_cos)
    return cos_lst[0] if len(cos_lst) == 1 else f"vgf.CostAnd({",".join(cos_lst)})"


def Get_Continuous(eff: str, loc: str, typ: str, con: str, tg: str):
    def Get_Val(key: str) -> str:
        match = re.search(rf"{key}([^\d\+\-]*[\d\+\-]*\d+)", eff)
        return int(match.group(1)) if match else "val"

    target_range_chk = "" if typ == "EFFECT_TYPE_SINGLE" else f"{tg}, loc_self, loc_op"
    continuous_dic = {
        "力量": f"vgd.EffectTypeContinuousChangeAttack(c, m, {loc}, {typ}, {Get_Val("力量")}, {con}, {target_range_chk})\n",
        "盾护": f"vgd.EffectTypeContinuousChangeDefense(c, m, {typ}, {Get_Val("盾护")}, {con}, {target_range_chk})\n",
        "☆": f"vgd.EffectTypeContinuousChangeStar(c, m,{typ}, {Get_Val("☆")}, {con}, {target_range_chk})\n",
    }
    if eff_line := "".join(continuous_dic[key] for key in continuous_dic if key in eff):
        return eff_line
    return f"vgd.EffectTypeContinuous(c, m, {loc}, {typ}, code, val, {con}, {target_range_chk})\n"
