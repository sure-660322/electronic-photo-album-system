# -*- coding: utf-8 -*-
"""生成类别与评论模块的 draw.io 源文件。"""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(parents=True, exist_ok=True)

FONT = "fontFamily=Microsoft YaHei;fontSize=12;fontColor=#222222;"
BOX = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;" + FONT
NOTE = BOX + "dashed=1;"
DIAMOND = "rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;" + FONT
ELLIPSE = "ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;" + FONT
ACTOR = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;fillColor=#FFFFFF;strokeColor=#444444;" + FONT
BOUND = "rounded=0;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#444444;verticalAlign=top;align=left;spacingLeft=12;spacingTop=8;" + FONT
CLASS_TITLE = "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;align=center;verticalAlign=middle;fontStyle=1;" + FONT
CLASS_COMP = "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;verticalAlign=top;align=left;spacingLeft=10;spacingTop=6;" + FONT
TEXT = "text;html=1;align=center;verticalAlign=middle;fillColor=none;strokeColor=none;" + FONT
TEXT_L = TEXT.replace("align=center", "align=left")
TEXT_R = TEXT.replace("align=center", "align=right")
EDGE = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#444444;strokeWidth=1;fontFamily=Microsoft YaHei;fontSize=11;fontColor=#444444;labelBackgroundColor=#FFFFFF;startArrow=none;endArrow=open;endFill=0;"
STRAIGHT = "html=1;strokeColor=#444444;strokeWidth=1;startArrow=none;endArrow=none;"
SEG = "html=1;rounded=0;strokeColor=#444444;strokeWidth=1;startArrow=none;endArrow=open;endFill=0;"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "&#xa;")


def vertex(cid, value, style, x, y, w, h):
    return f'<mxCell id="{cid}" value="{esc(value)}" style="{style}" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>'


def edge(eid, src, dst, label="", style=EDGE, points=None):
    pts = "" if not points else '<Array as="points">' + "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in points) + "</Array>"
    return f'<mxCell id="{eid}" value="{esc(label)}" style="{style}" edge="1" parent="1" source="{src}" target="{dst}"><mxGeometry relative="1" as="geometry">{pts}</mxGeometry></mxCell>'


def seg(eid, x1, y1, x2, y2):
    return f'<mxCell id="{eid}" value="" style="{SEG}" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="{x1}" y="{y1}" as="sourcePoint"/><mxPoint x="{x2}" y="{y2}" as="targetPoint"/></mxGeometry></mxCell>'


