import os, re

path = r"C:\Users\KHUser\Desktop\vgdpro\vgdpro-scripts"


cos_dic = {
    # "横置": "vgf.ChangePosDefence()",
    "舍弃": "vgf.DisCardCost(%s)",
    "能量爆发": "vgf.EnergyCost(%s)",
    "灵魂爆发": "vgf.OverlayCost(%s)",
    "灵魂填充": "vgf.OverlayFill(%s)",
    "计数爆发": "vgf.DamageCost(%s)",
    # "退场": "vgf.LeaveFieldCost(card_or_code_or_func, val_max, val_min, except, ...)",
}


def Get_Cos(eff_count: int, chk: bool, eff: str) -> str:
    default_cos = f"cm.cos{eff_count}"
    match = re.search(r"【费用】\[(.*?)\]", eff)
    if not match:
        return default_cos if chk else "nil"
    cos_lst = []
    for cost in match.group(1).split("，"):
        if "横置" in cost:
            cos_lst.append("vgf.ChangePosDefence()")
            continue
        if "退场" in cost:
            # leave_filter = cost.split("将")[1].split("退场")[0]
            leave_filter = cost[1:-2]
            leave_filter = "" if leave_filter == "这个单位" else leave_filter
            cos_lst.append("vgf.LeaveFieldCost(%s)" % leave_filter)
            continue
        find = False
        for key, cosf in cos_dic.items():
            num_match = re.search(r"\d+", cost)
            if key in cost and num_match:
                cos_lst.append(cosf % num_match.group(0))
                find = True
                break
        if not (default_cos in cos_lst or find):
            cos_lst.append(default_cos)
    return cos_lst[0] if len(cos_lst) == 1 else f"vgf.CostAnd({",".join(cos_lst)})"


# cos = "这个单位的攻击击中时，通过【费用】[计数爆发1]，将这个单位重置，这个回合中，这个单位的驱动数-1。"
cos = "这个单位的攻击击中时，通过【费用】[横置，计数爆发1，将这个单位退场，将手牌中的1张卡舍弃]，将这个单位重置，这个回合中，这个单位的驱动数-1。"
print()
print(Get_Cos(1, True, cos))
print()
