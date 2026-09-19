# -*- coding: utf-8 -*-
"""成员B · 账户管理模块「用户注册」图稿：活动图 + 类模型图 + 协作图。

本目录下「用户登录」的三张图与模块用例图不由本脚本生成——它们按组长 835c105
《修订成员B交付示例图稿》后的新版样例，从 main 的 docs/交付/1-账户管理-成员B/
逐文件整体拷贝（字节一致），本脚本只负责「用户注册」的三张图。

用法：
    python gen_figures.py                # 在本目录 images/ 下生成 .drawio
    然后用本机 draw.io 命令行导出 PNG（本机 draw.io 为 Windows 版，在 WSL 下必须
    把路径转成 Windows 路径，否则报 input file not found）：
        cd images
        WD=$(wslpath -w "$PWD")
        "/mnt/c/Program Files/draw.io/draw.io.exe" -x -f png --scale 2 \
          -o "$WD\\用户注册_活动图.png" "$WD\\用户注册_活动图.drawio"

风格遵循 docs/绘图规范.md：白底、黑白线条（#444444）、Microsoft YaHei、走线不穿框、
扩展流程必须画成分支并形成回路。图编号不烤进图片，由组长整合排版时统一编号。

设计约定（2026-09 修订，与 docs/交付/1-账户管理-成员B/gen_login_diagrams.py 对齐）：
- 协作图：对象框内不写冒号；每条消息一根两端坐标写死的独立直线段（不吸附图元），
  编号标签紧贴自己那根线（水平线标签在线上方/下方，垂直线标签在线的左/右侧），
  两对象间的双向消息画成两条平行线，方向一目了然。
- 类模型图：类框用三个独立矩形拼成"类名/属性/方法"三栏，不用 <hr> 灰色分隔线；
  同一关联线上的所有文字（关联名 + 两端多重性）全部放在线的同一侧，水平线统一在
  上方、垂直线统一在右方。
- 导出说明：draw.io 命令行按"内容包围盒"裁剪 PNG，内容以外的白边会被裁掉。为使
  边缘的标签不贴图，每张图加一块比内容略大（四周 10~15px）的白色底板，底板不可见
  但会被计入包围盒，从而得到整齐的四周边距。
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "docs" / "交付" / "1-账户管理-钟标" / "images"
OUT.mkdir(parents=True, exist_ok=True)

FONT = "fontFamily=Microsoft YaHei;fontSize=12;fontColor=#222222;"
BOX = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;" + FONT
NOTE = "rounded=1;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#444444;dashed=1;" + FONT
DIAMOND = "rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;" + FONT
ACTOR = ("shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
         "fillColor=#FFFFFF;strokeColor=#444444;" + FONT)
CLASS_TITLE = ("rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;"
               "align=center;verticalAlign=middle;fontStyle=1;" + FONT)
CLASS_COMP = ("rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;"
              "verticalAlign=top;align=left;spacingLeft=10;spacingTop=6;" + FONT)
TEXT = "text;html=1;align=center;verticalAlign=middle;fillColor=none;strokeColor=none;" + FONT
TEXT_L = TEXT.replace("align=center", "align=left")
TEXT_R = TEXT.replace("align=center", "align=right")
EDGE = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#444444;strokeWidth=1;"
        "fontFamily=Microsoft YaHei;fontSize=11;fontColor=#444444;labelBackgroundColor=#FFFFFF;")
SEG = ("html=1;rounded=0;strokeColor=#444444;strokeWidth=1;"
       "startArrow=none;endArrow=open;endFill=0;")    # 两端坐标写死的独立线段


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


def mxfile(cells, page_w, page_h, bg):
    """bg = (x, y, w, h)：比内容略大的白色底板，用来在导出时留出整齐的四周边距。"""
    bx, by, bw, bh = bg
    bgcell = vertex("page_bg", "", "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=none;",
                    bx, by, bw, bh)
    body = "\n        ".join([bgcell] + cells)
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


def save(name, cells, w, h, bg):
    (OUT / f"{name}.drawio").write_text(mxfile(cells, w, h, bg), encoding="utf-8")
    print("written:", OUT / f"{name}.drawio")


def classbox(cid, stereotype, name, attrs, methods, x, y, w):
    """三栏类框：标题栏 + 属性栏 + 方法栏三个矩形拼接，栏间是共享黑边框。"""
    LINE_H, PAD = 24, 12
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


# ================= 1. 用户注册活动图 =================
# 主线一列（x=90..370，中心 230）：基本流程自上而下；
# 三个扩展流程 2a/2b/3a 各画一个菱形判断 + 虚线错误框 + 回路，回程竖线分三条通道
# （x=575 / 680 / 800），从"输入"步骤右侧的不同高度拐回，互不穿越。
cells = [
    vertex("start", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 218, 24, 24, 24),
    vertex("a1", "打开注册页面", BOX, 90, 70, 280, 44),
    vertex("a2", "输入用户名、密码、确认密码、邮箱", BOX, 90, 150, 280, 44),
    vertex("d1", "信息是否完整？", DIAMOND, 140, 234, 180, 90),
    vertex("err1", "提示补全输入", NOTE, 500, 251, 150, 56),
    vertex("d2", "两次密码是否一致？", DIAMOND, 140, 364, 180, 90),
    vertex("err2", "提示密码不一致", NOTE, 500, 381, 150, 56),
    vertex("a3", "系统检查用户名是否已被注册", BOX, 90, 494, 280, 44),
    vertex("d3", "用户名已存在？", DIAMOND, 140, 578, 180, 90),
    vertex("err3", "提示用户名已被占用", NOTE, 500, 595, 150, 56),
    vertex("a4", "创建新账户", BOX, 90, 708, 280, 44),
    vertex("a5", "提示注册成功，跳转登录页面", BOX, 90, 788, 280, 44),
    vertex("end", "", "ellipse;html=1;fillColor=#FFFFFF;strokeColor=#444444;strokeWidth=2;", 218, 872, 24, 24),
    vertex("end_in", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 224, 878, 12, 12),
    # 基本流程
    edge("f1", "start", "a1"),
    edge("f2", "a1", "a2"),
    edge("f3", "a2", "d1"),
    edge("f6", "d1", "d2", "是"),
    edge("f9", "d2", "a3", "是"),
    edge("f10", "a3", "d3"),
    edge("f13", "d3", "a4", "否"),
    edge("f14", "a4", "a5"),
    edge("f15", "a5", "end"),
    # 扩展流程 2b：信息不完整 → 提示补全 → 返回步骤 2
    edge("f4", "d1", "err1", "否", style=EDGE + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    edge("f5", "err1", "a2", "返回步骤 2",
         style=EDGE + "exitX=0.5;exitY=0;entryX=1;entryY=0.75;", points=[(575, 183)]),
    # 扩展流程 2a：两次密码不一致 → 提示密码不一致 → 返回步骤 2
    edge("f7", "d2", "err2", "否", style=EDGE + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    edge("f8", "err2", "a2", "返回步骤 2",
         style=EDGE + "exitX=1;exitY=0.5;entryX=1;entryY=0.5;", points=[(680, 409), (680, 172)]),
    # 扩展流程 3a：用户名已存在 → 提示已被占用 → 返回步骤 2
    edge("f11", "d3", "err3", "是", style=EDGE + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    edge("f12", "err3", "a2", "返回步骤 2",
         style=EDGE + "exitX=1;exitY=0.5;entryX=1;entryY=0.25;", points=[(800, 623), (800, 161)]),
]
save("用户注册_活动图", cells, 900, 940, bg=(78, 12, 764, 896))

# ================= 2. 用户注册类模型图 =================
# 布局与样例一致：注册页面（左上）→ 注册控制器（右上）→ 用户（右下，实体）
# 关联文字统一放线的同侧：水平线在上方，垂直线在右方。
cells = []
b, h_page = classbox("page", "boundary", "注册页面",
                     ["注册表单"],
                     ["显示注册表单()", "读取用户输入()", "提示错误信息()", "跳转登录页面()"],
                     60, 80, 240)
cells += b
b, h_ctl = classbox("ctl", "control", "注册控制器",
                    [],
                    ["校验输入完整性()", "校验两次密码一致()", "检查用户名是否存在()", "创建账户()"],
                    460, 80, 240)
cells += b
b, h_user = classbox("user", "entity", "用户",
                     ["用户名", "密码", "邮箱", "角色"],
                     ["校验用户名唯一()", "保存账户()"],
                     460, 420, 240)
cells += b

# 关联 1：注册页面 → 注册控制器（水平线，全部文字在线上方）
cells += [
    seg("a1", 300, 172, 460, 172),
    vertex("a1_m1", "1", TEXT, 308, 144, 24, 20),              # 页面端多重性
    vertex("a1_m2", "1", TEXT, 428, 144, 24, 20),              # 控制器端多重性
    vertex("a1_name", "提交注册请求", TEXT, 335, 144, 90, 20),  # 关联名居中
]
# 关联 2：注册控制器 → 用户（垂直线，全部文字在线右方）
cells += [
    seg("a2", 580, 80 + h_ctl, 580, 420),
    vertex("a2_m1", "1", TEXT_L, 592, 262, 24, 20),            # 控制器端多重性
    vertex("a2_name", "查重并创建", TEXT_L, 592, 328, 90, 20),  # 关联名居中
    vertex("a2_m2", "0..1", TEXT_L, 592, 390, 40, 20),         # 用户端多重性
]
save("用户注册_类模型图", cells, 800, 700, bg=(50, 68, 660, 572))

# ================= 3. 用户注册协作图 =================
# 布局：用户（左）— 注册页面（中上）— 注册控制器（中下）— 用户实体（右）。
# 每条消息一根两端坐标写死的独立直线段 + 紧贴该线的编号标签；双向消息画两条
# 平行线（1/8、2/7、3/4、5/6 各一对），箭头方向即消息方向。
# 消息编号与用例基本流程一一对应：1（输入）→2（提交）→3/4（检查用户名）
# →5/6（创建账户）→7（提示成功并跳转）→8（显示登录页）。
cells = [
    vertex("actor", "用户", ACTOR, 60, 100, 30, 60),
    vertex("page", "注册页面", BOX, 280, 90, 200, 56),
    vertex("ctl", "注册控制器", BOX, 280, 250, 200, 130),
    vertex("user", "用户", BOX, 700, 250, 200, 130),

    # 1: 用户 → 注册页面（上线，箭头向右，标签在线上方）
    seg("m1", 100, 112, 280, 112),
    vertex("m1_t", "1: 输入注册信息", TEXT, 100, 84, 180, 20),
    # 8: 注册页面 → 用户（下线，箭头向左，标签在线下方）
    seg("m8", 280, 136, 100, 136),
    vertex("m8_t", "8: 跳转登录页", TEXT, 100, 146, 170, 20),

    # 2: 注册页面 → 注册控制器（左线，箭头向下，标签在线左侧）
    seg("m2", 340, 146, 340, 250),
    vertex("m2_t", "2: 提交注册请求", TEXT_R, 188, 180, 140, 20),
    # 7: 注册控制器 → 注册页面（右线，箭头向上，标签在线右侧）
    seg("m7", 420, 250, 420, 146),
    vertex("m7_t", "7: 提示注册成功", TEXT_L, 432, 212, 140, 20),

    # 3/5: 注册控制器 → 用户实体（两条平行下线，标签各自紧贴本线上方）
    seg("m3", 480, 265, 700, 265),
    vertex("m3_t", "3: 检查用户名", TEXT, 540, 239, 100, 20),
    seg("m5", 480, 335, 700, 335),
    vertex("m5_t", "5: 创建新账户", TEXT, 540, 309, 100, 20),
    # 4/6: 用户实体 → 注册控制器（两条平行上线，标签同样紧贴本线上方）
    seg("m4", 700, 300, 480, 300),
    vertex("m4_t", "4: 返回检查结果", TEXT, 530, 274, 120, 20),
    seg("m6", 700, 370, 480, 370),
    vertex("m6_t", "6: 返回创建结果", TEXT, 530, 344, 120, 20),
]
save("用户注册_协作图", cells, 980, 420, bg=(48, 72, 864, 320))

print("done.")
