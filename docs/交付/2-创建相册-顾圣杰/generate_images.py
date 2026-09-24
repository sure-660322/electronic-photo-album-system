# -*- coding: utf-8 -*-
from pathlib import Path

OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(parents=True, exist_ok=True)

FONT = "fontFamily=Microsoft YaHei;fontSize=12;fontColor=#222222;"
BOX = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;" + FONT
NOTE = "rounded=1;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#444444;dashed=1;" + FONT
DIAMOND = "rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;" + FONT
ELLIPSE = "ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;" + FONT
ACTOR = ("shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
         "fillColor=#FFFFFF;strokeColor=#444444;" + FONT)
BOUND = ("rounded=0;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#444444;"
         "verticalAlign=top;align=left;spacingLeft=12;spacingTop=8;" + FONT)
# 类框三栏：标题栏居中加粗，属性/方法栏左对齐
CLASS_TITLE = ("rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;"
               "align=center;verticalAlign=middle;fontStyle=1;" + FONT)
CLASS_COMP = ("rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;"
              "verticalAlign=top;align=left;spacingLeft=10;spacingTop=6;" + FONT)
TEXT = "text;html=1;align=center;verticalAlign=middle;fillColor=none;strokeColor=none;" + FONT
TEXT_L = TEXT.replace("align=center", "align=left")
TEXT_R = TEXT.replace("align=center", "align=right")
EDGE = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#444444;strokeWidth=1;"
        "fontFamily=Microsoft YaHei;fontSize=11;fontColor=#444444;labelBackgroundColor=#FFFFFF;")
STRAIGHT = ("html=1;strokeColor=#444444;strokeWidth=1;"
            "fontFamily=Microsoft YaHei;fontSize=11;fontColor=#444444;labelBackgroundColor=#FFFFFF;"
            "startArrow=none;endArrow=none;")          # 无箭头直线（用例图参与者连线）
OPEN = EDGE + "startArrow=none;endArrow=open;"        # 开放箭头（活动图以外保留）
SEG = ("html=1;rounded=0;strokeColor=#444444;strokeWidth=1;"
       "startArrow=none;endArrow=open;endFill=0;")    # 独立直线段（类图关联 / 协作图消息）


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "&#xa;")


def vertex(cid, value, style, x, y, w, h, parent="1"):
    return (f'<mxCell id="{cid}" value="{esc(value)}" style="{style}" vertex="1" parent="{parent}">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')


def edge(eid, src, dst, label="", style=EDGE, parent="1", points=None):
    val = f' value="{esc(label)}"' if label else ' value=""'
    if points:
        pts = "".join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in points)
        geom = f'<mxGeometry relative="1" as="geometry"><Array as="points">{pts}</Array></mxGeometry>'
    else:
        geom = '<mxGeometry relative="1" as="geometry"/>'
    return (f'<mxCell id="{eid}"{val} style="{style}" edge="1" parent="{parent}" '
            f'source="{src}" target="{dst}">{geom}</mxCell>')


def seg(eid, x1, y1, x2, y2, style=SEG):
    """两端坐标写死的独立线段（不吸附图元，箭头方向 = (x1,y1) → (x2,y2)）。"""
    return (f'<mxCell id="{eid}" value="" style="{style}" edge="1" parent="1">'
            f'<mxGeometry relative="1" as="geometry">'
            f'<mxPoint x="{x1}" y="{y1}" as="sourcePoint"/>'
            f'<mxPoint x="{x2}" y="{y2}" as="targetPoint"/>'
            f'</mxGeometry></mxCell>')


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


# ================= 1. 相册管理模块用例图 =================
cells = [
    vertex("boundary", "电子相册系统", BOUND, 180, 40, 520, 400),
    vertex("actor_user", "普通用户", ACTOR, 60, 200, 30, 60),
    vertex("uc_create", "创建相册", ELLIPSE, 400, 110, 170, 60),
    vertex("uc_modify", "修改相册", ELLIPSE, 400, 290, 170, 60),
    edge("l1", "actor_user", "uc_create", style=STRAIGHT + "exitX=1;exitY=0.4;entryX=0;entryY=0.5;"),
    edge("l2", "actor_user", "uc_modify", style=STRAIGHT + "exitX=1;exitY=0.6;entryX=0;entryY=0.5;"),
]
save("相册管理模块用例图", cells, 760, 480)

