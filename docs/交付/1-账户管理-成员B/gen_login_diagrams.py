# -*- coding: utf-8 -*-
"""成员B 交付目录画图脚本：账户管理模块用例图 + 用户登录活动图/类模型图/协作图。

用法：
    python gen_login_diagrams.py        # 在本目录 images/ 下生成 .drawio
    然后用各自本机安装的 draw.io 命令行导出 PNG，例如：
    drawio -x -f png --scale 2 -o images/输出.png images/输入.drawio

风格遵循 docs/绘图规范.md：白底、黑白线条、Microsoft YaHei、走线不穿框。
图编号不烤进图片，由组长整合排版时统一编号。

设计约定（2026-09 修订）：
- 协作图：对象框内不写冒号；每条消息一根独立带箭头直线，编号标签紧贴
  自己那根线（水平线标签在线上方、垂直线标签在线的侧方），两对象间
  双向消息画成上下/左右两条平行线，方向一目了然。
- 协作图参与者标注 = 用例描述中的参与者名（如「普通用户」「访客」），
  实体对象命名避开参与者名，避免同名歧义。
- 类模型图：类框用三个独立矩形拼成"类名/属性/方法"三栏，不用 <hr>
  灰色分隔线；同一关联线上的所有文字（关联名 + 两端多重性）全部放在
  线的同一侧，水平线统一在上方、垂直线统一在右方。
"""
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


# ================= 1. 账户管理模块用例图 =================
cells = [
    vertex("boundary", "电子相册系统", BOUND, 180, 40, 520, 400),
    vertex("actor_user", "普通用户", ACTOR, 60, 100, 30, 60),
    vertex("actor_admin", "管理员", ACTOR, 60, 300, 30, 60),
    vertex("uc_reg", "用户注册", ELLIPSE, 400, 110, 170, 60),
    vertex("uc_login", "用户登录", ELLIPSE, 400, 290, 170, 60),
    edge("l1", "actor_user", "uc_reg", style=STRAIGHT + "exitX=1;exitY=0.4;entryX=0;entryY=0.5;"),
    edge("l2", "actor_user", "uc_login", style=STRAIGHT + "exitX=1;exitY=0.6;entryX=0;entryY=0.4;"),
    edge("l3", "actor_admin", "uc_login", style=STRAIGHT + "exitX=1;exitY=0.4;entryX=0;entryY=0.8;"),
]
save("账户管理模块用例图", cells, 760, 480)

