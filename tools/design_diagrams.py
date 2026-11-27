"""Generate the UML figures, database ER diagram, and UML chapters.

Run from the repository root: python tools/design_diagrams.py
Add --classes-only or --sequences-only to limit generation.
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


COL_LEFT, COL_CENTER, COL_RIGHT = 24, 286, 548
THREE_COLUMN_WIDTH = COL_RIGHT + CARD_W + PAGE_MARGIN


def fields_of(name, *names):
    return tuple(f"- {field}" for field in ENTITIES[name]
                 if not names or field.split(":")[0] in names)


def operations_of(name):
    return tuple(f"+ {method}" for method in SERVICES[name])


def multiplicity_link(diagram, points, labels):
    link(diagram, points)
    for text, center, top in labels:
        diagram.label_mask(text, center, top, size=LABEL_SIZE)


def entity_diagram(database=False):
    """Use the same eight business relationships in the UML and ER views."""
    d = UML(800, 1094)
    left, center, right = COL_LEFT - 4, COL_CENTER, COL_RIGHT
    middle = 350
    photo = 751
    end_left, end_center = left + CARD_W, center + CARD_W

    relationships = (
        ([(center + 57, 220), (center + 57, middle)],
         (("1", 370, 224), ("owns", 374, 273), ("0..*", 380, 326))),
        ([(end_left, 420), (center, 420)],
         (("1", 241, 396), ("0..*", 270, 396), ("groups", 258, 373))),
        ([(center + 57, 594), (center + 57, photo)],
         (("1", 370, 598), ("contains", 380, 664), ("0..*", 380, 725))),
        ([(end_center, 155), (509, 155), (509, 730), (445, 730), (445, photo)],
         (("1", 508, 129), ("uploads", 469, 286), ("0..*", 471, 704))),
        ([(end_center, 105), (530, 105), (530, 328), (592, 328), (592, middle)],
         (("1", 516, 77), ("authors", 565, 238), ("0..*", 619, 325))),
        ([(end_center, 65), (773, 65), (773, 547), (690, 547), (690, 558)],
         (("1", 518, 40), ("likes", 650, 41), ("0..*", 721, 524))),
        ([(end_center, 839), (533, 839), (533, 500), (right, 500)],
         (("1", 514, 846), ("comments", 583, 524), ("0..*", 532, 475))),
        ([(end_center, 920), (652, 920), (652, 706)],
         (("1", 514, 896), ("likes", 577, 896), ("0..*", 682, 711))),
    )
    for route, labels in relationships:
        multiplicity_link(d, route, labels)

    entities = (
        ("User", center, 24), ("Category", left, middle), ("Album", center, middle),
        ("Comment", right, middle), ("PhotoLike", right, 558), ("Photo", center, photo),
    )
    for name, x, y in entities:
        if database:
            table, keys = ER_TABLES[name]
            class_card(d, table, x, y, "table", keys)
        else:
            fields = fields_of(name)
            if name == "PhotoLike":
                fields += ("{unique(user_id, photo_id)}",)
            class_card(d, name, x, y, "entity", fields)
    if database:
        for row, label in enumerate(("PK  Primary key", "FK  Foreign key", "UQ  Unique constraint",
                                     "1  Exactly one", "0..*  Zero or more")):
            d.text(label, left, 610 + row * 24, CARD_W, 22, LABEL_SIZE, align="left")
    else:
        d.text("1  Exactly one", left, 610, CARD_W, 22, LABEL_SIZE, align="left")
        d.text("0..*  Zero or more", left, 634, CARD_W, 22, LABEL_SIZE, align="left")
    return d


# Field constraints are repeated in the data dictionary with their SQL types and defaults.
ER_TABLES = {
    "User": ("users", ("PK id", "UQ username", "email", "password_hash", "role", "created_at")),
    "Category": ("categories", ("PK id", "UQ name")),
    "Album": ("albums", ("PK id", "FK owner_id", "FK category_id",
                         "name", "visibility", "version", "created_at", "updated_at")),
    "Photo": ("photos", ("PK id", "FK album_id", "FK uploader_id",
                         "original_path", "thumbnail_path", "upload_id", "media_type",
                         "size_bytes", "created_at", "UQ (album_id, uploader_id, upload_id)")),
    "Comment": ("comments", ("PK id", "FK photo_id", "FK user_id",
                             "body", "created_at")),
    "PhotoLike": ("photo_likes", ("PK/FK user_id", "PK/FK photo_id",
                                  "created_at", "PK (user_id, photo_id)")),
}


def account_diagram():
    left, center, right = COL_LEFT, COL_CENTER, COL_RIGHT
    d = UML(THREE_COLUMN_WIDTH, 680)
    for route in (
        [(left + 105, 152), (left + 105, 214), (center + 55, 214), (center + 55, 252)],
        [(right + 105, 152), (right + 105, 214), (center + 155, 214), (center + 155, 252)],
        [(center + CARD_W, 312), (right, 312)],
        [(right, 422), (center + CARD_W, 422)],
        [(right + 190, 428), (right + 190, 528)],
    ):
        link(d, route, dashed=True)
    class_card(d, "RegisterUI", left, 24, "boundary", ("- form: RegisterForm",),
               ("+ submit()", "+ open_login()"))
    class_card(d, "LoginUI", right, 24, "boundary", ("- form: LoginForm",),
               ("+ submit()", "+ route_by_role(role)"))
    class_card(d, "AuthRouter", center, 252, "control", (),
               ("+ register(form): AccountView", "+ login(form): AccountView", "+ me(): AccountView"))
    class_card(d, "AccountService", right, 252, "service", (), operations_of("AccountService"))
    class_card(d, "User", center, 417, "entity", fields_of("User"))
    class_card(d, "Session", right, 528, "SQLAlchemy", (),
               ("+ scalar(statement)", "+ add(instance)", "+ commit()"))
    link(d, [(left, 317), (left + 52, 317)], dashed=True)
    d.text("dependency", left + 61, 306, 120, 22, LABEL_SIZE, align="left")
    return d


def album_diagram():
    left, center, right = COL_LEFT, COL_CENTER, COL_RIGHT
    d = UML(THREE_COLUMN_WIDTH, 926)
    for route in (
        [(left + 105, 128), (left + 105, 194)], [(right + 105, 128), (right + 105, 194)],
        [(left + 105, 322), (left + 105, 380)], [(right + 105, 346), (right + 105, 380)],
        [(left + CARD_W, 438), (center, 438)],
        [(left + 105, 628), (left + 105, 664)],
        [(right + 105, 628), (right + 105, 722)],
        [(right + 44, 628), (right + 44, 646), (left + 155, 646), (left + 155, 664)],
    ):
        link(d, route, dashed=True)
    multiplicity_link(d, [(right, 763), (left + CARD_W, 763)],
                      (("1", right - 18, 738), ("0..*", left + CARD_W + 22, 738),
                       ("classifies", center + 105, 738)))

    class_card(d, "AlbumFormUI", left, 24, "boundary", (), ("+ create_album()", "+ update_album()"))
    class_card(d, "CategoryAdminUI", right, 24, "boundary", (),
               ("+ save_category()", "+ delete_category()"))
    class_card(d, "AlbumRouter", left, 194, "control", (),
               ("+ get(album_id, scope)", "+ create(data)", "+ update(album_id, data)"))
    class_card(d, "CategoryRouter", right, 194, "control", (),
               ("+ list()", "+ create(data)", "+ update(category_id, data)", "+ delete(category_id)"))
    class_card(d, "AlbumService", left, 380, "service", (), operations_of("AlbumService"))
    class_card(d, "AlbumAccessPolicy", center, 380, "policy", (), operations_of("AlbumAccessPolicy"))
    class_card(d, "CategoryService", right, 380, "service", (), operations_of("CategoryService"))
    class_card(d, "Album", left, 664, "entity", fields_of("Album"))
    class_card(d, "Category", right, 722, "entity", fields_of("Category"))
    figure_legend(d, center + 4, 35)
    return d


def photo_diagram():
    left, center, right = COL_LEFT, COL_CENTER, COL_RIGHT
    d = UML(THREE_COLUMN_WIDTH, 1160)
    for route in (
        [(left + 105, 176), (left + 105, 220), (center + 55, 220), (center + 55, 256)],
        [(right + 105, 152), (right + 105, 220), (center + 155, 220), (center + 155, 256)],
        [(center + 105, 432), (center + 105, 486)],
        [(center, 540), (left + CARD_W, 540)],
        [(center + CARD_W, 540), (right, 540)],
        [(center + 70, 830), (center + 70, 843), (left + 160, 843), (left + 160, 868)],
    ):
        link(d, route, dashed=True)
    multiplicity_link(d, [(right, 907), (left + CARD_W, 907)],
                      (("1", right - 18, 881), ("0..*", left + CARD_W + 22, 881),
                       ("contains", center + 105, 881)))

    class_card(d, "AlbumPhotosUI", left, 24, "boundary", ("- upload_id: UUID",),
               ("+ select_file()", "+ upload(file)", "+ list_photos()"))
    class_card(d, "PhotoDetailPage", right, 24, "boundary", (),
               ("+ load(photo_id)", "+ load_original()", "+ load_thumbnail()"))
    class_card(d, "PhotoRouter", center, 256, "control", (),
               ("+ upload(album_id, file, upload_id)", "+ list(album_id)",
                "+ detail(photo_id)", "+ image(photo_id, variant)"))
    class_card(d, "PhotoService", center, 486, "service", ("- storage: LocalPhotoStorage",),
               (*operations_of("PhotoService"), "- make_thumbnail(file)"))
    class_card(d, "AlbumAccessPolicy", left, 486, "policy", (), operations_of("AlbumAccessPolicy"))
    class_card(d, "LocalPhotoStorage", right, 486, "storage", (), operations_of("LocalPhotoStorage"))
    class_card(d, "Photo", left, 868, "entity",
               fields_of("Photo"))
    class_card(d, "Album", right, 868, "entity", fields_of("Album", "id", "owner_id", "visibility"))
    figure_legend(d, left, 270)
    return d


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


def dependency(diagram, points, label=None):
    diagram.stroke(points, head="open", dash=6)
    if label:
        diagram.label_mask(*label, size=14)


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


def write_chapter(filename, heading, figures, *, include_sources=False):
    blocks = [f"# {heading}"]
    for group, name, title, caption, *rest in figures:
        relative = f"图稿/{group}/{name}"
        note = rest[0] if rest else caption
        blocks.extend((f"## {title}", f"![{title}]({relative}.png)", *note.split("\\n\\n")))
        if include_sources:
            blocks.append(f"[Draw.io 源图]({relative}.drawio) · [SVG]({relative}.svg)")
    (DESIGN / filename).write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


INTERACTION_NOTE = """照片详情页通过 `InteractionRouter` 调用 `CommentService` 或 `LikeService`。两个服务都使用 `Photo.album_id` 调用 `AlbumAccessPolicy.require_visible`。照片不存在或所属相册不可见时返回 `404 PHOTO_UNAVAILABLE`。图中虚线表示调用依赖，实线表示业务关联。

