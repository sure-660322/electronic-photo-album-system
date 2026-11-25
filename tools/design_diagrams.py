"""Generate the design report's UML figures and three Markdown chapters.

Run from the repository root: python tools/design_diagrams.py
Add --sequences-only to rebuild only the sequence figures and chapter.
"""

import argparse
from functools import lru_cache
from html import escape
from math import hypot
import re

from PIL import Image, ImageFont

from postprocess_png import process

import figstyle as fs
from textbook_models import Canvas, FONT_DIR, ROOT
from design_sequences import SEQUENCES


DESIGN = ROOT / "docs" / "面向对象设计"
LINE = "#3D4145"
LIFELINE = "#8B9095"
ACTIVATION = "#F3DFE6"
ACTIVATION_BORDER = "#A25770"
WHITE = "#FFFFFF"


@lru_cache
def font(size):
    return ImageFont.truetype(str(FONT_DIR / "msyh.ttc"), size * 3)


def text_width(value, size):
    return font(size).getlength(value) / 3


def wrapped(value, width):
    code_token = r"\{[a-z_]+\}|\??[A-Za-z0-9_]+(?:[.=][A-Za-z0-9_]+)*"
    tokens = re.findall(code_token, value)
    size = 15
    while size > 12 and any(text_width(token, size) > width for token in tokens):
        size -= 1
    # A long identifier may use the gap beside the lifelines above its arrow.
    width = min(width + 25, max([width, *(text_width(token, size) for token in tokens)]))
    lines = []
    for paragraph in value.splitlines():
        while text_width(paragraph, size) > width:
            protected = {index for match in re.finditer(code_token, paragraph)
                         if text_width(match.group(), size) <= width
                         for index in range(match.start() + 1, match.end())}
            end = len(paragraph)
            while end > 1 and (
                end in protected
                or (end < len(paragraph) and paragraph[end] in ",)）")
                or text_width(paragraph[:end], size) > width
            ):
                end -= 1
            for index in range(end, max(1, int(end * 0.62)), -1):
                if (index not in protected and paragraph[index - 1] in " /,，、·"
                        and (index == len(paragraph) or paragraph[index] not in ",)）")):
                    end = index
                    break
            lines.append(paragraph[:end].strip())
            paragraph = paragraph[end:].lstrip()
        lines.append(paragraph)
    return size, lines


class UML(Canvas):
    def box(self, x, y, w, h, fill=WHITE, stroke=LINE):
        self.shape("rect", x, y, w, h, fill, stroke)

    def stroke(self, points, *, head="none", dash=0, color=LINE, weight=1.15):
        pixels = [(round(x * 3), round(y * 3)) for x, y in points]
        if dash:
            for (x, y), (ex, ey) in zip(points, points[1:]):
                length = hypot(ex - x, ey - y)
                stride = dash + 4
                for start in range(0, round(length), stride):
                    end = min(start + dash, length)
                    segment = [(3 * (x + (ex - x) * offset / length),
                                3 * (y + (ey - y) * offset / length))
                               for offset in (start, end)]
                    self.d.line(segment, fill=color, width=round(weight * 3))
        else:
            self.d.line(pixels, fill=color, width=round(weight * 3))
        xy = " ".join(f"{x},{y}" for x, y in points)
        dashed = f' stroke-dasharray="{dash},4"' if dash else ""
        self.svg.append(f'<polyline points="{xy}" fill="none" stroke="{color}" '
                        f'stroke-width="{weight}"{dashed}/>')
        style = f"strokeColor={color};strokeWidth={weight};startArrow=none;endArrow={head};"
        if dash:
            style += f"dashed=1;dashPattern={dash} 4;"
        if head != "none":
            self.arrowhead(points[-2], points[-1], head == "block", color, weight)
            style += f"endFill={int(head == 'block')};endSize=8;"
        self.cells.append(fs.poly(self.key(), points, style))

    def arrowhead(self, start, end, filled, color, weight):
        x, y = end
        dx, dy = x - start[0], y - start[1]
        length = hypot(dx, dy)
        dx, dy = dx / length, dy / length
        tips = [(x - 9 * dx + 3.8 * dy, y - 9 * dy - 3.8 * dx),
                end, (x - 9 * dx - 3.8 * dy, y - 9 * dy + 3.8 * dx)]
        points = [(round(a * 3), round(b * 3)) for a, b in tips]
        if filled:
            self.d.polygon(points, fill=color)
        else:
            self.d.line(points, fill=color, width=round(weight * 3))
        xy = " ".join(f"{a},{b}" for a, b in tips)
        shape = "polygon" if filled else "polyline"
        self.svg.append(f'<{shape} points="{xy}" fill="{color if filled else "none"}" '
                        f'stroke="{color}" stroke-width="{weight}"/>')

    def label_mask(self, value, cx, y, size=15, bold=False):
        w = round(text_width(value, size) * (1.08 if bold else 1.0)) + 12
        h = 22
        x = cx - w / 2
        # The white mask clears only the lifeline below the label.
        self.d.rectangle((round(x * 3), round(y * 3), round((x + w) * 3), round((y + h) * 3)),
                         fill=WHITE)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{WHITE}"/>')
        self.cells.append(fs.vertex(self.key(), "", "fillColor=#FFFFFF;strokeColor=none;", x, y, w, h))
        self.text(value, x, y, w, h, size, bold)

    def save_figure(self, group, filename, title, caption, postprocess=False):
        path = DESIGN / "图稿" / group / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        self.im.resize((self.w * 2, self.h * 2), Image.Resampling.LANCZOS).save(
            path.with_suffix(".png"), optimize=True)
        if postprocess:
            # 规范 §6：裁到内容、四周补 32px，并打印满宽等效字号
            process(path.with_suffix(".png"), font_size=BODY_SIZE)
        fs.save(path.with_suffix(".drawio"), self.cells, self.w, self.h)
        path.with_suffix(".svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="title desc">'
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(caption)}</desc>'
            f'<rect width="100%" height="100%" fill="white"/>'
            f'<g font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif" fill="{fs.INK}">'
            + "".join(self.svg) + "</g></svg>\n", encoding="utf-8")
        return group, filename, title, caption


