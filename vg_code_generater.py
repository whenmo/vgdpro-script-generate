import os
import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog


# 生成 lua
def get_loc(pros: str):
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


def get_pro(pros: str, loc: str, count: str):
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


def get_lua_with_line(line: str):
    """根據 line(1列 生成 (此處輸出不加縮進以及換行符號"""
    _str = ""
    if "：" not in line:
        return _str

    pros, eff = line.split("：", 1)

    # get loc
    loc = get_loc(pros)

    # get count
    count = "1" if "【1回合1次】" in pros else "nil"

    return get_pro(pros, loc, count)


def get_lua_code(name: str, text: str):
    initial = ""
    t = text.split("\n")
    for i in range(0, len(t)):
        line = t[i]
        initial += f"\t--{line}"
        if i == len(t) - 1:
            initial += "\n"
        initial += f"\t{get_lua_with_line(line)}\n"

    return f"""--{name}
local cm, m, o = GetID()
function cm.initial_effect(c)
\tvgf.VgCard(c)
{initial}end
"""
    # initial 最後有換行符, 因此 end 不換行


# ----------------------------------------------------------------------------------------------------------------------
# 生成函數
def find_cdb_files(path: str):
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


def try_generate(txt_component):
    path: str = txt_component.get("1.0", "end-1c")
    # chk path
    if not (os.path.isdir(path) or path.endswith(".cdb")):
        messagebox.showerror("錯誤", "指定的路徑不是 cdb 檔案也不是資料夾")
        return

    # get path cdbs
    cdb_files: list[str] = [path] if path.endswith(".cdb") else find_cdb_files(path)

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
            with open(os.path.join(script_path, cm), "w", encoding="utf-8") as lua_file:
                lua_file.write(get_lua_code(data["name"], data["desc"]))
            create_str += cm + "\n"
            creats.append(cm)
        messagebox.showinfo(
            "成功",
            f"{script_path}\n已在以上目錄中生成 :\n{create_str}共計 {len(creats)} 個檔案",
        )

    # messagebox.showinfo("成功", "已生成")


# ----------------------------------------------------------------------------------------------------------------------
# 創建主窗口
root = tk.Tk()
root.title("VG自動代碼生成器")

path_txt = tk.Text(root, width=60, height=1)
path_txt.grid(row=0, column=0, padx=10, pady=10, columnspan=10)

generate_button = tk.Button(
    root, text="生成", command=lambda: try_generate(path_txt), width=15
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