def save(name, cells, w, h):
    body = "\n        ".join(cells)
    xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" type="device" version="24.7.5"><diagram name="第1页" id="p1"><mxGraphModel dx="1000" dy="700" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{w}" pageHeight="{h}" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>{body}</root></mxGraphModel></diagram></mxfile>'''
    (OUT / f"{name}.drawio").write_text(xml, encoding="utf-8")


def classbox(cid, stereotype, name, attrs, methods, x, y, w):
    title_h, line_h, pad = 40, 24, 12
    ah, mh = max(1, len(attrs)) * line_h + pad, max(1, len(methods)) * line_h + pad
    cells = [
        vertex(cid + "t", f"«{stereotype}» {name}", CLASS_TITLE, x, y, w, title_h),
        vertex(cid + "a", "\n".join(attrs), CLASS_COMP, x, y + title_h, w, ah),
        vertex(cid + "m", "\n".join(methods), CLASS_COMP, x, y + title_h + ah, w, mh),
    ]
    return cells, title_h + ah + mh


# 模块用例图
save("类别与评论模块用例图", [
    vertex("b", "电子相册系统", BOUND, 180, 40, 540, 400),
    vertex("admin", "管理员", ACTOR, 60, 105, 30, 60),
    vertex("user", "普通用户", ACTOR, 60, 305, 30, 60),
    vertex("uc1", "相册类别管理", ELLIPSE, 390, 115, 190, 64),
    vertex("uc2", "对照片评论", ELLIPSE, 390, 295, 190, 64),
    edge("l1", "admin", "uc1", style=STRAIGHT), edge("l2", "user", "uc2", style=STRAIGHT),
], 780, 480)

# 类别管理活动图
save("相册类别管理_活动图", [
    vertex("s", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 328, 20, 24, 24),
    vertex("a1", "进入后台相册类别管理页面", BOX, 200, 70, 280, 46),
    vertex("a2", "显示现有类别列表", BOX, 200, 145, 280, 46),
    vertex("d1", "选择的操作？", DIAMOND, 250, 220, 180, 90),
    vertex("add", "填写新类别名称并提交", BOX, 20, 350, 210, 50),
    vertex("edit", "修改类别名称并提交", BOX, 260, 350, 180, 50),
    vertex("del", "选择类别并提交删除", BOX, 470, 350, 200, 50),
    vertex("d2", "名称有效且不重名？", DIAMOND, 40, 445, 180, 90),
    vertex("d3", "名称有效且不重名？", DIAMOND, 260, 445, 180, 90),
    vertex("d4", "类别下存在相册？", DIAMOND, 490, 445, 180, 90),
    vertex("err1", "提示名称为空或重名", NOTE, 20, 585, 190, 50),
    vertex("err2", "提示名称为空或重名", NOTE, 250, 585, 190, 50),
    vertex("err3", "提示该类别下存在相册，不能删除", NOTE, 470, 575, 220, 68),
    vertex("upd", "更新类别字典", BOX, 250, 690, 180, 46),
    vertex("ok", "提示成功并刷新类别列表", BOX, 200, 775, 280, 46),
    vertex("e", "", "ellipse;html=1;fillColor=#FFFFFF;strokeColor=#444444;strokeWidth=2;", 328, 860, 24, 24),
    vertex("ei", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 334, 866, 12, 12),
    edge("f1", "s", "a1"), edge("f2", "a1", "a2"), edge("f3", "a2", "d1"),
    edge("f4", "d1", "add", "添加"), edge("f5", "d1", "edit", "修改"), edge("f6", "d1", "del", "删除"),
    edge("f7", "add", "d2"), edge("f8", "edit", "d3"), edge("f9", "del", "d4"),
    edge("f10", "d2", "err1", "否"), edge("f11", "d3", "err2", "否"), edge("f12", "d4", "err3", "是"),
    edge("f13", "err1", "add", "返回填写", points=[(10, 610), (10, 375)]),
    edge("f14", "err2", "edit", "返回修改", points=[(240, 610), (240, 375)]),
    edge("f15", "err3", "a2", "返回列表", points=[(730, 610), (730, 168)]),
    edge("f16", "d2", "upd", "是"), edge("f17", "d3", "upd", "是"), edge("f18", "d4", "upd", "否"),
    edge("f19", "upd", "ok"), edge("f20", "ok", "e"),
], 760, 920)

# 评论活动图
save("对照片评论_活动图", [
    vertex("s", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 328, 20, 24, 24),
    vertex("a1", "在照片大图页输入评论并点击发表", BOX, 185, 70, 310, 48),
    vertex("d1", "内容非空且不超过200字？", DIAMOND, 235, 155, 210, 100),
    vertex("err", "提示评论内容错误", NOTE, 510, 180, 180, 52),
    vertex("a2", "保存评论并关联用户、照片与时间", BOX, 185, 300, 310, 48),
    vertex("a3", "按时间倒序显示评论列表", BOX, 185, 385, 310, 48),
    vertex("d2", "用户点击删除自己的评论？", DIAMOND, 225, 475, 230, 100),
    vertex("confirm", "显示删除确认", BOX, 500, 500, 180, 48),
    vertex("d3", "确认删除？", DIAMOND, 510, 600, 160, 85),
    vertex("remove", "移除该评论", BOX, 500, 730, 180, 48),
    vertex("refresh", "刷新评论列表", BOX, 185, 730, 220, 48),
    vertex("e", "", "ellipse;html=1;fillColor=#FFFFFF;strokeColor=#444444;strokeWidth=2;", 283, 835, 24, 24),
    vertex("ei", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 289, 841, 12, 12),
    edge("f1", "s", "a1"), edge("f2", "a1", "d1"), edge("f3", "d1", "err", "否"),
    edge("f4", "err", "a1", "返回输入", points=[(720, 206), (720, 94)]), edge("f5", "d1", "a2", "是"),
    edge("f6", "a2", "a3"), edge("f7", "a3", "d2"), edge("f8", "d2", "confirm", "是"),
    edge("f9", "confirm", "d3"), edge("f10", "d3", "remove", "是"), edge("f11", "remove", "refresh"),
    edge("f12", "d3", "a3", "否", points=[(720, 642), (720, 409)]),
    edge("f13", "d2", "e", "否"), edge("f14", "refresh", "e"),
], 760, 900)

# 类别管理类模型图
cells = []
b1, h1 = classbox("p", "boundary", "类别管理页面", ["类别列表", "类别表单"], ["显示类别列表()", "读取操作请求()", "提示操作结果()"], 40, 80, 220); cells += b1
b2, h2 = classbox("c", "control", "类别管理控制器", [], ["校验类别名称()", "检查类别占用()", "添加类别()", "修改类别()", "删除类别()"], 330, 80, 240); cells += b2
b3, h3 = classbox("e", "entity", "相册类别", ["类别编号", "类别名称"], ["保存()", "更新()", "删除()"], 650, 80, 210); cells += b3
b4, h4 = classbox("a", "entity", "相册", ["相册编号", "相册名称", "类别编号"], ["统计类别下相册数()"], 650, 420, 210); cells += b4
cells += [seg("r1", 260, 155, 330, 155), vertex("r1a", "1", TEXT, 265, 127, 20, 20), vertex("r1n", "提交管理请求", TEXT, 265, 105, 90, 20), vertex("r1b", "1", TEXT, 305, 127, 20, 20),
          seg("r2", 570, 155, 650, 155), vertex("r2a", "1", TEXT, 575, 127, 20, 20), vertex("r2n", "维护", TEXT, 596, 105, 50, 20), vertex("r2b", "0..*", TEXT, 615, 127, 35, 20),
          seg("r3", 755, 80+h3, 755, 420), vertex("r3a", "1", TEXT_L, 765, 280, 20, 20), vertex("r3n", "分类", TEXT_L, 765, 330, 50, 20), vertex("r3b", "0..*", TEXT_L, 765, 390, 40, 20)]
save("相册类别管理_类模型图", cells, 920, 690)

# 评论类模型图
cells = []
b1, h1 = classbox("p", "boundary", "照片详情页面", ["照片信息", "评论输入框", "评论列表"], ["读取评论内容()", "显示评论列表()", "确认删除()", "提示错误()"], 30, 70, 220); cells += b1
b2, h2 = classbox("c", "control", "评论控制器", [], ["校验评论内容()", "发表评论()", "校验删除权限()", "删除评论()"], 310, 70, 220); cells += b2
b3, h3 = classbox("m", "entity", "评论", ["评论编号", "评论内容", "评论时间", "用户编号", "照片编号"], ["保存()", "删除()"], 610, 70, 220); cells += b3
b4, h4 = classbox("u", "entity", "用户", ["用户编号", "用户名"], ["是否评论作者()"], 310, 430, 220); cells += b4
b5, h5 = classbox("ph", "entity", "照片", ["照片编号", "所属相册"], ["获取评论列表()"], 610, 430, 220); cells += b5
cells += [seg("r1", 250, 150, 310, 150), vertex("r1a", "1", TEXT, 252, 122, 20, 20), vertex("r1n", "提交请求", TEXT, 250, 100, 70, 20), vertex("r1b", "1", TEXT, 286, 122, 20, 20),
          seg("r2", 530, 150, 610, 150), vertex("r2a", "1", TEXT, 535, 122, 20, 20), vertex("r2n", "创建/删除", TEXT, 545, 100, 70, 20), vertex("r2b", "0..*", TEXT, 575, 122, 35, 20),
          seg("r3", 420, 70+h2, 420, 430), vertex("r3a", "1", TEXT_L, 430, 300, 20, 20), vertex("r3n", "校验作者", TEXT_L, 430, 342, 70, 20), vertex("r3b", "1", TEXT_L, 430, 400, 20, 20),
          seg("r4", 720, 70+h3, 720, 430), vertex("r4a", "0..*", TEXT_L, 730, 325, 40, 20), vertex("r4n", "属于", TEXT_L, 730, 355, 50, 20), vertex("r4b", "1", TEXT_L, 730, 400, 20, 20)]
save("对照片评论_类模型图", cells, 880, 720)

# 类别管理协作图
save("相册类别管理_协作图", [
    vertex("actor", "管理员", ACTOR, 35, 85, 30, 60), vertex("page", "类别管理页面", BOX, 190, 80, 170, 56),
    vertex("ctl", "类别管理控制器", BOX, 460, 80, 190, 56), vertex("cat", "相册类别", BOX, 750, 80, 160, 56), vertex("album", "相册", BOX, 750, 360, 160, 56),
    seg("m1", 75, 98, 190, 98), vertex("t1", "1: 选择添加/修改/删除并提交", TEXT, 55, 52, 220, 32),
    seg("m8", 190, 125, 75, 125), vertex("t8", "8: 显示结果和刷新列表", TEXT, 55, 136, 180, 22),
    seg("m2", 360, 98, 460, 98), vertex("t2", "2: 提交管理请求", TEXT, 360, 68, 110, 22),
    seg("m7", 460, 125, 360, 125), vertex("t7", "7: 返回操作结果", TEXT, 360, 136, 110, 22),
    seg("m3", 650, 98, 750, 98), vertex("t3", "3: 校验名称/读取类别", TEXT, 645, 58, 120, 32),
    seg("m6", 750, 125, 650, 125), vertex("t6", "6: 返回更新结果", TEXT, 650, 136, 110, 22),
    seg("m4", 785, 136, 785, 360), vertex("t4", "4: 删除前检查类别占用", TEXT_R, 610, 235, 165, 22),
    seg("m5", 865, 360, 865, 136), vertex("t5", "5: 返回相册数量", TEXT_L, 875, 235, 130, 22),
], 1040, 470)

# 评论协作图
save("对照片评论_协作图", [
    vertex("actor", "普通用户", ACTOR, 35, 85, 30, 60), vertex("page", "照片详情页面", BOX, 190, 80, 170, 56),
    vertex("ctl", "评论控制器", BOX, 460, 80, 170, 56), vertex("comment", "评论", BOX, 730, 80, 160, 56),
    vertex("photo", "照片", BOX, 730, 360, 160, 56), vertex("user", "用户", BOX, 460, 360, 170, 56),
    seg("m1", 75, 98, 190, 98), vertex("t1", "1: 输入内容并发表", TEXT, 65, 68, 140, 22),
    seg("m8", 190, 125, 75, 125), vertex("t8", "8: 显示倒序评论列表", TEXT, 55, 136, 170, 22),
    seg("m2", 360, 98, 460, 98), vertex("t2", "2: 提交评论内容", TEXT, 360, 68, 110, 22),
    seg("m7", 460, 125, 360, 125), vertex("t7", "7: 返回评论列表", TEXT, 360, 136, 110, 22),
    seg("m3", 630, 98, 730, 98), vertex("t3", "3: 保存评论", TEXT, 640, 68, 90, 22),
    seg("m6", 730, 125, 630, 125), vertex("t6", "6: 返回保存结果", TEXT, 635, 136, 105, 22),
    seg("m4", 765, 136, 765, 360), vertex("t4", "4: 关联照片并读取评论", TEXT_R, 580, 235, 175, 22),
    seg("m5", 855, 360, 855, 136), vertex("t5", "5: 返回倒序评论列表", TEXT_L, 865, 235, 150, 22),
    seg("m9", 545, 136, 545, 360), vertex("t9", "9(扩展): 删除时校验评论作者", TEXT_R, 315, 255, 220, 22),
    seg("m10", 600, 360, 600, 136), vertex("t10", "10(扩展): 返回权限并删除自己的评论", TEXT_L, 610, 285, 250, 32),
], 1040, 470)

print(f"已生成 7 个 draw.io 源文件：{OUT}")