def class_box(diagram, name, x, y, w, fields=(), methods=(), stereotype=""):
    title_height = 49 if stereotype else 33
    compartments = [values for values in (fields, methods) if values]
    diagram.box(x, y, w, title_height + sum(10 + len(values) * 23 for values in compartments))
    if stereotype:
        diagram.text(f"«{stereotype}»", x + 5, y + 3, w - 10, 21, 13)
    diagram.text(name, x + 5, y + title_height - 30, w - 10, 27, 17, True)
    top = y + title_height
    for values in compartments:
        diagram.stroke([(x, top), (x + w, top)])
        for index, value in enumerate(values):
            diagram.text(value, x + 8, top + 5 + 23 * index, w - 16, 22, 15, align="left")
        top += 10 + len(values) * 23


def association(diagram, points, role, left, right, label):
    diagram.line(points, arrow=False, color=LINE)
    diagram.label_mask("1", *left, size=14)
    diagram.label_mask("0..*", *right, size=14)
    diagram.label_mask(role, *label, size=14)


def dependency(diagram, points, label=None):
    diagram.stroke(points, head="open", dash=6)
    if label:
        diagram.label_mask(*label, size=14)


# ------------------------------------------------ 模块设计类图（绘图规范 v2.1）
# 严格按 docs/绘图规范.md：色值只用 §2.1 的七色（均取自 figstyle）、类框宽 210（§5）、
# 正文 14 / 类名 14 粗 / 标签与多重性 12（§2.2）、行距 24、间距 ≥24（§2.4）、
# 关联 open 箭头且关联名与多重性同侧（§5）、画布四周 24px（§2.4）。
CARD_W = 210            # §5 类框宽
GRID_GAP = 58           # §2.4 元素间距（≥24），横向
ROW_GAP = 80            # 行间距：给竖线上的多重性与关联名留位置
PAGE_MARGIN = 24        # §2.4 画布留白
TITLE_H = 40
BODY_H = 24             # §2.2 行距
NAME_SIZE = 14          # §2.2 类名 14 粗体
BODY_SIZE = 14          # §3 类模型图正文 13–14，取 14 以满足 ≥8.1pt 的满宽预算
LABEL_SIZE = 12         # §2.2 连线标签与多重性


def rows_of(value, width, size=BODY_SIZE):
    """把一条属性/操作折行（§3：宽度超标就重排、给长句换行，不缩字号）。

    断点取最靠右且能放下的一处：空格之后、左括号之后、逗号加空格之后，
    因此 "+ confirm_delete(comment_id)" 断在括号后，不会只剩一个 "+"。
    """
    lines, rest = [], value
    while rest:
        if text_width(rest, size) <= width:
            lines.append(rest)
            break
        best = 0
        for index, char in enumerate(rest):
            if char == "(" or (char == "," and rest[index + 1:index + 2] == " "):
                cut = index + 1
            elif char == " " and index:
                cut = index
            else:
                continue
            if cut > best and text_width(rest[:cut].rstrip(), size) <= width:
                best = cut
        best = best or len(rest)
        lines.append(rest[:best].rstrip())
        rest = rest[best:].lstrip()
    return lines


def card_height(fields=(), methods=()):
    inner = CARD_W - 14
    fields_rows = sum(len(rows_of(value, inner)) for value in fields)
    method_rows = sum(len(rows_of(value, inner)) for value in methods)
    return TITLE_H + 6 + fields_rows * BODY_H + (4 + method_rows * BODY_H if method_rows else 0) + 6