**评论对应图 14。** `CommentService.create` 校验去除首尾空白后的正文为 1–200 字符，用当前用户标识写入 `Comment.user_id`，并用 `Comment.photo_id` 记录被评论的照片。页面根据返回的 `CommentView` 更新列表。删除前校验照片可见性，再按照片和评论标识查找记录。目标评论不在该照片下时返回 `404 COMMENT_NOT_FOUND`。`ensure_author` 比较 `comment.user_id` 与 `actor.id`，尝试删除别人的评论时返回 `403 COMMENT_NOT_OWNED`。

**点赞对应图 15。** `LikeService.set_liked` 将 `PhotoLike` 更新到请求指定的状态。每条记录为一名用户对一张照片的点赞，`(user_id, photo_id)` 为联合主键，与图 02 和数据库 ER 图一致。

| 操作 | 事务内写入 | 返回 |
| --- | --- | --- |
| 首次点赞 | 按联合键插入当前用户和照片的记录 | `liked = true`，本次操作新增一条计数 |
| 重复点赞 | 保留原记录和创建时间 | `liked = true`，本次操作未新增计数 |
| 取消点赞 | 按联合键删除本人记录，已不存在时保持现状 | `liked = false`，本次操作至多移除一条计数 |

服务用同一次查询统计该照片的记录数，并判断当前用户的联合键是否存在。两个结果组成 `LikeState`，事务提交成功后返回给页面。读取照片详情时按同一口径取得 `liked` 和 `like_count`。[评论和点赞顺序图](06_顺序图.md) · [数据库关系与约束](07_数据库设计.md#约束与服务校验)"""

ENTITY_NOTE = """每条关联的父端都是 `1`，记录端都是 `0..*`。一个用户可以拥有相册、上传照片、发表或点赞多次，分别由 `Album.owner_id`、`Photo.uploader_id`、`Comment.user_id` 和 `PhotoLike.user_id` 记录。相册所有者、上传者和评论作者是不同的业务角色，上传时服务另行校验相册归属。

每个相册必属一个类别，每张照片必属一个相册，每条评论和点赞必属一张照片。类别可暂未使用，相册可为空，照片可没有评论或点赞。`PhotoLike` 对 `(user_id, photo_id)` 的唯一性与数据库联合主键一致。[数据库设计与八条关系对照](07_数据库设计.md#关系与多重性)"""

ACCOUNT_NOTE = """注册页 `RegisterUI` 和登录页 `LoginUI` 通过 `AuthRouter` 提交表单。`AccountService.register` 校验输入、生成带盐密码哈希，并用 SQLAlchemy `Session` 保存角色为 `member` 的 `User`。注册成功后由页面引导登录。

登录对应图 08。`AuthRouter.login` 调用 `authenticate(data)`，账户服务按用户名查找记录并校验一次密码哈希。通过后用返回的 `User` 调用 `issue_token(user)`，路由设置会话 Cookie，页面按角色进入个人主页或类别管理后台。刷新页面时可调用 `AuthRouter.me`，由 `resolve_user(token)` 解析当前账户。[注册和登录顺序图](06_顺序图.md)"""

ALBUM_NOTE = """相册表单通过 `AlbumRouter` 查询、创建和修改相册，类别列表和后台维护请求由 `CategoryRouter` 分派给 `CategoryService`。相册服务保存名称、可见性、类别及版本，创建时以当前用户为所有者。

**只能修改本人相册。** 打开编辑页时用 `scope=mine` 查询相册，提交时 `AlbumService.update` 再调用 `AlbumAccessPolicy.require_owned`。更新条件同时匹配相册标识、所有者和提交的版本号，成功后版本加一。仍归本人但版本已变更时返回 `409 ALBUM_VERSION_CONFLICT`。

**使用中的类别禁止删除。** `CategoryService.delete` 先验证管理员角色并检查相册引用。即使另一事务在检查后创建了引用，`albums.category_id` 的外键也会阻止删除，服务返回 `409 CATEGORY_IN_USE`。[数据库约束](07_数据库设计.md#约束与服务校验)"""

PHOTO_NOTE = """相册照片页负责选择文件、生成 `upload_id`、上传和浏览列表。照片详情页通过 `PhotoRouter` 读取详情、原图和缩略图。`Photo` 用 `album_id` 关联所属相册，用 `uploader_id` 记录当前上传者，并保留上传标识及两条存储路径。

**上传对应图 12。** 打开入口时按 `scope=mine` 读取相册。提交时 `PhotoService.upload` 调用 `require_owned(actor, album_id)` 再次核对归属，校验文件后按上传联合键预留记录，生成缩略图并使用 `LocalPhotoStorage.save` 保存两份文件。成功落盘后提交，使用相同上传标识重试可返回已有记录。

**浏览对应图 13。** `list_photos` 检查请求指定的相册。`get_detail` 和 `open_image` 先查照片的 `album_id`，再调用 `require_visible(actor, album_id)`。登录用户可浏览公开相册或本人私有相册。`open_image` 按请求的图片类型选择 `original_path` 或 `thumbnail_path`，并调用 `LocalPhotoStorage.open`。[上传和浏览顺序图](06_顺序图.md)"""


def write_class_figures():
    classes = []
    for number, (name, caption, build, note) in enumerate((
        ("全局领域实体类图", "每张照片属于一个相册，相册可以为空。评论与点赞都关联用户和照片，同一用户对同一张照片最多有一条点赞记录。", entity_diagram, ENTITY_NOTE),
        ("账户管理设计类图", "账户服务负责注册、凭据验证和会话处理。", account_diagram, ACCOUNT_NOTE),
        ("相册管理设计类图", "相册服务处理创建和修改，访问策略校验可见性或归属。类别服务删除前查询相册引用，数据库外键在并发写入时仍会阻止删除已被引用的类别。", album_diagram, ALBUM_NOTE),
        ("照片管理设计类图", "照片服务通过访问策略检查相册权限。上传时由照片服务生成缩略图，由其持有的本地存储对象保存原图和缩略图。", photo_diagram, PHOTO_NOTE),
        ("评论与点赞设计类图", "评论和点赞共用相册可见性检查与同一个控制入口，评论按作者和照片关联，点赞以联合主键记录本人状态。", interaction_diagram, INTERACTION_NOTE),
    ), 2):
        figure = build().save_figure("类图", f"{number:02}_{name}", f"图 {number:02} {name}", caption,
                                       postprocess=True)
        classes.append(tuple(figure) + ((note,) if note else ()))
    write_chapter("04_设计类图.md", "设计类图", classes, include_sources=True)


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
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--sequences-only", action="store_true")
    selection.add_argument("--classes-only", action="store_true")
    args = parser.parse_args()
    if not args.sequences_only:
        write_class_figures()
        entity_diagram(database=True).save_figure(
            "数据库", "16_PostgreSQL数据库ER图", "图 16 PostgreSQL 数据库 ER 图",
            "六张表的主外键、唯一约束和关系多重性。", postprocess=True)
    if not args.classes_only:
        if not args.sequences_only:
            write_package_figure()
        write_sequence_figures()
