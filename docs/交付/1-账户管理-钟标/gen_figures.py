# -*- coding: utf-8 -*-
"""成员B · 账户管理模块「用户注册」图稿：活动图 + 类模型图 + 协作图。

说明：
- 模块用例图（账户管理模块用例图）由两个用例共用，已随模板提供，本脚本不重复生成。
- 生成后用本机 draw.io 命令行导出 PNG（2 倍缩放）。本机 draw.io 为 Windows 版，
  在 WSL 下必须把路径转成 Windows 路径（wslpath -w），否则报 input file not found：
      cd docs/交付/1-账户管理-钟标/images
      WD=$(wslpath -w "$PWD")
      "/mnt/c/Program Files/draw.io/draw.io.exe" -x -f png --scale 2 \
        -o "$WD\\用户注册_活动图.png" "$WD\\用户注册_活动图.drawio"

风格遵循 docs/绘图规范.md：白底、黑白线条（#444444）、Microsoft YaHei、
走线不穿框、扩展流程必须画成分支并形成回路。
图编号不烤进图片，由组长整合排版时统一编号（本用例的图 2-x）。
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "docs" / "交付" / "1-账户管理-钟标" / "images"
OUT.mkdir(parents=True, exist_ok=True)

FONT = "fontFamily=Microsoft YaHei;fontSize=12;fontColor=#222222;"
BOX = "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;" + FONT
GRAY = "rounded=1;whiteSpace=wrap;html=1;fillColor=#F5F5F5;strokeColor=#444444;" + FONT
NOTE = "rounded=1;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#444444;dashed=1;" + FONT
DIAMOND = "rhombus;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;" + FONT
ELLIPSE = "ellipse;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;" + FONT
ACTOR = ("shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;"
         "fillColor=#FFFFFF;strokeColor=#444444;" + FONT)
CLASSBOX = ("rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#444444;"
            "verticalAlign=top;align=left;spacingLeft=10;spacingTop=8;" + FONT)
TEXT = "text;html=1;align=center;verticalAlign=middle;fillColor=none;strokeColor=none;" + FONT
EDGE = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#444444;strokeWidth=1;"
        "fontFamily=Microsoft YaHei;fontSize=11;fontColor=#444444;labelBackgroundColor=#FFFFFF;")
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
        # x = 沿线位置偏移（-1..1），y = 垂直于线的像素偏移
        geom = f'<mxGeometry relative="1" as="geometry" x="{label_xy[0]}" y="{label_xy[1]}"/>'
    else:
        geom = '<mxGeometry relative="1" as="geometry"/>'
    return (f'<mxCell id="{eid}"{val} style="{style}" edge="1" parent="{parent}" '
            f'source="{src}" target="{dst}">{geom}</mxCell>')


def mxfile(cells, page_w, page_h):
    # 页面大小的白色底板（无边框）：draw.io 命令行导出 PNG 时按"内容包围盒"裁剪，
    # 没有底板时最右/最下的文字会紧贴图片边缘；加底板后导出即整页，四周留出白边。
    bg = vertex("page_bg", "", "rounded=0;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=none;",
                0, 0, page_w, page_h)
    body = "\n        ".join([bg] + cells)
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


# ================= 1. 用户注册活动图 =================
# 主线一列（x=90..370，中心 230）：基本流程自上而下；
# 三个扩展流程 2a/2b/3a 各画一个菱形判断 + 虚线错误框 + 回路，回程竖线分三条通道
# （x=575 / 680 / 800），从框右侧不同高度拐回"输入"步骤，互不穿越。
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
save("用户注册_活动图", cells, 900, 940)

# ================= 2. 用户注册类模型图 =================
def classbox(cid, stereotype, name, attrs, methods, x, y, w, h):
    parts = [f"<b>{stereotype} {name}</b>", "<hr>"]
    parts += [a + "<br>" for a in attrs] if attrs else ["—"]
    parts.append("<hr>")
    parts += [m + "<br>" for m in methods] if methods else ["—"]
    return vertex(cid, "".join(parts), CLASSBOX, x, y, w, h)


cells = [
    classbox("page", "«boundary»", "注册页面",
             ["注册表单"],
             ["显示注册表单()", "读取用户输入()", "提示错误信息()", "跳转登录页面()"],
             40, 60, 240, 170),
    classbox("ctl", "«control»", "注册控制器",
             [],
             ["校验输入完整性()", "校验两次密码一致()", "检查用户名是否存在()", "创建账户()"],
             380, 60, 240, 162),
    classbox("user", "«entity»", "用户",
             ["用户名", "密码", "邮箱", "角色"],
             ["校验用户名唯一()", "保存账户()"],
             380, 320, 240, 192),
    edge("a1", "page", "ctl", "提交注册请求",
         style=OPEN + "exitX=1;exitY=0.5;entryX=0;entryY=0.5;"),
    edge("a2", "ctl", "user", "查重并创建",
         style=OPEN + "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
    # 多重性
    vertex("m1", "1", TEXT, 288, 106, 20, 20),
    vertex("m2", "1", TEXT, 348, 106, 20, 20),
    vertex("m3", "1", TEXT, 510, 232, 20, 20),
    vertex("m4", "0..1", TEXT, 506, 296, 30, 20),
]
save("用户注册_类模型图", cells, 700, 560)

# ================= 3. 用户注册协作图 =================
# 消息编号与用例基本流程一一对应：1（输入）→2（提交）→3/4（检查用户名）→5/6（创建）
# →7（提示成功并跳转）→8（显示登录页）。ctl 与 user 之间 4 条消息按链接上下并排。
cells = [
    vertex("actor", "用户", ACTOR, 110, 330, 30, 60),
    vertex("page", ":注册页面", BOX, 290, 40, 180, 60),
    vertex("ctl", ":注册控制器", BOX, 290, 200, 180, 200),
    vertex("user", ":用户", BOX, 690, 200, 180, 200),
    # 1/8：参与者与注册页面之间
    edge("m1", "actor", "page", "1: 输入注册信息",
         style=OPEN + "exitX=1;exitY=0.2;entryX=0;entryY=0.5;", points=[(160, 342), (160, 70)]),
    edge("m8", "page", "actor", "8: 跳转登录页",
         style=OPEN + "exitX=0;exitY=0.2;entryX=0;entryY=0.5;", points=[(90, 52), (90, 360)]),
    # 2/7：注册页面与注册控制器之间
    edge("m2", "page", "ctl", "2: 提交注册请求",
         style=OPEN + "exitX=0.5;exitY=1;entryX=0.5;entryY=0;"),
    edge("m7", "ctl", "page", "7: 提示注册成功",
         style=OPEN + "exitX=0;exitY=0.15;entryX=0;entryY=0.8;", points=[(260, 230), (260, 88)]),
    # 3-6：注册控制器与用户（实体）之间，按链接自左向右、自上而下并排
    edge("m3", "ctl", "user", "3: 检查用户名",
         style=OPEN + "exitX=1;exitY=0.1;entryX=0;entryY=0.1;", label_xy=(0, -14)),
    edge("m4", "user", "ctl", "4: 返回检查结果",
         style=OPEN + "exitX=0;exitY=0.4;entryX=1;entryY=0.4;", label_xy=(0, 14)),
    edge("m5", "ctl", "user", "5: 创建新账户",
         style=OPEN + "exitX=1;exitY=0.7;entryX=0;entryY=0.7;", label_xy=(0, -14)),
    edge("m6", "user", "ctl", "6: 返回创建结果",
         style=OPEN + "exitX=0;exitY=0.925;entryX=1;entryY=0.925;", label_xy=(0, 14)),
]
save("用户注册_协作图", cells, 940, 500)

print("done.")