def class_card(diagram, name, x, y, stereotype, fields=(), methods=()):
    """三栏类框：类名栏（浅主色填充）+ 属性栏 + 操作栏，栏高按内容自适应。"""
    pad, inner = 6, CARD_W - 14
    h = card_height(fields, methods)
    diagram.box(x, y, CARD_W, h, fill=WHITE, stroke=fs.MAIN)
    diagram.box(x, y, CARD_W, TITLE_H, fill=fs.MAIN_LIGHT, stroke=fs.MAIN)
    diagram.text(f"«{stereotype}»", x + 4, y + 3, CARD_W - 8, 18, 12)
    diagram.text(name, x + 4, y + 16, CARD_W - 8, 22, NAME_SIZE, True)
    top = y + TITLE_H + pad
    for value in fields:
        for line in rows_of(value, inner):
            diagram.text(line, x + pad, top, CARD_W - 10, BODY_H - 2, BODY_SIZE, align="left")
            top += BODY_H
    if methods:
        diagram.stroke([(x, top + 2), (x + CARD_W, top + 2)], color=fs.MAIN, weight=1.5)
        top += 4
        for value in methods:
            for line in rows_of(value, inner):
                diagram.text(line, x + pad, top, CARD_W - 10, BODY_H - 2, BODY_SIZE, align="left")
                top += BODY_H
    return y + h


def link(diagram, points, label=None, at=None, dashed=False):
    """一条连线：调用依赖虚线、业务关联实线，均为 open 箭头（§2.3），标签 12 号衬白（§2.2/§2.4）。"""
    diagram.stroke(points, head="open", dash=5 if dashed else 0, color=fs.EDGE, weight=1.5)
    if label:
        diagram.label_mask(label, *at, size=LABEL_SIZE)


def figure_legend(diagram, x, y):
    """图例：依赖、关联、多重性、可见性（§2.1 七色）。"""
    diagram.text("legend", x, y, CARD_W - 12, 20, LABEL_SIZE, True, align="left")
    diagram.stroke([(x + 4, y + 34), (x + 74, y + 34)], head="open", dash=5,
                   color=fs.EDGE, weight=1.5)
    diagram.text("dependency", x + 82, y + 24, CARD_W - 90, 20, LABEL_SIZE, align="left")
    diagram.stroke([(x + 4, y + 66), (x + 74, y + 66)], head="open", color=fs.EDGE, weight=1.5)
    diagram.text("association", x + 82, y + 56, CARD_W - 90, 20, LABEL_SIZE, align="left")
    diagram.text("1 / 0..*  multiplicity", x, y + 88, CARD_W - 8, 20, LABEL_SIZE, align="left")
    diagram.text("+ public    − private", x, y + 112, CARD_W - 8, 20, LABEL_SIZE, align="left")


ENTITIES = {
    "User": ("id: int", "username: str", "email: str", "password_hash: str", "role: str", "created_at: datetime"),
    "Category": ("id: int", "name: str"),
    "Album": ("id: int", "owner_id: int", "category_id: int", "name: str", "visibility: str",
              "version: int", "created_at: datetime", "updated_at: datetime"),
    "Photo": ("id: int", "album_id: int", "uploader_id: int", "original_path: str", "thumbnail_path: str",
              "upload_id: UUID", "media_type: str", "size_bytes: int", "created_at: datetime"),
    "Comment": ("id: int", "photo_id: int", "user_id: int", "body: str", "created_at: datetime"),
    "PhotoLike": ("user_id: int", "photo_id: int", "created_at: datetime"),
}

SERVICES = {
    "AccountService": ("register(data) → User", "authenticate(data) → User",
                       "issue_token(user) → str", "resolve_user(token) → User"),
    "AlbumService": ("list_albums(actor, scope) → list[Album]", "get_album(actor, album_id, scope) → Album",
                     "create(actor, data) → Album", "update(actor, album_id, data) → Album"),
    "CategoryService": ("list_categories() → list[Category]", "create(actor, data) → Category",
                        "update(actor, category_id, data) → Category", "delete(actor, category_id) → None"),
    "AlbumAccessPolicy": ("require_visible(actor, album_id) → Album", "require_owned(actor, album_id) → Album"),
    "PhotoService": ("upload(actor, album_id, file, upload_id) → tuple[Photo, bool]",
                     "list_photos(actor, album_id) → list[Photo]", "get_detail(actor, photo_id) → PhotoDetail",
                     "open_image(actor, photo_id, variant) → ImageStream"),
    "LocalPhotoStorage": ("save(path, stream) → None", "open(path) → ImageStream", "remove(path) → None"),
    "CommentService": ("create(actor, photo_id, body) → Comment", "delete(actor, photo_id, comment_id) → None"),
    "LikeService": ("set_liked(actor, photo_id, liked) → LikeState",),
}


