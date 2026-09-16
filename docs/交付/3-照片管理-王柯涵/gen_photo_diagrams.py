# -*- coding: utf-8 -*-
"""成员D（王柯涵）图稿：照片管理模块用例图 + 上传图片/浏览照片 活动图、类模型图、协作图。

用法：
    python "docs/交付/3-照片管理-王柯涵/gen_photo_diagrams.py"
    然后用本机 draw.io 命令行导出 PNG，例如：
    drawio -x -f png --scale 2 -o images/xxx.png images/xxx.drawio

风格遵循 docs/绘图规范.md：白底、黑白线条、Microsoft YaHei、走线不穿框。
图编号不烤进图片，由组长整合排版时统一编号。
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(parents=True, exist_ok=True)

FONT = "fontFamily=Microsoft YaHei;fontSize=12;fontColor=#222222;"
BOX = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;" + FONT
GRAY = "rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#444444;" + FONT
NOTE = "rounded=1;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#444444;dashed=1;" + FONT
DIAMOND = "rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;" + FONT
ELLIPSE = "ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;" + FONT
ACTOR = ("shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
         "fillColor=#FFFFFF;strokeColor=#444444;" + FONT)
BOUND = ("rounded=0;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#444444;"
         "verticalAlign=top;align=left;spacingLeft=12;spacingTop=8;" + FONT)
CLASSBOX = ("rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;"
            "verticalAlign=top;align=left;spacingLeft=10;spacingTop=8;" + FONT)
TEXT = "text;html=1;align=center;verticalAlign=middle;fillColor=none;strokeColor=none;" + FONT
EDGE = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#444444;strokeWidth=1;"
        "fontFamily=Microsoft YaHei;fontSize=11;fontColor=#444444;labelBackgroundColor=#FFFFFF;")
STRAIGHT = ("html=1;strokeColor=#444444;strokeWidth=1;"
            "fontFamily=Microsoft YaHei;fontSize=11;fontColor=#444444;labelBackgroundColor=#FFFFFF;"
            "startArrow=none;endArrow=none;")          # 无箭头直线（用例图参与者连线）
OPEN = EDGE + "startArrow=none;endArrow=open;"        # 开放箭头（类图关联 / 协作图消息）


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "&#xa;")


def vertex(cid, value, style, x, y, w, h, parent="1", raw=False):
    v = value if raw else esc(value)
    return (f'<mxCell id="{cid}" value="{v}" style="{style}" vertex="1" parent="{parent}">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')


def edge(eid, src, dst, label="", style=EDGE, parent="1", points=None, label_xy=None):
    val = f' value="{esc(label)}"' if label else ' value=""'
    if points:
        pts = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in points)
        geom = f'<mxGeometry relative="1" as="geometry"><Array as="points">{pts}</Array></mxGeometry>'
    elif label_xy is not None:
        geom = f'<mxGeometry relative="1" as="geometry" x="{label_xy[0]}" y="{label_xy[1]}"/>'
    else:
        geom = '<mxGeometry relative="1" as="geometry"/>'
    return (f'<mxCell id="{eid}"{val} style="{style}" edge="1" parent="{parent}" '
            f'source="{src}" target="{dst}">{geom}</mxCell>')


def mxfile(cells, page_w, page_h):
    body = "\n        ".join(cells)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" type="device" version="24.7.5">
  <diagram name="第1页" id="p1">
    <mxGraphModel dx="1000" dy="700" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{page_w}" pageHeight="{page_h}" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        {body}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
'''


def save(name, cells, w, h):
    (OUT / f"{name}.drawio").write_text(mxfile(cells, w, h), encoding="utf-8")
    print("written:", OUT / f"{name}.drawio")


def classbox(cid, stereotype, name, attrs, methods, x, y, w, h):
    # value 整体交给 esc 做 XML 转义，<hr>/<br> 标签会被存为 &lt;hr&gt;，drawio 按 HTML 渲染
    parts = [f"<b>{stereotype} {name}</b>", "<hr>"]
    parts += [a + "<br>" for a in attrs] if attrs else ["—"]
    parts.append("<hr>")
    parts += [m + "<br>" for m in methods] if methods else ["—"]
    return vertex(cid, "".join(parts), CLASSBOX, x, y, w, h)


# ================= 1. 照片管理模块用例图 =================
cells = [
    vertex("boundary", "电子相册系统", BOUND, 180, 40, 520, 400),
    vertex("actor_user", "普通用户", ACTOR, 60, 200, 30, 60),
    vertex("uc_upload", "上传图片", ELLIPSE, 400, 110, 170, 60),
    vertex("uc_browse", "浏览照片", ELLIPSE, 400, 290, 170, 60),
    edge("l1", "actor_user", "uc_upload",
         style=STRAIGHT + "exitX=1;exitY=0.35;entryX=0;entryY=0.5;"),
    edge("l2", "actor_user", "uc_browse",
         style=STRAIGHT + "exitX=1;exitY=0.65;entryX=0;entryY=0.5;"),
]
save("照片管理模块用例图", cells, 760, 480)

# ================= 2. 上传图片_活动图 =================
cells = [
    vertex("start", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 218, 24, 24, 24),
    vertex("a1", "进入目标相册，点击“上传图片”", BOX, 100, 70, 260, 44),
    vertex("a2", "系统显示文件选择窗口", BOX, 100, 150, 260, 44),
    vertex("a3", "选择本地图片文件并提交", BOX, 100, 230, 260, 44),
    vertex("d1", "格式、大小校验通过？", DIAMOND, 140, 314, 180, 90),
    vertex("err1", "提示“仅支持 jpg/png/gif，且不超过 10MB”", NOTE, 450, 330, 190, 70),
    vertex("a4", "保存图片文件并生成缩略图，记录上传者与上传时间", BOX, 100, 444, 260, 60),
    vertex("a5", "提示上传成功，照片显示在相册中", BOX, 100, 552, 260, 44),
    vertex("end", "", "ellipse;html=1;fillColor=#FFFFFF;strokeColor=#444444;strokeWidth=2;", 218, 640, 24, 24),
    vertex("end_in", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 224, 646, 12, 12),
    edge("f1", "start", "a1"),
    edge("f2", "a1", "a2"),
    edge("f3", "a2", "a3"),
    edge("f4", "a3", "d1"),
    edge("f5", "d1", "err1", "否", style=EDGE + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    edge("f6", "err1", "a3", "返回重新选择",
         style=EDGE + "exitX=0.5;exitY=0;entryX=1;entryY=0.5;", points=[(545, 252)]),
    edge("f7", "d1", "a4", "是"),
    edge("f8", "a4", "a5"),
    edge("f9", "a5", "end"),
]
save("上传图片_活动图", cells, 780, 720)

# ================= 3. 上传图片_类模型图 =================
# 版式对齐成员B基准：三框统一 240 宽、左右两列纵向对齐、框高贴合内容。
cells = [
    classbox("page", "«boundary»", "上传页面",
             ["上传表单"],
             ["显示文件选择窗口()", "提示错误信息()", "显示上传结果()"],
             40, 60, 240, 150),
    classbox("ctl", "«control»", "上传控制器",
             [],
             ["校验格式与大小()", "保存图片并生成缩略图()", "记录上传信息()"],
             380, 60, 240, 130),
    classbox("photo", "«entity»", "照片",
             ["文件路径", "缩略图路径", "所属相册", "上传者", "上传时间"],
             ["保存()"],
             380, 300, 240, 170),
    edge("a1", "page", "ctl", "提交上传请求",
         style=OPEN + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    edge("a2", "ctl", "photo", "创建并保存",
         style=OPEN + "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
    vertex("m1", "1", TEXT, 292, 106, 20, 20),
    vertex("m2", "1", TEXT, 352, 106, 20, 20),
    vertex("m3", "1", TEXT, 482, 214, 20, 20),
    vertex("m4", "0..*", TEXT, 476, 268, 34, 20),
]
save("上传图片_类模型图", cells, 680, 510)

# ================= 4. 上传图片_协作图 =================
# 版式对齐成员B基准：对象用紧凑薄框，小人 30×60；
# 1/2/3 走 小人↔页面 通道，8 从页面底部绕行回小人左侧（通道不拥挤），
# 4/7 水平双线、5/6 竖直双线，标签放线侧空白处。
cells = [
    vertex("actor", "用户", ACTOR, 50, 160, 30, 60),
    vertex("page", ":上传页面", BOX, 210, 130, 180, 120),
    vertex("ctl", ":上传控制器", BOX, 500, 140, 190, 70),
    vertex("photo", ":照片", BOX, 470, 330, 170, 50),
    edge("m1", "actor", "page", "1: 进入相册，\n点击“上传图片”",
         style=OPEN + "exitX=1;exitY=0.2;entryX=0;entryY=0.2;", label_xy=(0, -20)),
    edge("m2", "page", "actor", "2: 显示文件选择窗口",
         style=OPEN + "exitX=0;exitY=0.45;entryX=1;entryY=0.5;", label_xy=(0, -12)),
    edge("m3", "actor", "page", "3: 选择图片文件\n并提交",
         style=OPEN + "exitX=1;exitY=0.8;entryX=0;entryY=0.75;", label_xy=(0, 18)),
    edge("m8", "page", "actor", "8: 提示上传成功，\n照片显示在相册中",
         style=OPEN + "exitX=0.15;exitY=1;entryX=0;entryY=0.9;",
         points=[(237, 290), (45, 290)], label_xy=(0, 16)),
    edge("m4", "page", "ctl", "4: 提交上传请求",
         style=OPEN + "exitX=1;exitY=0.25;entryX=0;entryY=0.3;", label_xy=(0, -12)),
    edge("m7", "ctl", "page", "7: 返回上传结果",
         style=OPEN + "exitX=0;exitY=0.8;entryX=1;entryY=0.6;", label_xy=(0, 12)),
    edge("m5", "ctl", "photo", "5: 保存并生成缩略图，\n记录上传信息",
         style=OPEN + "exitX=0.2;exitY=1;entryX=0.2;entryY=0;", label_xy=(-0.3, -60)),
    edge("m6", "photo", "ctl", "6: 返回保存结果",
         style=OPEN + "exitX=0.85;exitY=0;entryX=0.85;entryY=1;", label_xy=(-0.3, 45)),
]
save("上传图片_协作图", cells, 740, 430)

# ================= 5. 浏览照片_活动图 =================
cells = [
    vertex("start", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 218, 24, 24, 24),
    vertex("a1", "进入浏览页面，加载可见相册列表", BOX, 100, 70, 260, 48),
    vertex("d1", "存在可见相册？", DIAMOND, 140, 158, 180, 90),
    vertex("err1", "显示“暂无相册”", NOTE, 460, 174, 160, 50),
    vertex("a2", "点击某个相册", BOX, 100, 288, 260, 44),
    vertex("d2", "相册可查看？", DIAMOND, 140, 372, 180, 90),
    vertex("err2", "提示“该相册为私有，无权查看”", NOTE, 460, 388, 180, 56),
    vertex("a3", "显示相册内照片缩略图网格", BOX, 100, 502, 260, 48),
    vertex("a4", "点击某张缩略图", BOX, 100, 592, 260, 44),
    vertex("a5", "显示照片大图及照片信息", BOX, 100, 678, 260, 48),
    vertex("end", "", "ellipse;html=1;fillColor=#FFFFFF;strokeColor=#444444;strokeWidth=2;", 218, 776, 24, 24),
    vertex("end_in", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 224, 782, 12, 12),
    edge("f1", "start", "a1"),
    edge("f2", "a1", "d1"),
    edge("f3", "d1", "err1", "否", style=EDGE + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    edge("f4", "err1", "end", "结束浏览",
         style=EDGE + "exitX=1;exitY=0.5;entryX=1;entryY=0.5;", points=[(680, 199), (680, 788)]),
    edge("f5", "d1", "a2", "是"),
    edge("f6", "a2", "d2"),
    edge("f7", "d2", "err2", "否", style=EDGE + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    edge("f8", "err2", "a1", "返回相册列表",
         style=EDGE + "exitX=0;exitY=0.5;entryX=1;entryY=0.5;", points=[(420, 416), (420, 94)]),
    edge("f9", "d2", "a3", "是"),
    edge("f10", "a3", "a4"),
    edge("f11", "a4", "a5"),
    edge("f12", "a5", "end"),
]
save("浏览照片_活动图", cells, 780, 860)

# ================= 6. 浏览照片_类模型图 =================
cells = [
    classbox("page", "«boundary»", "浏览页面",
             ["浏览视图"],
             ["显示相册列表()", "显示缩略图网格()", "显示照片大图与信息()"],
             40, 60, 250, 170),
    classbox("ctl", "«control»", "浏览控制器",
             [],
             ["获取可见相册列表()", "获取相册照片列表()", "获取照片详情()"],
             420, 60, 260, 160),
    classbox("album", "«entity»", "相册",
             ["相册名称", "可见性", "所有者"],
             ["获取照片列表()"],
             40, 350, 250, 170),
    classbox("photo", "«entity»", "照片",
             ["文件路径", "缩略图路径", "上传者", "上传时间"],
             ["获取详情()"],
             420, 350, 250, 170),
    edge("a1", "page", "ctl", "提交浏览请求",
         style=OPEN + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    edge("a2", "ctl", "album", "查询可见相册",
         style=OPEN + "exitX=0;exitY=1;entryX=0.5;entryY=0;", points=[(370, 260)]),
    edge("a3", "ctl", "photo", "读取照片详情",
         style=OPEN + "exitX=0.8;exitY=1;entryX=0.5;entryY=0;", points=[(628, 300)]),
    edge("a4", "album", "photo", "包含",
         style=OPEN + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    vertex("m1", "1", TEXT, 302, 118, 20, 20),
    vertex("m2", "1", TEXT, 392, 118, 20, 20),
    vertex("m3", "1", TEXT, 388, 236, 20, 20),
    vertex("m4", "0..*", TEXT, 176, 316, 34, 20),
    vertex("m5", "1", TEXT, 648, 236, 20, 20),
    vertex("m6", "0..1", TEXT, 556, 316, 30, 20),
    vertex("m7", "1", TEXT, 302, 408, 20, 20),
    vertex("m8", "0..*", TEXT, 376, 408, 34, 20),
]
save("浏览照片_类模型图", cells, 760, 560)

# ================= 7. 浏览照片_协作图 =================
cells = [
    vertex("actor", "用户", ACTOR, 40, 210, 30, 100),
    vertex("page", ":浏览页面", BOX, 170, 170, 190, 160),
    vertex("ctl", ":浏览控制器", BOX, 450, 170, 210, 160),
    vertex("album", ":相册", BOX, 740, 150, 170, 70),
    vertex("photo", ":照片", BOX, 740, 340, 170, 70),
    edge("m1", "actor", "page", "1: 进入浏览页面",
         style=OPEN + "exitX=1;exitY=0.15;entryX=0;entryY=0.15;", label_xy=(0, -12)),
    edge("m6", "actor", "page", "6: 点击某个相册",
         style=OPEN + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;", label_xy=(0, -12)),
    edge("m11", "actor", "page", "11: 点击某张缩略图",
         style=OPEN + "exitX=1;exitY=0.85;entryX=0;entryY=0.85;", label_xy=(0, 14)),
    edge("m2", "page", "ctl", "2: 请求可见相册列表",
         style=OPEN + "exitX=1;exitY=0.08;entryX=0;entryY=0.08;", label_xy=(0, -12)),
    edge("m5", "ctl", "page", "5: 返回并显示相册列表",
         style=OPEN + "exitX=0;exitY=0.24;entryX=1;entryY=0.24;", label_xy=(0, 14)),
    edge("m7", "page", "ctl", "7: 请求相册照片列表",
         style=OPEN + "exitX=1;exitY=0.40;entryX=0;entryY=0.40;", label_xy=(0, -12)),
    edge("m10", "ctl", "page", "10: 返回并显示缩略图网格",
         style=OPEN + "exitX=0;exitY=0.56;entryX=1;entryY=0.56;", label_xy=(0, 14)),
    edge("m12", "page", "ctl", "12: 请求照片详情",
         style=OPEN + "exitX=1;exitY=0.72;entryX=0;entryY=0.72;", label_xy=(0, -12)),
    edge("m15", "ctl", "page", "15: 返回并显示照片大图与信息",
         style=OPEN + "exitX=0;exitY=0.88;entryX=1;entryY=0.88;", label_xy=(0, 14)),
    edge("m3", "ctl", "album", "3: 查询可见相册",
         style=OPEN + "exitX=1;exitY=0.15;entryX=0;entryY=0.3;", points=[(700, 194)]),
    edge("m4", "album", "ctl", "4: 返回相册列表",
         style=OPEN + "exitX=0;entryX=1;exitY=0.7;entryY=0.35;", points=[(678, 199)]),
    edge("m8", "ctl", "album", "8: 查询相册内照片",
         style=OPEN + "exitX=1;exitY=0.55;entryX=0;entryY=0.7;", points=[(700, 258)]),
    edge("m9", "album", "ctl", "9: 返回照片列表",
         style=OPEN + "exitX=0;exitY=0.9;entryX=1;entryY=0.7;", points=[(678, 263)]),
    edge("m13", "ctl", "photo", "13: 读取照片详情",
         style=OPEN + "exitX=1;exitY=0.85;entryX=0;entryY=0.3;", points=[(700, 306), (700, 361)]),
    edge("m14", "photo", "ctl", "14: 返回照片详情",
         style=OPEN + "exitX=0;exitY=0.7;entryX=1;entryY=0.65;", points=[(678, 389), (678, 274)]),
]
save("浏览照片_协作图", cells, 960, 440)

print("全部 7 张 .drawio 生成完毕")