# ================= 2. 用户登录活动图 =================
cells = [
    vertex("start", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 218, 24, 24, 24),
    vertex("a1", "打开登录页面", BOX, 100, 70, 260, 44),
    vertex("a2", "输入用户名和密码", BOX, 100, 150, 260, 44),
    vertex("d1", "输入完整？", DIAMOND, 140, 234, 180, 90),
    vertex("err1", "提示补全输入", NOTE, 470, 250, 150, 56),
    vertex("a3", "系统验证用户名和密码", BOX, 100, 364, 260, 44),
    vertex("d2", "验证通过？", DIAMOND, 140, 448, 180, 90),
    vertex("err2", "提示“用户名或密码错误”", NOTE, 470, 464, 150, 56),
    vertex("d3", "账户角色？", DIAMOND, 140, 578, 180, 90),
    vertex("a4", "进入个人主页", BOX, 40, 708, 160, 44),
    vertex("a5", "进入后台管理页", BOX, 280, 708, 170, 44),
    vertex("end", "", "ellipse;html=1;fillColor=#FFFFFF;strokeColor=#444444;strokeWidth=2;", 218, 792, 24, 24),
    vertex("end_in", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 224, 798, 12, 12),
    edge("f1", "start", "a1"),
    edge("f2", "a1", "a2"),
    edge("f3", "a2", "d1"),
    edge("f4", "d1", "err1", "否", style=EDGE + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    edge("f5", "err1", "a2", "返回输入",
         style=EDGE + "exitX=0.5;exitY=0;entryX=1;entryY=0.75;", points=[(545, 183)]),
    edge("f6", "d1", "a3", "是"),
    edge("f7", "a3", "d2"),
    edge("f8", "d2", "err2", "否", style=EDGE + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    edge("f9", "err2", "a2", "返回重新输入",
         style=EDGE + "exitX=1;exitY=0.5;entryX=1;entryY=0.25;", points=[(700, 492), (700, 161)]),
    edge("f10", "d2", "d3", "是"),
    edge("f11", "d3", "a4", "普通用户", style=EDGE + "exitX=0.25;exitY=1;entryX=0.5;entryY=0;"),
    edge("f12", "d3", "a5", "管理员", style=EDGE + "exitX=0.75;exitY=1;entryX=0.5;entryY=0;"),
    edge("f13", "a4", "end", style=EDGE + "exitX=0.5;exitY=1;entryX=0;entryY=0.5;",
         points=[(120, 804)]),
    edge("f14", "a5", "end", style=EDGE + "exitX=0.5;exitY=1;entryX=1;entryY=0.5;",
         points=[(365, 804)]),
]
save("用户登录_活动图", cells, 780, 860)

# ================= 3. 用户登录类模型图 =================
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
b, h_page = classbox("page", "boundary", "登录页面",
                     ["登录表单"],
                     ["显示登录表单()", "读取用户输入()", "提示错误信息()", "按角色跳转页面()"],
                     60, 80, 240)
cells += b
b, h_ctl = classbox("ctl", "control", "登录控制器",
                    [],
                    ["校验输入完整性()", "验证账户()", "判断角色()"],
                    460, 80, 240)
cells += b
b, h_user = classbox("user", "entity", "用户",
                     ["用户名", "密码", "邮箱", "角色"],
                     ["验证密码()"],
                     460, 420, 240)
cells += b

# 关联 1：登录页面 → 登录控制器（水平线，全部文字在线上方）
cells += [
    seg("a1", 300, 152, 460, 152),
    vertex("a1_m1", "1", TEXT, 308, 124, 24, 20),          # 页面端多重性
    vertex("a1_m2", "1", TEXT, 428, 124, 24, 20),          # 控制器端多重性
    vertex("a1_name", "提交登录请求", TEXT, 335, 124, 90, 20),  # 关联名居中
]
# 关联 2：登录控制器 → 用户（垂直线，全部文字在线右方）
cells += [
    seg("a2", 580, 80 + h_ctl, 580, 420),
    vertex("a2_m1", "1", TEXT_L, 592, 238, 24, 20),        # 控制器端多重性
    vertex("a2_name", "查找并验证", TEXT_L, 592, 314, 90, 20),  # 关联名居中
    vertex("a2_m2", "0..1", TEXT_L, 592, 386, 40, 20),     # 用户端多重性
]
save("用户登录_类模型图", cells, 800, 680)

# ================= 4. 用户登录协作图 =================
# 布局：普通用户(左) — 登录页面(中上) — 登录控制器(右上) — 用户实体(右下)
# 每条消息一根独立直线 + 紧贴该线的编号标签；双向消息画两条平行线。
cells = [
    vertex("actor", "普通用户", ACTOR, 60, 90, 30, 60),
    vertex("page", "登录页面", BOX, 280, 80, 200, 56),
    vertex("ctl", "登录控制器", BOX, 640, 80, 200, 56),
    vertex("user", "用户", BOX, 640, 370, 200, 56),

    # 1: 普通用户 → 登录页面（上线，箭头向右，标签在线上方）
    seg("m1", 100, 100, 280, 100),
    vertex("m1_t", "1: 输入用户名、密码", TEXT, 100, 72, 180, 20),
    # 6: 登录页面 → 普通用户（下线，箭头向左，标签在线下方）
    seg("m6", 280, 124, 100, 124),
    vertex("m6_t", "6: 显示个人主页/后台管理页", TEXT, 110, 132, 220, 20),

    # 2: 登录页面 → 登录控制器（上线，箭头向右，标签在线上方）
    seg("m2", 480, 98, 640, 98),
    vertex("m2_t", "2: 提交登录\n（用户名、密码）", TEXT, 492, 44, 136, 44),
    # 5: 登录控制器 → 登录页面（下线，箭头向左，标签在线下方）
    seg("m5", 640, 124, 480, 124),
    vertex("m5_t", "5: 按角色跳转页面", TEXT, 492, 132, 136, 20),

    # 3: 登录控制器 → 用户实体（左线，箭头向下，标签在线左方）
    seg("m3", 676, 136, 676, 370),
    vertex("m3_t", "3: 验证账户", TEXT_R, 560, 243, 104, 20),
    # 4: 用户实体 → 登录控制器（右线，箭头向上，标签在线右方）
    seg("m4", 764, 370, 764, 136),
    vertex("m4_t", "4: 返回验证结果与角色", TEXT_L, 776, 243, 180, 20),
]
save("用户登录_协作图", cells, 980, 470)