def entity_diagram():
    d = UML(974, 705)
    for route, role, start, end, label in (
        ([(240, 111), (380, 111)], "owns", (253, 88), (361, 88), (309, 88)),
        ([(735, 111), (615, 111)], "classifies", (722, 88), (633, 88), (677, 88)),
        ([(102, 205), (102, 432)], "authors", (83, 209), (75, 405), (67, 346)),
        ([(240, 161), (293, 161), (293, 461), (380, 461)], "uploads",
         (253, 136), (361, 438), (327, 405)),
        ([(186, 205), (186, 331), (836, 331), (836, 432)], "likes",
         (167, 209), (863, 403), (656, 306)),
        ([(495, 251), (495, 432)], "contains", (476, 254), (467, 405), (548, 354)),
        ([(380, 516), (240, 516)], "has comments", (367, 524), (258, 524), (310, 491)),
        ([(615, 516), (725, 516)], "has likes", (630, 524), (707, 524), (670, 491)),
    ):
        association(d, route, role, start, end, label)
    for name, x, y, w in (
        ("User", 25, 24, 215), ("Album", 380, 24, 235), ("Category", 735, 24, 215),
        ("Comment", 25, 432, 215), ("Photo", 380, 432, 235), ("PhotoLike", 725, 432, 225),
    ):
        fields = tuple(f"- {field}" for field in ENTITIES[name])
        if name == "PhotoLike":
            fields += ("{unique(user_id, photo_id)}",)
        class_box(d, name, x, y, w, fields)
    return d


def class_cards(width, height, cards, arrows, *, operation_overrides=None, associations=()):
    d = UML(width, height)
    for points in arrows:
        dependency(d, points)
    for points, role in associations:
        d.stroke(points, head="open")
        d.label_mask(*role, size=14)
    overrides = operation_overrides or {}
    for name, x, y, w, kind in cards:
        methods = overrides.get(name, tuple(f"+ {method}" for method in SERVICES.get(name, ())))
        class_box(d, name, x, y, w, methods=methods, stereotype=kind)
    return d


def account_diagram():
    return class_cards(608, 202, [
        ("AccountService", 24, 25, 330, "service"), ("User", 434, 88, 150, "entity"),
    ], [[(354, 112), (434, 112)]])


def album_diagram():
    d = class_cards(928, 437, [
        ("AlbumService", 24, 24, 401, "service"), ("CategoryService", 520, 260, 384, "service"),
        ("AlbumAccessPolicy", 24, 260, 401, "policy"), ("Album", 520, 79, 160, "entity"),
        ("Category", 744, 79, 160, "entity"),
    ], [
        [(133, 175), (133, 260)],
        [(425, 54), (824, 54), (824, 79)],
        [(425, 105), (520, 105)],
        [(425, 304), (478, 304), (478, 196), (555, 196), (555, 128)],
        [(612, 260), (612, 128)],
        [(824, 260), (824, 128)],
    ])
    d.label_mask("checks references", 692, 192, size=14)
    return d


def photo_diagram():
    return class_cards(872, 530, [
        ("PhotoService", 24, 24, 540, "service"), ("Photo", 664, 49, 160, "entity"),
        ("AlbumAccessPolicy", 24, 280, 402, "policy"), ("LocalPhotoStorage", 475, 280, 349, "storage"),
        ("User", 29, 455, 168, "entity"), ("Comment", 246, 455, 168, "entity"),
        ("PhotoLike", 465, 455, 168, "entity"),
    ], [
        [(564, 74), (664, 74)],
        [(136, 198), (136, 280)],
        [(24, 161), (12, 161), (12, 480), (29, 480)],
        [(451, 198), (451, 430), (329, 430), (329, 455)],
        [(564, 150), (843, 150), (843, 480), (633, 480)],
    ], operation_overrides={
        "PhotoService": (*[f"+ {operation}" for operation in SERVICES["PhotoService"]],
                         "- make_thumbnail(file)"),
    }, associations=[
        ([(524, 198), (524, 280)], ("storage", 563, 248)),
    ])


