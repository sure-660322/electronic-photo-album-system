# -*- coding: utf-8 -*-
"""成员D（王柯涵）图稿：照片管理模块用例图 + 上传图片/浏览照片 活动图、类模型图、协作图。

用法：
    python "docs/交付/3-照片管理-王柯涵/gen_photo_diagrams.py"
    然后用本机 draw.io 命令行导出 PNG，例如：
    drawio -x -f png --scale 2 -o images/xxx.png images/xxx.drawio

风格遵循 docs/绘图规范.md：白底、黑白线条、Microsoft YaHei、走线不穿框。
图编号不烤进图片，由组长整合排版时统一编号。

设计约定（2026-09 返工，对齐成员B修订范例 gen_login_diagrams.py）：
- 类模型图：类框用三个独立矩形拼成"类名/属性/方法"三栏，不用 <hr>
  灰色分隔线；属性为空就留空栏，不放"—"占位符；同一关联线上的所有
  文字（关联名 + 两端多重性）放在线的同一侧（水平线在上方、垂直线在右方）。
- 协作图：对象框内不写冒号；每条消息一根独立带箭头直线，"编号: 消息内容"
  单行标签紧贴自己那根线（水平线标签在线上方/下方，垂直线标签在线侧方）；
  双向消息画成上下/左右两条平行线，错开不共线；对象间距加大。
- 活动图：分支标签（是/否、回路名）不再挂在边上听凭自动布局，改为
  独立文字框按绝对坐标紧贴对应线段；回路终点画到明确的节点上。
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
STRAIGHT = ("html=1;strokeColor=#444444;strokeWidth=1;"
            "fontFamily=Microsoft YaHei;fontSize=11;fontColor=#444444;labelBackgroundColor=#FFFFFF;"
            "startArrow=none;endArrow=none;")          # 无箭头直线（用例图参与者连线）
# 独立直线段（类图关联 / 协作图消息）：开放箭头，对齐范例 SEG
SEG_OPEN = ("html=1;rounded=0;strokeColor=#444444;strokeWidth=1;"
            "startArrow=none;endArrow=open;endFill=0;")
# 活动图流程线：实心箭头（与范例 EDGE 默认箭头一致）
SEG_ARR = "html=1;rounded=0;strokeColor=#444444;strokeWidth=1;"
# 折线中间段：无箭头
SEG_NONE = "html=1;rounded=0;strokeColor=#444444;strokeWidth=1;startArrow=none;endArrow=none;"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "&#xa;")


def vertex(cid, value, style, x, y, w, h, parent="1"):
    return (f'<mxCell id="{cid}" value="{esc(value)}" style="{style}" vertex="1" parent="{parent}">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')


def edge(eid, src, dst, style=STRAIGHT, parent="1"):
    return (f'<mxCell id="{eid}" value="" style="{style}" edge="1" parent="{parent}" '
            f'source="{src}" target="{dst}"><mxGeometry relative="1" as="geometry"/></mxCell>')


def seg(eid, x1, y1, x2, y2, style=SEG_ARR):
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


LINE_H, PAD = 24, 12   # 类框属性/方法栏：每行 24px，上下留白共 12px


def classbox(cid, stereotype, name, attrs, methods, x, y, w):
    """三栏类框：标题栏 + 属性栏 + 方法栏三个矩形拼接，栏间是共享黑边框。

    属性/方法为空时留空栏（高度按一行计），不放"—"占位符。
    """
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


# ================= 1. 照片管理模块用例图（本次返工不改） =================
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
# 主流程居中自上而下；扩展流程在右侧同层；回路标签全部按绝对坐标紧贴线段。
cells = [
    vertex("start", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 218, 24, 24, 24),
    vertex("a1", "进入目标相册，点击“上传图片”", BOX, 100, 70, 260, 44),
    vertex("a2", "系统显示文件选择窗口", BOX, 100, 150, 260, 44),
    vertex("a3", "选择本地图片文件并提交", BOX, 100, 230, 260, 44),
    vertex("d1", "格式、大小校验通过？", DIAMOND, 140, 314, 180, 90),
    vertex("err1", "提示“仅支持 jpg/png/gif，\n且不超过 10MB”", NOTE, 450, 326, 230, 66),
    vertex("a4", "保存图片文件并生成缩略图，记录上传者与上传时间", BOX, 100, 444, 260, 60),
    vertex("a5", "提示上传成功，照片显示在相册中", BOX, 100, 552, 260, 44),
    vertex("end", "", "ellipse;html=1;fillColor=#FFFFFF;strokeColor=#444444;strokeWidth=2;", 218, 640, 24, 24),
    vertex("end_in", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 224, 646, 12, 12),

    # 主流程
    seg("f1", 230, 48, 230, 70),
    seg("f2", 230, 114, 230, 150),
    seg("f3", 230, 194, 230, 230),
    seg("f4", 230, 274, 230, 314),
    seg("f7", 230, 404, 230, 444),
    seg("f8", 230, 504, 230, 552),
    seg("f9", 230, 596, 230, 640),
    # 扩展流程 4a：否 → 提示框，回路拐回 a3（范例 f5 画法）
    seg("f5", 320, 359, 450, 359),
    seg("f6a", 565, 326, 565, 252, SEG_NONE),
    seg("f6b", 565, 252, 360, 252),
    # 分支标签：紧贴各自线段
    vertex("l_no", "否", TEXT, 375, 334, 20, 20),
    vertex("l_yes", "是", TEXT, 196, 414, 24, 20),
    vertex("l_back", "返回重新选择", TEXT, 397, 226, 130, 20),
]
save("上传图片_活动图", cells, 760, 700)

# ================= 3. 上传图片_类模型图 =================
# 版式对齐范例：页面左上、控制器右上、实体右下；关联文字同侧（水平线上方/垂直线右方）
cells = []
b, _ = classbox("page", "boundary", "上传页面",
                ["上传表单"],
                ["显示文件选择窗口()", "提示错误信息()", "显示上传结果()"],
                60, 80, 240)
cells += b
b, _ = classbox("ctl", "control", "上传控制器",
                [],
                ["校验格式与大小()", "保存图片并生成缩略图()", "记录上传信息()"],
                460, 80, 240)
cells += b
b, _ = classbox("photo", "entity", "照片",
                ["文件路径", "缩略图路径", "所属相册", "上传者", "上传时间"],
                ["保存()"],
                460, 420, 240)
cells += b

# 关联 1：上传页面 → 上传控制器（水平线，全部文字在线上方）
cells += [
    seg("a1", 300, 152, 460, 152, SEG_OPEN),
    vertex("a1_m1", "1", TEXT, 308, 124, 24, 20),
    vertex("a1_name", "提交上传请求", TEXT, 340, 124, 80, 20),
    vertex("a1_m2", "1", TEXT, 428, 124, 24, 20),
]
# 关联 2：上传控制器 → 照片（垂直线，全部文字在线右方）
cells += [
    seg("a2", 580, 240, 580, 420, SEG_OPEN),
    vertex("a2_m1", "1", TEXT_L, 592, 258, 24, 20),
    vertex("a2_name", "创建并保存", TEXT_L, 592, 314, 90, 20),
    vertex("a2_m2", "0..*", TEXT_L, 592, 386, 40, 20),
]
save("上传图片_类模型图", cells, 800, 680)

# ================= 4. 上传图片_协作图 =================
# 布局：用户(左) — 上传页面(中) — 上传控制器(右上) — 照片(右下)
# 每条消息一根独立直线 + 单行"编号: 消息"标签紧贴该线；双向消息画两条平行线。
cells = [
    vertex("actor", "用户", ACTOR, 40, 205, 30, 100),
    vertex("page", "上传页面", BOX, 280, 160, 200, 240),
    vertex("ctl", "上传控制器", BOX, 700, 160, 200, 170),
    vertex("photo", "照片", BOX, 700, 430, 200, 64),

    # 用户 ↔ 上传页面（三条水平线，去程标签在线上方、回程在线下方）
    seg("m1", 70, 210, 280, 210, SEG_OPEN),
    vertex("m1_t", "1: 进入相册，点击“上传图片”", TEXT, 85, 184, 180, 20),
    seg("m2", 280, 236, 70, 236, SEG_OPEN),
    vertex("m2_t", "2: 显示文件选择窗口", TEXT, 113, 242, 125, 20),
    seg("m3", 70, 296, 280, 296, SEG_OPEN),
    vertex("m3_t", "3: 选择图片文件并提交", TEXT, 107, 270, 136, 20),

    # 上传页面 ↔ 上传控制器（双线错开）
    seg("m4", 480, 210, 700, 210, SEG_OPEN),
    vertex("m4_t", "4: 提交上传请求", TEXT, 540, 184, 100, 20),
    seg("m7", 700, 246, 480, 246, SEG_OPEN),
    vertex("m7_t", "7: 返回上传结果", TEXT, 540, 252, 100, 20),

    # 上传控制器 ↔ 照片（竖直双线，标签在线侧方）
    seg("m5", 736, 330, 736, 430, SEG_OPEN),
    vertex("m5_t", "5: 保存图片并生成缩略图，记录上传信息", TEXT_R, 496, 368, 224, 20),
    seg("m6", 824, 430, 824, 330, SEG_OPEN),
    vertex("m6_t", "6: 返回保存结果", TEXT_L, 836, 370, 110, 20),

    # 8: 上传页面 → 用户（沿底部绕行回用户，标签贴水平段上方）
    seg("m8a", 380, 400, 380, 430, SEG_NONE),
    seg("m8b", 380, 430, 28, 430, SEG_NONE),
    seg("m8c", 28, 430, 28, 260, SEG_NONE),
    seg("m8d", 28, 260, 40, 260, SEG_OPEN),
    vertex("m8_t", "8: 提示上传成功，照片显示在相册中", TEXT, 117, 404, 200, 20),
]
save("上传图片_协作图", cells, 980, 530)

# ================= 5. 浏览照片_活动图 =================
# 主流程居中自上而下；两个扩展分支标签紧贴线段；
# "暂无相册"分支指向紧邻的结束节点（箭头短、去向明确，UML 允许多个活动终点）；
# "私有相册"回路沿最右侧通道绕行回到"进入浏览页面"（范例 f9 画法）。
cells = [
    vertex("start", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 218, 24, 24, 24),
    vertex("a1", "进入浏览页面，加载可见相册列表", BOX, 100, 70, 260, 44),
    vertex("d1", "存在可见相册？", DIAMOND, 140, 154, 180, 90),
    vertex("err1", "显示“暂无相册”", NOTE, 460, 170, 160, 50),
    vertex("a2", "点击某个相册", BOX, 100, 284, 260, 44),
    vertex("d2", "相册可查看？", DIAMOND, 140, 368, 180, 90),
    vertex("err2", "提示“该相册为私有，无权查看”", NOTE, 460, 386, 190, 56),
    vertex("a3", "显示相册内照片缩略图网格", BOX, 100, 498, 260, 44),
    vertex("a4", "点击某张缩略图", BOX, 100, 588, 260, 44),
    vertex("a5", "显示照片大图及照片信息", BOX, 100, 674, 260, 44),
    vertex("end", "", "ellipse;html=1;fillColor=#FFFFFF;strokeColor=#444444;strokeWidth=2;", 218, 772, 24, 24),
    vertex("end_in", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 224, 778, 12, 12),
    # 第二个活动终点：紧邻"暂无相册"，结束浏览分支短箭头直达
    vertex("end2", "", "ellipse;html=1;fillColor=#FFFFFF;strokeColor=#444444;strokeWidth=2;", 700, 183, 24, 24),
    vertex("end2_in", "", "ellipse;html=1;fillColor=#444444;strokeColor=#444444;", 706, 189, 12, 12),

    # 主流程
    seg("f1", 230, 48, 230, 70),
    seg("f2", 230, 114, 230, 154),
    seg("f5", 230, 244, 230, 284),
    seg("f9", 230, 458, 230, 498),
    seg("f10", 230, 542, 230, 588),
    seg("f11", 230, 632, 230, 674),
    seg("f12", 230, 718, 230, 772),
    # 扩展 1a：否 → 显示"暂无相册" → 结束浏览 → 就近终点
    seg("f3", 320, 199, 460, 199),
    seg("f4", 620, 195, 700, 195),
    # 扩展 2a：否 → 提示私有 → 最右通道绕回 a1（范例 f9 画法）
    seg("f7", 320, 413, 460, 413),
    seg("f8a", 650, 413, 740, 413, SEG_NONE),
    seg("f8b", 740, 413, 740, 92, SEG_NONE),
    seg("f8c", 740, 92, 360, 92),
    # 分支标签：紧贴各自线段
    vertex("l_no1", "否", TEXT, 375, 174, 20, 20),
    vertex("l_yes1", "是", TEXT, 196, 254, 24, 20),
    vertex("l_no2", "否", TEXT, 375, 388, 20, 20),
    vertex("l_yes2", "是", TEXT, 196, 468, 24, 20),
    vertex("l_end", "结束浏览", TEXT, 628, 168, 64, 20),
    vertex("l_back", "返回相册列表", TEXT, 500, 66, 100, 20),
]
save("浏览照片_活动图", cells, 800, 830)

# ================= 6. 浏览照片_类模型图 =================
# 版式：控制类与边界类在上、实体类在下；连线短直不交叉，
# 关联文字放线中点附近、同一侧（水平线上方 / 垂直线右方）。
cells = []
b, _ = classbox("page", "boundary", "浏览页面",
                ["浏览视图"],
                ["显示相册列表()", "显示缩略图网格()", "显示照片大图与信息()"],
                60, 80, 240)
cells += b
b, _ = classbox("ctl", "control", "浏览控制器",
                [],
                ["获取可见相册列表()", "获取相册照片列表()", "获取照片详情()"],
                560, 80, 240)
cells += b
b, _ = classbox("album", "entity", "相册",
                ["相册名称", "可见性", "所有者"],
                ["获取照片列表()"],
                60, 440, 240)
cells += b
b, _ = classbox("photo", "entity", "照片",
                ["文件路径", "缩略图路径", "上传者", "上传时间"],
                ["获取详情()"],
                560, 440, 240)
cells += b

# 关联 1：浏览页面 → 浏览控制器（水平线，文字在线上方）
cells += [
    seg("a1", 300, 152, 560, 152, SEG_OPEN),
    vertex("a1_m1", "1", TEXT, 308, 124, 24, 20),
    vertex("a1_name", "提交浏览请求", TEXT, 390, 124, 80, 20),
    vertex("a1_m2", "1", TEXT, 528, 124, 24, 20),
]
# 关联 2：浏览控制器 → 相册（直角三段，文字贴水平段上方/竖直段右侧）
cells += [
    seg("a2a", 620, 240, 620, 350, SEG_NONE),
    seg("a2b", 620, 350, 180, 350, SEG_NONE),
    seg("a2c", 180, 350, 180, 440, SEG_OPEN),
    vertex("a2_m1", "1", TEXT_L, 632, 270, 24, 20),
    vertex("a2_name", "查询可见相册", TEXT, 355, 322, 90, 20),
    vertex("a2_m2", "0..*", TEXT_L, 190, 386, 40, 20),
]
# 关联 3：浏览控制器 → 照片（垂直线，文字在线右方）
cells += [
    seg("a3", 690, 240, 690, 440, SEG_OPEN),
    vertex("a3_m1", "1", TEXT_L, 702, 258, 24, 20),
    vertex("a3_name", "读取照片详情", TEXT_L, 702, 314, 90, 20),
    vertex("a3_m2", "0..*", TEXT_L, 702, 396, 40, 20),
]
# 关联 4：相册 → 照片（水平线，文字在线上方）
cells += [
    seg("a4", 300, 510, 560, 510, SEG_OPEN),
    vertex("a4_m1", "1", TEXT, 308, 482, 24, 20),
    vertex("a4_name", "包含", TEXT, 405, 482, 50, 20),
    vertex("a4_m2", "0..*", TEXT, 516, 482, 34, 20),
]
save("浏览照片_类模型图", cells, 860, 680)

# ================= 7. 浏览照片_协作图 =================
# 布局：用户(左) — 浏览页面(中) — 浏览控制器(中右) — 相册/照片(右列上下)
# 每条消息一根独立水平直线 + 单行"编号: 消息"标签紧贴该线；
# 成对消息（去程/回程）上下错开为平行线；对象间距加大。
cells = [
    vertex("actor", "用户", ACTOR, 40, 230, 30, 120),
    vertex("page", "浏览页面", BOX, 280, 160, 200, 320),
    vertex("ctl", "浏览控制器", BOX, 700, 160, 220, 320),
    vertex("album", "相册", BOX, 1140, 140, 200, 190),
    vertex("photo", "照片", BOX, 1140, 400, 200, 90),

    # 用户 → 浏览页面（三次交互，标签在线上方）
    seg("m1", 70, 240, 280, 240, SEG_OPEN),
    vertex("m1_t", "1: 进入浏览页面", TEXT, 115, 214, 120, 20),
    seg("m6", 70, 290, 280, 290, SEG_OPEN),
    vertex("m6_t", "6: 点击某个相册", TEXT, 115, 264, 120, 20),
    seg("m11", 70, 340, 280, 340, SEG_OPEN),
    vertex("m11_t", "11: 点击某张缩略图", TEXT, 105, 314, 140, 20),

    # 浏览页面 ↔ 浏览控制器（三对双向消息，去程标签在线上方、回程在线下方）
    seg("m2", 480, 200, 700, 200, SEG_OPEN),
    vertex("m2_t", "2: 请求可见相册列表", TEXT, 520, 174, 140, 20),
    seg("m5", 700, 226, 480, 226, SEG_OPEN),
    vertex("m5_t", "5: 返回并显示相册列表", TEXT, 520, 232, 140, 20),
    seg("m7", 480, 286, 700, 286, SEG_OPEN),
    vertex("m7_t", "7: 请求相册照片列表", TEXT, 520, 260, 140, 20),
    seg("m10", 700, 312, 480, 312, SEG_OPEN),
    vertex("m10_t", "10: 返回并显示缩略图网格", TEXT, 515, 318, 150, 20),
    seg("m12", 480, 366, 700, 366, SEG_OPEN),
    vertex("m12_t", "12: 请求照片详情", TEXT, 530, 340, 120, 20),
    seg("m15", 700, 392, 480, 392, SEG_OPEN),
    vertex("m15_t", "15: 返回并显示照片大图与信息", TEXT, 510, 398, 160, 20),

    # 浏览控制器 ↔ 相册（两对双向消息）
    seg("m3", 920, 200, 1140, 200, SEG_OPEN),
    vertex("m3_t", "3: 查询可见相册", TEXT, 975, 174, 110, 20),
    seg("m4", 1140, 226, 920, 226, SEG_OPEN),
    vertex("m4_t", "4: 返回相册列表", TEXT, 975, 232, 110, 20),
    seg("m8", 920, 286, 1140, 286, SEG_OPEN),
    vertex("m8_t", "8: 查询相册内照片", TEXT, 970, 260, 120, 20),
    seg("m9", 1140, 312, 920, 312, SEG_OPEN),
    vertex("m9_t", "9: 返回照片列表", TEXT, 975, 318, 110, 20),

    # 浏览控制器 ↔ 照片（一对双向消息）
    seg("m13", 920, 430, 1140, 430, SEG_OPEN),
    vertex("m13_t", "13: 读取照片详情", TEXT, 970, 404, 120, 20),
    seg("m14", 1140, 456, 920, 456, SEG_OPEN),
    vertex("m14_t", "14: 返回照片详情", TEXT, 975, 462, 110, 20),
]
save("浏览照片_协作图", cells, 1400, 540)

print("全部 7 张 .drawio 生成完毕")