# ================= 2. 创建相册活动图 =================
cells = [
    vertex("start", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 218, 24, 24, 24),
    vertex("a1", "点击“创建相册”按钮", BOX, 100, 70, 260, 44),
    vertex("a2", "填写相册名称、描述与可见性", BOX, 100, 150, 260, 44),
    vertex("d1", "名称非空？", DIAMOND, 140, 234, 180, 90),
    vertex("err1", "提示“请输入相册名称”", NOTE, 470, 250, 160, 56),
    vertex("a3", "校验相册名称唯一性", BOX, 100, 364, 260, 44),
    vertex("d2", "名称唯一？", DIAMOND, 140, 448, 180, 90),
    vertex("err2", "提示“相册名称已存在”", NOTE, 470, 464, 160, 56),
    vertex("a4", "保存相册信息，提示成功并刷新列表", BOX, 100, 578, 260, 44),
    vertex("end", "", "ellipse;html=1;fillColor=#FFFFFF;strokeColor=#444444;strokeWidth=2;", 218, 662, 24, 24),
    vertex("end_in", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 224, 668, 12, 12),
    edge("f1", "start", "a1"),
    edge("f2", "a1", "a2"),
    edge("f3", "a2", "d1"),
    edge("f4", "d1", "err1", "否", style=EDGE + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    edge("f5", "err1", "a2", "返回补充",
         style=EDGE + "exitX=0.5;exitY=0;entryX=1;entryY=0.75;", points=[(550, 183)]),
    edge("f6", "d1", "a3", "是"),
    edge("f7", "a3", "d2"),
    edge("f8", "d2", "err2", "否", style=EDGE + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    edge("f9", "err2", "a2", "返回重新输入",
         style=EDGE + "exitX=1;exitY=0.5;entryX=1;entryY=0.25;", points=[(700, 492), (700, 161)]),
    edge("f10", "d2", "a4", "是"),
    edge("f11", "a4", "end"),
]
save("创建相册_活动图", cells, 780, 730)

# ================= 3. 修改相册活动图 =================
cells = [
    vertex("start", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 218, 24, 24, 24),
    vertex("a1", "选择目标相册，点击“修改相册”", BOX, 100, 70, 260, 44),
    vertex("a2", "加载原相册信息并进行修改", BOX, 100, 150, 260, 44),
    vertex("d1", "名称非空？", DIAMOND, 140, 234, 180, 90),
    vertex("err1", "提示“相册名称不能为空”", NOTE, 470, 250, 160, 56),
    vertex("a3", "更新相册数据并提示成功", BOX, 100, 364, 260, 44),
    vertex("end", "", "ellipse;html=1;fillColor=#FFFFFF;strokeColor=#444444;strokeWidth=2;", 218, 448, 24, 24),
    vertex("end_in", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 224, 454, 12, 12),
    edge("f1", "start", "a1"),
    edge("f2", "a1", "a2"),
    edge("f3", "a2", "d1"),
    edge("f4", "d1", "err1", "否", style=EDGE + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    edge("f5", "err1", "a2", "返回修改",
         style=EDGE + "exitX=0.5;exitY=0;entryX=1;entryY=0.75;", points=[(550, 183)]),
    edge("f6", "d1", "a3", "是"),
    edge("f7", "a3", "end"),
]
save("修改相册_活动图", cells, 780, 520)

# ================= 4. 相册管理类模型图 =================
LINE_H, PAD = 24, 12   # 属性/方法栏：每行 24px，上下留白共 12px


def classbox(cid, stereotype, name, attrs, methods, x, y, w):
    """三栏类框：标题栏 + 属性栏 + 方法栏三个矩形拼接，栏间是共享黑边框。"""
    h_title = 40
    h_attrs = max(1, len(attrs)) * LINE_H + PAD
    h_meth = max(1, len(methods)) * LINE_H + PAD
    title = f"«{stereotype}» {name}"
    return [
        vertex(cid + "_t", title, CLASS_TITLE, x, y, w, h_title),
        vertex(cid + "_a", "\n".join(attrs), CLASS_COMP, x, y + h_title, w, h_attrs),
        vertex(cid + "_m", "\n".join(methods), CLASS_COMP,
               x, y + h_title + h_attrs, w, h_meth),
    ], h_title + h_attrs + h_meth


cells = []
b, h_page = classbox("page", "boundary", "相册页面",
                     ["相册表单"],
                     ["显示创建表单()", "显示编辑表单()", "读取相册数据()", "提示错误信息()", "刷新相册列表()"],
                     60, 80, 240)
cells += b
b, h_ctl = classbox("ctl", "control", "相册控制器",
                    [],
                    ["校验相册数据()", "检查名称唯一性()", "创建相册()", "更新相册()"],
                    460, 80, 240)
cells += b
b, h_album = classbox("album", "entity", "相册",
                      ["相册ID", "相册名称", "描述", "可见性", "创建时间", "用户ID"],
                      ["检查重名()", "保存相册()", "更新相册()"],
                      460, 420, 240)
cells += b

# 关联 1：相册页面 → 相册控制器（水平线，全部文字在线上方）
cells += [
    seg("a1", 300, 152, 460, 152),
    vertex("a1_m1", "1", TEXT, 308, 124, 24, 20),          # 页面端多重性
    vertex("a1_m2", "1", TEXT, 428, 124, 24, 20),          # 控制器端多重性
    vertex("a1_name", "提交相册操作请求", TEXT, 335, 124, 100, 20),  # 关联名居中
]
# 关联 2：相册控制器 → 相册（垂直线，全部文字在线右方）
cells += [
    seg("a2", 580, 80 + h_ctl, 580, 420),
    vertex("a2_m1", "1", TEXT_L, 592, 238, 24, 20),        # 控制器端多重性
    vertex("a2_name", "管理与保存", TEXT_L, 592, 314, 90, 20),  # 关联名居中
    vertex("a2_m2", "0..*", TEXT_L, 592, 386, 40, 20),     # 相册端多重性
]
save("相册管理_类模型图", cells, 800, 700)

# ================= 5. 相册管理协作图（以创建相册为例） =================
# 布局：用户(左) — 相册页面(中上) — 相册控制器(右上) — 相册实体(右下)
cells = [
    vertex("actor", "用户", ACTOR, 60, 90, 30, 60),
    vertex("page", "相册页面", BOX, 280, 80, 200, 56),
    vertex("ctl", "相册控制器", BOX, 640, 80, 200, 56),
    vertex("album", "相册", BOX, 640, 370, 200, 56),

    # 1: 用户 → 相册页面（上线，箭头向右，标签在线上方）
    seg("m1", 100, 100, 280, 100),
    vertex("m1_t", "1: 输入相册名称、描述与可见性", TEXT, 100, 72, 180, 20),
    # 6: 相册页面 → 用户（下线，箭头向左，标签在线下方）
    seg("m6", 280, 124, 100, 124),
    vertex("m6_t", "6: 提示创建成功并刷新列表", TEXT, 110, 132, 220, 20),

    # 2: 相册页面 → 相册控制器（上线，箭头向右，标签在线上方）
    seg("m2", 480, 98, 640, 98),
    vertex("m2_t", "2: 提交创建相册请求", TEXT, 492, 68, 136, 20),
    # 5: 相册控制器 → 相册页面（下线，箭头向左，标签在线下方）
    seg("m5", 640, 124, 480, 124),
    vertex("m5_t", "5: 返回创建结果", TEXT, 492, 132, 136, 20),

    # 3: 相册控制器 → 相册实体（左线，箭头向下，标签在线左方）
    seg("m3", 676, 136, 676, 370),
    vertex("m3_t", "3: 检查相册名称唯一性", TEXT_R, 530, 243, 134, 20),
    # 4: 相册控制器 → 相册实体（右线，箭头向下，标签在线右方）
    seg("m4", 764, 136, 764, 370),
    vertex("m4_t", "4: 保存新相册实体", TEXT_L, 776, 243, 140, 20),
]
save("相册管理_协作图", cells, 980, 470)