def interaction_diagram():
    """图 06 评论与点赞设计类图（绘图规范 v2.1）：界面—控制入口—服务—访问策略—实体。"""
    c1, c2, c3 = PAGE_MARGIN, PAGE_MARGIN + CARD_W + GRID_GAP, PAGE_MARGIN + 2 * (CARD_W + GRID_GAP)

    page = ("- comments: CommentView[]", "- like: LikeState", "- current_user_id: int")
    page_ops = ("+ submit_comment(body)", "+ confirm_delete(comment_id)", "+ toggle_like(liked)")
    router_ops = ("+ create(photo_id, body): CommentView",
                  "+ delete(photo_id, comment_id): None",
                  "+ set_like(photo_id, liked): LikeState")
    comment_ops = ("+ create(actor, photo_id, body): Comment",
                   "+ delete(actor, photo_id, comment_id): None",
                   "- ensure_author(actor, comment): None")
    like_ops = ("+ set_liked(actor, photo_id, liked): LikeState",
                "+ load_state(actor, photo_id): LikeState",
                "- count(photo_id): int")
    policy_ops = ("+ require_visible(actor, album_id): Album",)
    user_fields = ("- id: int", "- username: str")
    comment_fields = ("- id: int", "- photo_id: int", "- user_id: int", "- body: str",
                      "- created_at: datetime")
    photo_fields = ("- id: int", "- album_id: int", "- created_at: datetime")
    like_fields = ("- user_id: int", "- photo_id: int", "- created_at: datetime",
                   "{PK (user_id, photo_id)}")

    r1 = PAGE_MARGIN
    h1 = max(card_height(page, page_ops), card_height((), router_ops),
             card_height((), comment_ops))
    r2 = r1 + h1 + ROW_GAP
    h2 = max(card_height((), policy_ops), card_height((), like_ops))
    r3 = r2 + h2 + ROW_GAP
    h3 = max(card_height(like_fields), card_height(user_fields))
    r4 = r3 + h3 + ROW_GAP
    h4 = max(card_height(photo_fields), card_height(comment_fields))
    height = r4 + h4 + PAGE_MARGIN

    lane = c3 + CARD_W + 6          # 右侧通道：评论服务写评论记录
    d = UML(lane + PAGE_MARGIN + 2, height)   # 右边缘留 24px，另计通道线宽
    class_card(d, "PhotoDetailPage", c1, r1, "boundary", page, page_ops)
    class_card(d, "InteractionRouter", c2, r1, "control", (), router_ops)
    class_card(d, "CommentService", c3, r1, "service", (), comment_ops)
    class_card(d, "LikeService", c1, r2, "service", (), like_ops)
    class_card(d, "AlbumAccessPolicy", c2, r2, "policy", (), policy_ops)
    class_card(d, "PhotoLike", c2, r3, "entity", like_fields)
    class_card(d, "User", c3, r3, "entity", user_fields)
    class_card(d, "Photo", c2, r4, "entity", photo_fields)
    class_card(d, "Comment", c3, r4, "entity", comment_fields)

    g1 = c1 + CARD_W + 30           # c1/c2 通道中线
    g2 = c3 - 30                    # c2/c3 通道中线
    # 界面 → 控制入口；控制入口 → 评论服务（同行）、点赞服务（下一行）
    link(d, [(c1 + CARD_W, r1 + 100), (c2, r1 + 100)], "request", (c1 + CARD_W + 30, r1 + 70), True)
    link(d, [(c2 + CARD_W, r1 + 100), (c3, r1 + 100)], "call", (c2 + CARD_W + 30, r1 + 70), True)
    link(d, [(c2, r1 + 160), (g1, r1 + 160), (g1, r2 - 30), (c1 + CARD_W // 2, r2 - 30),
             (c1 + CARD_W // 2, r2)], "call", (g1 + 36, r1 + h1 + 4), True)
    # 两个服务 → 访问策略（依赖）
    link(d, [(c1 + CARD_W, r2 + 80), (c2, r2 + 80)], "checks", (c1 + CARD_W + 30, r2 + 50), True)
    link(d, [(c3, r1 + 170), (g2, r1 + 170), (g2, r2 + 60), (c2 + CARD_W, r2 + 60)],
         "visibility", (g2 - 34, r1 + h1 + 4), True)
    # 服务 → 实体：评论服务写 Comment 记录，点赞服务写 PhotoLike 记录
    link(d, [(c3 + CARD_W, r1 + 150), (lane, r1 + 150), (lane, r4 + 90), (c3 + CARD_W, r4 + 90)],
         "writes", (lane - 34, r3 - 50), True)
    link(d, [(c1 + CARD_W // 2, r2 + h2), (c1 + CARD_W // 2, r3 - 30), (c2 + CARD_W // 2, r3 - 30),
             (c2 + CARD_W // 2, r3)], "writes", (c1 + CARD_W // 2 + 120, r3 - 56), True)
    # 业务关联：评论—作者、评论—照片、点赞—点赞人、点赞—照片（箭头指向 0..* 端）
    link(d, [(c3, r3 + 56), (c2 + CARD_W, r3 + 56)])
    d.label_mask("0..*", c2 + CARD_W + 16, r3 + 30, size=LABEL_SIZE)
    d.label_mask("1", c3 - 16, r3 + 30, size=LABEL_SIZE)
    d.label_mask("likes", c2 + CARD_W + 30, r3 + 4, size=LABEL_SIZE)
    link(d, [(c3 + CARD_W // 2, r3 + 100), (c3 + CARD_W // 2, r4)])
    d.label_mask("1", c3 + CARD_W // 2 + 40, r3 + 104, size=LABEL_SIZE)
    d.label_mask("authors", c3 + CARD_W // 2 + 52, r3 + 130, size=LABEL_SIZE)
    d.label_mask("0..*", c3 + CARD_W // 2 + 40, r4 - 24, size=LABEL_SIZE)
    link(d, [(c2 + CARD_W, r4 + 60), (c3, r4 + 60)])
    d.label_mask("1", c2 + CARD_W + 16, r4 + 34, size=LABEL_SIZE)
    d.label_mask("0..*", c3 - 16, r4 + 34, size=LABEL_SIZE)
    d.label_mask("photo", c2 + CARD_W + 32, r4 + 8, size=LABEL_SIZE)
    link(d, [(c2 + CARD_W // 2, r4), (c2 + CARD_W // 2, r3 + h3)])
    d.label_mask("1", c2 + CARD_W // 2 + 40, r4 - 24, size=LABEL_SIZE)
    d.label_mask("0..*", c2 + CARD_W // 2 + 40, r3 + h3 + 2, size=LABEL_SIZE)
    d.label_mask("likes", c2 + CARD_W // 2 + 36, r3 + h3 + 32, size=LABEL_SIZE)

    figure_legend(d, c1, r3 + 20)
    return d


def package_tab(d, x, y, w, h, label, tab_w):
    tab_h = 26
    d.box(x, y + tab_h, w, h - tab_h)
    d.box(x, y, tab_w, tab_h)
    d.text(label, x + 5, y + 2, tab_w - 10, 22, 15, True, "left")


def package_diagram():
    d = UML(1016, 744)
    for x, y, w, h, label, tab in (
        (24, 22, 968, 92, "视图层 · Vue", 160),
        (24, 166, 968, 92, "控制层 · FastAPI", 185),
        (24, 314, 968, 246, "模型层 · 业务与持久化", 223),
        (52, 360, 187, 79, "账户管理", 105),
        (290, 360, 187, 79, "相册管理", 105),
        (528, 360, 187, 79, "照片管理", 105),
        (766, 360, 188, 79, "评论与点赞", 125),
        (52, 477, 902, 62, "SQLAlchemy 持久化", 181),
    ):
        package_tab(d, x, y, w, h, label, tab)
    d.text("注册与登录页   /   相册页   /   照片详情页   /   类别管理页", 56, 63, 900, 30, 17)
    d.text("认证路由   /   相册与类别路由   /   照片路由   /   评论与点赞路由", 56, 207, 900, 30, 17)
    d.text("解析当前用户", 56, 397, 180, 30, 16)
    d.text("相册访问策略", 294, 397, 179, 30, 16)
    d.text("照片服务与本地存储", 531, 397, 181, 30, 15)
    d.text("评论服务与点赞服务", 769, 397, 181, 30, 15)
    d.text("ORM 实体与事务", 307, 504, 390, 30, 16)
    d.box(160, 647, 195, 69)
    d.box(690, 647, 195, 69)
    d.text("«database»", 165, 654, 185, 22, 14)
    d.text("PostgreSQL", 165, 678, 185, 26, 17, True)
    d.text("«file system»", 695, 654, 185, 22, 14)
    d.text("uploads/ 原图与缩略图", 695, 678, 185, 26, 15)
    for route, label in (
        ([(506, 114), (506, 166)], ("HTTP /api", 563, 127)),
        ([(146, 258), (146, 296), (265, 296), (265, 392), (239, 392)], ("解析当前身份", 206, 269)),
        ([(506, 258), (506, 340)], ("调用模块服务", 568, 285)),
        ([(528, 409), (477, 409)], None),
        ([(861, 439), (861, 454), (425, 454), (425, 439)], ("检查相册访问权限", 606, 458)),
        ([(147, 439), (147, 477)], None),
        ([(339, 439), (339, 503)], None),
        ([(582, 439), (582, 503)], None),
        ([(916, 439), (916, 503)], None),
        ([(257, 539), (257, 647)], ("读写数据", 308, 594)),
        ([(700, 439), (700, 469), (970, 469), (970, 690), (885, 690)], ("读写图片", 921, 598)),
    ):
        dependency(d, route, label)
    return d


class Sequence:
    GAP = 192
    FIRST = 85
    LIFELINE_TOP = 100

    def __init__(self, participants):
        self.participants = participants
        self.positions = {
            key: self.FIRST + index * self.GAP
            for index, (key, _, _) in enumerate(participants)
        }
        self.w = max(self.positions.values()) + self.FIRST + 25
        self.y = self.LIFELINE_TOP + 22
        self.messages = []
        self.frames = []
        self.activations = {}

    def place(self, events, pending=None):
        if pending is None:
            pending = {}
        for event in events:
            kind, *args = event
            if kind == "alt":
                self.fragment(args, pending)
                continue
            source, target, value = args
            x, ex = self.positions[source], self.positions[target]
            span = self.GAP - 18 if source == target else abs(x - ex) - 14
            message = f"return {value}" if kind == "reply" else value
            label = f"{len(self.messages) + 1}: {message}"
            size, lines = wrapped(label, span)
            label_y = self.y + 3
            line_y = label_y + len(lines) * 21 + 3
            exit_y = line_y + (18 if source == target else 0)
            self.messages.append((kind, x, ex, label_y, line_y, exit_y, size, lines))
            self.y = exit_y + 9
            if source == target:
                continue
            if kind == "call":
                pending.setdefault((source, target), []).append(line_y)
            elif pending.get((target, source)):
                start = pending[(target, source)].pop()
                key = (x, start)
                self.activations[key] = max(line_y, self.activations.get(key, start))

    def fragment(self, branches, pending):
        start = self.y
        rows = []
        exits = []
        for index, (guard, events) in enumerate(branches):
            rows.append((self.y, guard))
            self.y += 31 if index == 0 else 29
            branch_pending = {key: calls.copy() for key, calls in pending.items()}
            self.place(events, branch_pending)
            exits.append(branch_pending)
            self.y += 3
        # A call made before the frame can return in any of its operands.
        for key, calls in pending.items():
            pending[key] = [call for call in calls if any(call in branch[key] for branch in exits)]
        self.frames.append((start, self.y, rows))
        self.y += 9

    def draw(self):
        d = UML(self.w, self.y + 28)
        for key, name, role in self.participants:
            x = self.positions[key]
            d.stroke([(x, self.LIFELINE_TOP), (x, self.y + 7)], dash=5, color=LIFELINE)
            if role == "infrastructure":
                top = self.LIFELINE_TOP - 52
                d.box(x - 83, top, 166, 52)
                d.text(name, x - 80, top + 2, 160, 48, 15)
            else:
                if role == "actor":
                    self.actor(d, x)
                else:
                    d.object_icon(x, 41, role)
                d.text(name, x - 83, 72, 166, 24, 15, underline=True)
        left, right = 20, self.w - 20
        for start, end, rows in self.frames:
            d.stroke([(left, start), (right, start), (right, end), (left, end), (left, start)])
            d.stroke([(left, start + 23), (left + 53, start + 23),
                      (left + 63, start + 13), (left + 63, start)])
            d.text("alt", left + 3, start + 1, 55, 22, 14, True)
            for index, (y, guard) in enumerate(rows):
                if index:
                    d.stroke([(left, y), (right, y)], dash=7, color=LIFELINE)
                label = f"[{guard}]"
                guard_x = left + (77 if not index else 15)
                d.label_mask(label, guard_x + text_width(label, 15) / 2, y + 4)
        for (x, start), end in self.activations.items():
            d.box(x - 4, start, 8, end - start, ACTIVATION, ACTIVATION_BORDER)
        for kind, x, ex, label_y, line_y, exit_y, size, lines in self.messages:
            if x == ex:
                start = x + self.activation_inset(x, line_y)
                end = x + self.activation_inset(x, exit_y)
                d.stroke([(start, line_y), (x + 24, line_y), (x + 24, exit_y), (end, exit_y)], head="block")
                cx = x + 9 + max(text_width(line, size) for line in lines) / 2
            else:
                sign = 1 if ex > x else -1
                start = x + sign * self.activation_inset(x, line_y)
                end = ex - sign * self.activation_inset(ex, line_y)
                d.stroke([(start, line_y), (end, line_y)],
                         head="open" if kind == "reply" else "block", dash=7 if kind == "reply" else 0)
                cx = (x + ex) / 2
            for idx, line in enumerate(lines):
                d.label_mask(line, cx, label_y + idx * 21, size)
        return d

    def activation_inset(self, x, y):
        return 4 if any(a == x and start <= y <= end for (a, start), end in self.activations.items()) else 0

    @staticmethod
    def actor(d, x):
        d.shape("circle", x - 6, 20, 12, 12, WHITE, LINE)
        for points in (
            [(x, 32), (x, 55)], [(x - 12, 39), (x + 12, 39)],
            [(x, 55), (x - 12, 66)], [(x, 55), (x + 12, 66)],
        ):
            d.stroke(points)


def write_chapter(filename, heading, figures):
    blocks = [f"# {heading}"]
    for group, name, title, caption, *rest in figures:
        relative = f"图稿/{group}/{name}"
        note = rest[0] if rest else caption
        blocks.extend((f"## {title}", f"![{title}]({relative}.png)", *note.split("\n\n")))
    (DESIGN / filename).write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


INTERACTION_NOTE = """\
本图覆盖「对照片评论」与「对照片点赞」两个用例，按「界面 → 控制入口 → 服务 → 访问策略 → 实体」分层。上排左起依次是 PhotoDetailPage（«boundary»，Vue 照片详情页，持有 comments、like 与 current_user_id）、InteractionRouter（«control»，评论与点赞路由，三个操作对应发表评论、删除评论、设置点赞三个接口）和 CommentService（«service»）；第二排是 LikeService 与 AlbumAccessPolicy（«policy»，提供相册可见性判断）；下部四个实体按相邻关系摆放：PhotoLike 与 Photo 在中列、User 与 Comment 在右列，四条关联正好连成一个环。虚线带空心箭头是调用依赖，实线带空心箭头是业务关联（箭头指向 0..* 端），关联名与两端多重性同放在线的上方，图例见左下角。

实体的字段按本模块的使用范围裁剪：`Comment` 保留 `id`、`photo_id`、`user_id`、`body`、`created_at`；`PhotoLike` 保留 `user_id`、`photo_id`、`created_at`，并以 `{PK (user_id, photo_id)}` 标出联合主键；`Photo` 只需要 `id` 与 `album_id`，因为评论和点赞都要先用照片所属相册复核可见性；`User` 只需要 `id` 与 `username`，用于回显评论作者和点赞人。服务只列关键操作：`CommentService.create`/`delete` 与 `LikeService.set_liked`/`load_state` 对应接口，`ensure_author` 与 `count` 是服务内部的归属校验和计数。`InteractionRouter` 对应包图中的「评论与点赞路由」，评论接口与点赞接口共用这一个入口，按路径和方法分派到两个服务。

**发表评论与删除本人评论。** 页面调用 `submit_comment(body)`，路由以 `create(photo_id, body)` 转交服务。`CommentService.create` 先按照片记录的 `album_id` 调 `AlbumAccessPolicy.require_visible`，照片不存在或当前不可见即返回 `404 PHOTO_UNAVAILABLE`；再把正文去首尾空白，校验 1–200 字符；最后在事务内写入 `photo_id`、当前用户的 `user_id`、正文和创建时间，返回的 `CommentView` 由页面追加到列表尾部。删除评论分两步校验：先用路径中的 `photo_id` 与 `comment_id` 定位记录，评论不存在或属于另一张照片时返回 `404 COMMENT_NOT_FOUND`；再由 `ensure_author` 比较 `comment.user_id` 与当前 `actor.id`，不相等返回 `403 COMMENT_NOT_OWNED`。页面只按 `author.id == current_user_id` 显示删除入口，服务端的这次比较才是最终判据，改请求参数也删不掉他人评论。

**点赞、重复点赞与取消点赞。** 三个动作都由 `LikeService.set_liked(actor, photo_id, liked)` 处理，写入前同样先按 `Photo.album_id` 复核可见性。`photo_likes` 以 `(user_id, photo_id)` 为联合主键，一个用户对一张照片最多一条记录，因此同一用户对同一照片的三次操作结果如下。

| 操作 | 请求 | 事务内写入 | 返回 |
| --- | --- | --- | --- |
| 点赞 | `liked = true` | 按联合主键插入 `user_id`、`photo_id`、`created_at` | `liked = true`，`like_count` 加 1 |
| 重复点赞 | `liked = true` | 联合主键冲突，保留原记录与原创建时间，不新增 | `liked = true`，`like_count` 不变 |
| 取消点赞 | `liked = false` | 按联合主键删除本人记录，记录已不存在时视为已取消 | `liked = false`，`like_count` 减 1 或保持 |
| 读取状态 | `GET /api/photos/{photo_id}` | 不写入 | `load_state` 返回同一口径的 `LikeState` |

本人状态和点赞数在同一次查询中取得：`count(photo_id)` 统计该照片的记录数作为 `like_count`，再判断本人的联合键记录是否存在作为 `liked`，两者组成 `LikeState`，随事务提交后返回，页面用回包更新按钮与计数。重复点赞和重复取消都按幂等处理，连续点击既不会产生第二条记录，也不会返回错误。

**与其他图稿的口径。** 多重性与图 02 全局领域实体类图、《公共设计约定》第 4 节一致：`User` 1 对 0..* `Comment`（authors）、`Photo` 1 对 0..* `Comment`（has comments）、`User` 1 对 0..* `PhotoLike`（likes）、`Photo` 1 对 0..* `PhotoLike`（has likes），`PhotoLike` 的联合主键与 ER 图的 `photo_likes` 表一致。操作名与图 14、图 15 两张顺序图对应：评论侧为 `create`、`delete`、`require_visible`，点赞侧为 `set_liked` 以及内部的插入、删除和状态查询。"""


def write_class_figures():
    classes = []
    for number, (name, caption, build, note) in enumerate((
        ("全局领域实体类图", "每张照片属于一个相册，相册可以为空。评论与点赞都关联用户和照片，同一用户对同一张照片最多有一条点赞记录。", entity_diagram, None),
        ("账户管理设计类图", "账户服务负责注册、凭据验证和会话处理。", account_diagram, None),
        ("相册管理设计类图", "相册服务处理创建和修改，访问策略校验可见性或归属。类别服务删除前查询相册引用，数据库外键在并发写入时仍会阻止删除已被引用的类别。", album_diagram, None),
        ("照片管理设计类图", "照片服务通过访问策略检查相册权限。上传时由照片服务生成缩略图，由其持有的本地存储对象保存原图和缩略图。", photo_diagram, None),
        ("评论与点赞设计类图", "评论和点赞共用相册可见性检查与同一个控制入口，评论按作者和照片关联，点赞以联合主键记录本人状态。", interaction_diagram, INTERACTION_NOTE),
    ), 2):
        figure = build().save_figure("类图", f"{number:02}_{name}", f"图 {number:02} {name}", caption,
                                       postprocess=bool(note))   # 图 06 按 §6 跑后处理
        classes.append(tuple(figure) + ((note,) if note else ()))
    write_chapter("04_设计类图.md", "设计类图", classes)


def write_package_figure():
    package = package_diagram().save_figure("包图", "01_系统MVC包图", "图 01 系统 MVC 包图",
                                            "视图调用路由，业务模块复用账户身份与相册访问规则。")
    write_chapter("05_包图.md", "包图", [package])


def write_sequence_figures():
    sequences = []
    for number, (name, caption, participants, events) in enumerate(SEQUENCES, 7):
        sequence = Sequence(participants)
        sequence.place(events)
        title = f"{name}顺序图"
        sequences.append(sequence.draw().save_figure(
            "顺序图", f"{number:02}_{title}", f"图 {number:02} {title}", caption))
    write_chapter("06_顺序图.md", "顺序图", sequences)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sequences-only", action="store_true")
    args = parser.parse_args()
    if not args.sequences_only:
        write_class_figures()
        write_package_figure()
    write_sequence_figures()
