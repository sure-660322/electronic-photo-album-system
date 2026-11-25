"""Textbook UML figures, drawn entirely in Python. Run from the project root.

python tools/textbook_models.py
PNG, SVG and editable draw.io sources share the same geometry and data.
"""
from pathlib import Path
import json
import math
import re
import html
import os
from PIL import Image, ImageDraw, ImageFont
import figstyle as fs
from postprocess_png import process

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/textbook-models'
MAIN, LIGHT, INK, EDGE = fs.MAIN, fs.MAIN_LIGHT, fs.INK, fs.EDGE
FONT_DIR=Path(os.environ.get('WINDIR',Path.home().anchor))/'Fonts'


class Canvas:
    def __init__(self, width, height):
        self.w, self.h = width, height
        self.im = Image.new('RGB', (width*3, height*3), 'white')
        self.d = ImageDraw.Draw(self.im)
        self.cells, self.svg, self.rects, self.texts, self.edges = [], [], [], [], []
        self.n = 0

    def key(self):
        self.n += 1
        return f'n{self.n}'

    def text(self, value, x, y, w, h=24, size=15, bold=False, align='center', underline=False):
        key = self.key()
        font = ImageFont.truetype(str(FONT_DIR/('msyhbd.ttc' if bold else 'msyh.ttc')), size*3)
        lines = value.split('\n')
        line_h = size*1.4
        assert len(lines)*line_h <= h+2, (value, h)
        for i, line in enumerate(lines):
            tw = self.d.textlength(line, font=font)/3
            assert tw <= w-3, (line, round(tw), w)
            xx = x+(w-tw)/2 if align == 'center' else x+5
            yy = y+(h-len(lines)*line_h)/2+i*line_h
            self.d.text((xx*3, yy*3), line, font=font, fill=INK, anchor='lt')
            if underline:
                self.d.line((xx*3, (yy+size+3)*3, (xx+tw)*3, (yy+size+3)*3), fill=INK, width=2)
            self.svg.append(f'<text x="{xx}" y="{yy+size}" font-size="{size}" font-weight="{600 if bold else 400}" text-decoration="{"underline" if underline else "none"}">{html.escape(line)}</text>')
        style = fs.TEXT + f'fontSize={size};align={align};fontStyle={(1 if bold else 0)+(4 if underline else 0)};'
        self.cells.append(fs.label(key, value, x,y,w,h,style=style))
        self.texts.append(dict(value=value, rect=[x,y,w,h]))

    def shape(self, kind, x, y, w, h, fill='white', stroke=MAIN, value='', size=15, bold=False):
        key = self.key()
        box = [x*3,y*3,(x+w)*3,(y+h)*3]
        if kind == 'circle':
            self.d.ellipse(box, fill=fill, outline=stroke, width=4)
            sv = f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}"'
            style = 'ellipse;'
        elif kind == 'diamond':
            pts=[(x+w/2,y),(x+w,y+h/2),(x+w/2,y+h),(x,y+h/2)]
            self.d.polygon([(a*3,b*3) for a,b in pts], fill=fill, outline=stroke, width=4)
            sv = '<polygon points="'+' '.join(f'{a},{b}' for a,b in pts)+'"'
            style='rhombus;'
        elif kind == 'pill':
            self.d.rounded_rectangle(box, radius=h*1.5, fill=fill, outline=stroke, width=4)
            sv=f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2}"'
            style='rounded=1;arcSize=50;'
        else:
            self.d.rectangle(box, fill=fill, outline=stroke, width=4)
            sv=f'<rect x="{x}" y="{y}" width="{w}" height="{h}"'
            style='rounded=0;'
        self.svg.append(sv+f' fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        self.cells.append(fs.vertex(key,'',style+f'fillColor={fill};strokeColor={stroke};strokeWidth=1.5;',x,y,w,h))
        self.rects.append(dict(id=key,kind=kind,rect=[x,y,w,h]))
        if value:
            self.text(value,x+4,y+2,w-8,h-4,size,bold)
        return (x+w/2,y),(x+w/2,y+h)

    def line(self, pts, arrow=True, diamond=False, dashed=False, color=EDGE):
        key=self.key()
        prior=self.edges[:]
        self.edges.append(dict(points=pts,arrow=arrow))
        self.d.line([(x*3,y*3) for x,y in pts], fill=color, width=4)
        self.svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="1.5"/>')
        if arrow:
            a,b=pts[-2],pts[-1]
            ang=math.atan2(b[1]-a[1],b[0]-a[0])
            q=[(b[0]-9*math.cos(ang)+4*math.sin(ang),b[1]-9*math.sin(ang)-4*math.cos(ang)), b,
               (b[0]-9*math.cos(ang)-4*math.sin(ang),b[1]-9*math.sin(ang)+4*math.cos(ang))]
            self.d.line([(x*3,y*3) for x,y in q],fill=color,width=4)
            self.svg.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in q)+f'" fill="none" stroke="{color}" stroke-width="1.5"/>')
        self.cells.append(fs.poly(key,pts,(fs.SEG_OPEN if arrow else fs.SEG_NONE)+'jumpStyle=arc;jumpSize=5;'+('dashed=1;' if dashed else '')))
        # Bridge every proper crossing; junctions at endpoints remain connected.
        for a,b in zip(pts,pts[1:]):
            for old in prior:
                if old.get('icon'):continue
                for p,q in zip(old['points'],old['points'][1:]):
                    if a[0]==b[0] and p[1]==q[1]:
                        cx,cy=a[0],p[1]; vertical=True
                        hit=min(a[1],b[1])+6<cy<max(a[1],b[1])-6 and min(p[0],q[0])+6<cx<max(p[0],q[0])-6
                    elif a[1]==b[1] and p[0]==q[0]:
                        cx,cy=p[0],a[1];vertical=False
                        hit=min(a[0],b[0])+6<cx<max(a[0],b[0])-6 and min(p[1],q[1])+6<cy<max(p[1],q[1])-6
                    else:continue
                    if not hit:continue
                    r=5
                    self.d.ellipse(((cx-r-1)*3,(cy-r-1)*3,(cx+r+1)*3,(cy+r+1)*3),fill='white')
                    keep=[(cx-r-2,cy),(cx+r+2,cy)] if vertical else [(cx,cy-r-2),(cx,cy+r+2)]
                    self.d.line([(x*3,y*3) for x,y in keep],fill=EDGE,width=4)
                    self.d.arc(((cx-r)*3,(cy-r)*3,(cx+r)*3,(cy+r)*3),270 if vertical else 180,450 if vertical else 360,fill=color,width=4)
                    path=f'M {cx},{cy-r} Q {cx+2*r},{cy} {cx},{cy+r}' if vertical else f'M {cx-r},{cy} Q {cx},{cy-2*r} {cx+r},{cy}'
                    self.svg.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="white"/><path d="M {keep[0][0]},{keep[0][1]} L {keep[1][0]},{keep[1][1]}" stroke="{EDGE}" stroke-width="1.5"/><path d="{path}" fill="none" stroke="{color}" stroke-width="1.5"/>')
        if diamond:
            a,b=pts[0],pts[1]
            dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy);dx/=length;dy/=length
            q=[a,(a[0]+8*dx+5*dy,a[1]+8*dy-5*dx),(a[0]+16*dx,a[1]+16*dy),(a[0]+8*dx-5*dy,a[1]+8*dy+5*dx)]
            self.d.polygon([(x*3,y*3) for x,y in q],fill='white',outline=color,width=4)
            self.svg.append('<polygon points="'+' '.join(f'{x},{y}' for x,y in q)+f'" fill="white" stroke="{color}" stroke-width="1.5"/>')
            self.cells[-1]=fs.poly(key,pts,fs.SEG_NONE+'startArrow=diamond;startFill=0;')

    def actor(self,cx,cy,name,instance=False):
        self.shape('circle',cx-8,cy-32,16,16,stroke=INK)
        for pts in [[(cx,cy-16),(cx,cy+12)],[(cx-17,cy-5),(cx+17,cy-5)],[(cx,cy+12),(cx-16,cy+32)],[(cx,cy+12),(cx+16,cy+32)]]:
            self.line(pts,False,color=INK)
            self.edges[-1]['icon']=True
        self.text((': ' if instance else '')+name,cx-65,cy+39,130,24,14,underline=instance)

    def object_icon(self,cx,cy,kind):
        self.shape('circle',cx-22,cy-22,44,44, LIGHT if kind != 'entity' else 'white')
        if kind=='boundary':
            self.line([(cx-34,cy-18),(cx-34,cy+18)],False,color=MAIN)
            self.line([(cx-34,cy),(cx-22,cy)],False,color=MAIN)
        elif kind=='control':
            # The curved arrow sits outside the object, clear of both its rim
            # and the vertical object link entering at the top centre.
            angles=[math.radians(20-95*i/16) for i in range(17)]
            self.line([(cx+32*math.cos(t),cy+32*math.sin(t)) for t in angles],True,color=MAIN)
            self.edges[-1].update(icon=True,role='control-arrow')
        else:
            self.line([(cx-27,cy+25),(cx+27,cy+25)],False,color=MAIN)

    def obj(self,cx,cy,name,kind,instance=False):
        self.object_icon(cx,cy,kind)
        self.text((': ' if instance else '')+name,cx-105,cy+34,210,26,14,underline=instance)

    def save(self,path):
        path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
        self.im.resize((self.w*2,self.h*2),Image.Resampling.LANCZOS).save(path.with_suffix('.png'))
        fs.save(path.with_suffix('.drawio'),self.cells,self.w,self.h)
        path.with_suffix('.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="diagram-title"><title id="diagram-title">{html.escape(path.stem)}</title><desc>Textbook UML analysis model</desc><rect width="100%" height="100%" fill="white"/><g font-family="Microsoft YaHei, sans-serif" fill="{INK}">'+''.join(self.svg)+'</g></svg>',encoding='utf-8')
        process(path.with_suffix('.png'),font_size=getattr(self,'font_size',14))
        return dict(path=path.relative_to(ROOT).as_posix(),size=[self.w,self.h],labels=self.texts,nodes=self.rects,edges=self.edges)


# Entity attributes are shared by every use case. Operations are selected per view.
ATTRS={
 'User':['- userId: Integer','- username: String','- passwordHash: String','- email: String','- role: UserRole'],
 'Album':['- albumId: Integer','- name: String','- visibility: Visibility','- ownerId: Integer','- categoryId: Integer'],
 'Category':['- categoryId: Integer','- name: String'],
 'Photo':['- photoId: Integer','- filePath: String','- thumbnailPath: String','- albumId: Integer','- uploaderId: Integer','- uploadedAt: DateTime'],
 'Comment':['- commentId: Integer','- content: String','- authorId: Integer','- photoId: Integer','- createdAt: DateTime'],
 'PhotoLike':['- userId: Integer','- photoId: Integer','- createdAt: DateTime'],
}


def case(module,actor,page,ctl,ops,entities,actor_messages,requests,entity_messages,relations,activity,collaboration):
    return dict(module=module,actor=actor,page=page,ctl=ctl,ops=ops,entities=entities,actor_messages=actor_messages,requests=requests,entity_messages=entity_messages,relations=relations,activity=activity,collaboration=collaboration)


CASES={
 '用户注册':case('1-账户管理-钟标','Visitor','RegisterUI','RegisterHandler',
 ['register(form)'], [('User',['isNameAvailable(name)','create(form)'])],
 ['1: submit(form)'],['1.1: register(form)'],
 [['1.1.1: isNameAvailable(name)','1.1.2: [available] create(form)']],[],
 '从初始节点进入注册页面，填写后形成注册信息对象；系统校验必填项、两次密码及用户名可用性。失败分支提示后回到填写，成功分支创建普通账户并跳转登录页，以活动终止节点结束。',
 'Visitor 向 RegisterUI 提交表单，RegisterHandler 执行 register(form)，依次调用 User 的 isNameAvailable(name) 与 create(form)。校验通过后创建普通账户，界面显示结果并跳转登录页。'),
 '用户登录':case('1-账户管理-钟标','LoginUser','LoginUI','LoginHandler',
 ['login(credentials)'],[('User',['authenticate(credentials)','getRole()'])],
 ['1: submit(credentials)'],['1.1: login(credentials)'],
 [['1.1.1: authenticate(credentials)','1.1.2: [valid] getRole()']],[],
 '登录凭据对象流入账户验证动作；验证失败提示并回到输入，验证成功按账户角色分为个人主页和管理后台两个互斥分支，合并后结束。',
 'LoginUser 包含普通用户和管理员。LoginUI 委派 LoginHandler 登录，User 完成 authenticate(credentials) 并在成功后返回 getRole()，界面据角色进入对应页面。'),
 '创建相册':case('2-相册管理-刘硕','Member','CreateAlbumUI','AlbumHandler',
 ['loadCategories()','createAlbum(form)'], [('Category',['listAll()']),('Album',['create(form, ownerId)'])],
 ['1: openForm()','2: submit(form)'],['1.1: loadCategories()','2.1: createAlbum(form)'],
 [['1.1.1: listAll()'],['2.1.1: [valid] create(form, ownerId)']], [('Category','Album','1','0..*','albums',True)],
 '读取类别并显示创建表单，用户提交名称、类别与可见性，形成相册信息对象；校验失败提示后回到填写，校验通过创建相册并关联当前用户，再显示更新后的相册列表。',
 'Member 打开 CreateAlbumUI，AlbumHandler 先调用 Category.listAll() 准备表单，再接收提交。createAlbum(form) 校验成功后调用 Album.create(form, ownerId)，将相册归属当前用户。'),
 '修改相册':case('2-相册管理-刘硕','Member','EditAlbumUI','AlbumHandler',
 ['loadAlbum(albumId)','updateAlbum(form)'],[('Album',['findOwned(albumId, userId)','update(form)']),('Category',['listAll()'])],
 ['1: openForm(albumId)','2: submit(form)'],['1.1: loadAlbum(albumId)','2.1: updateAlbum(form)'],
 [['1.1.1: findOwned(albumId, userId)','2.1.1: [valid] update(form)'],['1.1.2: [owned] listAll()']], [('Category','Album','1','0..*','albums',True)],
 '先读取本人相册，未找到时提示并返回相册列表，结束本次修改；读取成功后加载类别并填写修改信息。相册信息对象进入校验，失败回到填写，成功更新原相册并显示列表。',
 'EditAlbumUI 请求 AlbumHandler 读取相册；Album.findOwned(albumId, userId) 确认归属后，Category.listAll() 提供可选类别。提交时调用 updateAlbum(form)，通过校验后更新原相册。'),
 '上传图片':case('3-照片管理-王柯涵','Member','UploadUI','UploadHandler',
 ['upload(file, albumId)','saveFile(file)','makeThumbnail(path)'],[('Album',['findOwned(albumId, userId)']),('Photo',['create(metadata)'])],
 ['1: submit(file, albumId)'],['1.1: upload(file, albumId)'],
 [['1.1.1: findOwned(albumId, userId)'],['1.1.2: [valid] create(metadata)']], [('Album','Photo','1','0..*','photos',True)],
 '选择本人相册并提交图片文件对象，系统校验归属、格式和大小。失败提示并返回选择，成功依次保存原图、生成缩略图、记录照片元数据，最后显示上传结果。',
 'UploadUI 委派 UploadHandler 上传，先通过 Album.findOwned(albumId, userId) 确认目标相册，再校验文件、保存原图并生成缩略图，最后调用 Photo.create(metadata) 记录路径、归属与时间。'),
 '浏览照片':case('3-照片管理-王柯涵','Member','BrowseUI','BrowseHandler',
 ['listAlbums(userId)','openAlbum(albumId)','openPhoto(photoId)'],[('Album',['listVisible(userId)','canView(userId)','listPhotos()']),('Photo',['getDetails(userId)'])],
 ['1: browse()','2: selectAlbum(albumId)','3: selectPhoto(photoId)'],['1.1: listAlbums(userId)','2.1: openAlbum(albumId)','3.1: openPhoto(photoId)'],
 [['1.1.1: listVisible(userId)','2.1.1: canView(userId)','2.1.2: [visible] listPhotos()'],['3.1.1: getDetails(userId)']], [('Album','Photo','1','0..*','photos',True)],
 '按入口分为列表浏览和链接直达。列表为空时显示空状态并结束；选择相册与直达链接合并到同一个可见性判断。允许访问时读取照片对象并显示详情、评论与点赞状态，拒绝访问时提示后返回浏览入口。',
 'BrowseUI 依次请求可见相册、相册照片和照片详情。Album 提供 listVisible(userId)、canView(userId) 与 listPhotos()；Photo.getDetails(userId) 每次检查所属相册的当前可见性，通过后返回大图信息、评论、点赞数与本人点赞状态；原图与缩略图的读取采用相同规则。直达链接从 openAlbum 开始。'),
 '相册类别管理':case('4-类别与评论-陈诺','Administrator','CategoryUI','CategoryHandler',
 ['loadCategories()','maintain(operation)'],[('Category',['listAll()','isNameAvailable(name, id)','createOrUpdate(form)','delete(categoryId)']),('Album',['countByCategory(id)'])],
 ['1: openList()','2: submit(operation)'],['1.1: loadCategories()','2.1: maintain(operation)'],
 [['1.1.1: listAll()','2.1.1: [edit] isNameAvailable(name, id)','2.1.2: [valid] createOrUpdate(form)','2.1.4: [unused] delete(categoryId)'],['2.1.3: [delete] countByCategory(id)']], [('Category','Album','1','0..*','albums',True)],
 '新增或修改在左侧校验名称并保存，删除在右侧检查相册占用后执行。名称无效、类别被占用时分别沿左、右外侧返回操作选择；成功分支在下方合并，提示成功并刷新类别列表。',
 'CategoryUI 请求现有类别并提交操作。CategoryHandler 对新增或修改调用 Category 的查重及保存，对删除调用 Album.countByCategory(id)，计数为零时调用 Category.delete(categoryId)，完成后刷新类别列表。'),
 '对照片评论':case('4-类别与评论-陈诺','Member','PhotoDetailUI','CommentHandler',
 ['postComment(content)','deleteComment(commentId)'],[('Comment',['create(userId, photoId, text)','isAuthor(userId)','delete(commentId)']),('Photo',['canView(userId)','listComments()']),('User',['getId()'])],
 ['1: post(content)','2: [confirmed] remove(id)'],['1.1: postComment(content)','2.1: deleteComment(commentId)'],
 [['1.1.2: [valid] create(userId, photoId, text)','2.1.1: isAuthor(userId)','2.1.2: [author] delete(commentId)'],['1.1.1: canView(userId)','1.1.3: listComments()','2.1.3: [deleted] listComments()'],[]],
 [('User','Comment','1','0..*','comments',False),('Photo','Comment','1','0..*','comments',False)],
 '评论内容对象进入校验，内容有效且照片可见时保存并显示评论列表；错误分支回到输入。删除自己的评论时进入确认分支，确认后删除并刷新，取消则保留评论；浏览结束进入终止节点。',
 'PhotoDetailUI 委派 CommentHandler 发表评论或删除本人评论。发布先调用 Photo.canView(userId)，保存 Comment 后读取列表；删除先调用 Comment.isAuthor(userId)，确认归属后删除并刷新列表。User 与 Comment 的关联表达作者身份。'),
 '对照片点赞':case('5-点赞功能','Member','PhotoDetailUI','LikeHandler',
 ['loadLikeState(photoId)','likePhoto(photoId)','unlikePhoto(photoId)'],[('PhotoLike',['find(userId, photoId)','create(userId, photoId)','delete(userId, photoId)']),('Photo',['canView(userId)','countLikes()']),('User',['getId()'])],
 ['1: openPhoto(photoId)','2: like(photoId)','3: unlike(photoId)'],['1.1: loadLikeState(photoId)','2.1: likePhoto(photoId)','3.1: unlikePhoto(photoId)'],
 [['1.1.2: [visible] find(userId, photoId)','2.1.2: [visible] find(userId, photoId)','2.1.3: [visible and absent] create(userId, photoId)','3.1.2: [visible] find(userId, photoId)','3.1.3: [visible and present] delete(userId, photoId)'],['1.1.1: canView(userId)','1.1.3: [visible] countLikes()','2.1.1: canView(userId)','2.1.4: [visible] countLikes()','3.1.1: canView(userId)','3.1.4: [visible] countLikes()'],[]],
 [('User','PhotoLike','1','0..*','likes',False),('Photo','PhotoLike','1','0..*','likes',False)],
 '打开照片后读取当前用户点赞状态和点赞数。点击按钮产生点赞请求对象，系统确认照片可见，再按操作分为新增点赞和取消点赞；两条互斥分支合并后重新读取并显示状态与数量。同一用户与照片组合仅保留一条点赞记录，重复相同操作保持当前状态。',
 'PhotoDetailUI 通过 LikeHandler 读取状态、点赞或取消点赞。Photo.canView(userId) 在读取状态、点赞和取消点赞前检查访问权限，不可见时结束操作；可见时由 PhotoLike.find(userId, photoId) 获取个人状态；新增用 create，取消用 delete，操作后由 Photo.countLikes() 返回总数。PhotoLike 以 userId 与 photoId 联合唯一，重复请求保持相同结果。'),
}


COLLABORATION_NOTES={
 '浏览照片':['getDetails rechecks current album visibility.'],
 '对照片点赞':['Not visible: stop the current operation.'],
}


class Flow:
    def __init__(self,h=940):
        self.c=Canvas(720,h);self.last=None;self.nodes={};self.y=24
    def node(self,key,label='',kind='pill',x=240,y=None,w=220,h=48,system=True):
        y=self.y if y is None else y
        self.c.shape(kind,x,y,w,h,LIGHT if system and kind=='pill' else 'white',value=label)
        self.nodes[key]=(x,y,w,h)
        self.y=y+h+32
        return key
    def add(self,key,label='',**kw):
        old=self.last;self.node(key,label,**kw)
        if old:self.edge(old,key)
        self.last=key;return key
    def edge(self,a,b,label='',side=False,route=None):
        x,y,w,h=self.nodes[a];X,Y,W,H=self.nodes[b]
        if route:
            pts=route
        elif side:
            pts=([(x+w,y+h/2),(X,Y+H/2)] if abs(y+h/2-Y-H/2)<2 else
                 [(x+w,y+h/2),(X+W/2,y+h/2),(X+W/2,Y)])
        else:
            pts=([(x+w/2,y+h),(X+W/2,Y)] if abs(x+w/2-X-W/2)<2 else
                 [(x+w/2,y+h),(x+w/2,(y+h+Y)/2),(X+W/2,(y+h+Y)/2),(X+W/2,Y)])
        self.c.line(pts)
        if label:
            if side:self.c.text(label,min(x+w+4,X+W/2-32),y+h/2-27,64,24,13)
            else:self.c.text(label,x+w/2+10,y+h+2,100,24,13,align='left')
    def start(self):
        self.node('start',kind='circle',x=340,w=20,h=20,system=False)
        x,y,w,h=self.nodes['start'];self.c.shape('circle',x,y,w,h,MAIN)
        self.last='start'
    def end(self,y=None):
        self.add('end',kind='circle',x=335,y=y,w=30,h=30,system=False)
        x,yy,_,_=self.nodes['end'];self.c.shape('circle',x+6,yy+6,18,18,MAIN)
    def decision(self,key):
        return self.add(key,kind='diamond',x=322,w=56,h=40,system=False)
    def error(self,key,decision,text,target,label='[无效]'):
        x,y,w,h=self.nodes[decision]
        self.node(key,text,x=520,y=y-4,w=170,h=48)
        self.edge(decision,key,label,True)
        X,Y,W,H=self.nodes[target]
        self.c.line([(605,y+44),(605,y+64),(704,y+64),(704,Y-16),(X+W-25,Y-16),(X+W-25,Y)])
    def obj(self,key,label):
        # Object flow is part of the main path, matching the textbook example.
        old=self.last
        self.node(key,label,kind='rect',x=28,w=174,h=44,system=False)
        x,y,w,h=self.nodes[old];X,Y,W,H=self.nodes[key]
        self.edge(old,key,route=[(x,y+h/2),(115,y+h/2),(115,Y)])
        self.last=key
    def after_obj(self,key,label,**kw):
        old=self.last;self.node(key,label,**kw)
        x,y,w,h=self.nodes[old];X,Y,W,H=self.nodes[key]
        self.edge(old,key,route=[(x+w,y+h/2),(350,y+h/2),(350,Y)])
        self.last=key


def category_activity():
    """Two operation columns, outside error returns, and no crossed links."""
    c=Canvas(900,930);c.font_size=18
    def action(text,x,y,w=240,h=56,system=True):
        c.shape('pill',x,y,w,h,LIGHT if system else 'white',value=text,size=18)
    def guard(text,x,y,w=120):
        c.text(text,x,y,w,28,18)
    c.shape('circle',440,24,20,20,MAIN)
    action('系统显示现有类别列表',300,80,300)
    c.shape('diamond',434,164,32,24)
    action('管理员选择并提交操作',300,216,300,system=False)
    c.shape('diamond',422,300,56,40)
    action('系统校验类别名称\n非空且不重名',160,380,h=64)
    action('系统统计类别下\n的相册数量',500,380,h=64)
    c.shape('diamond',252,490,56,40)
    c.shape('diamond',592,490,56,40)
    action('提示名称错误',20,482,160)
    action('提示类别被占用',720,482,160)
    action('系统保存类别',160,610)
    action('系统删除类别',500,610)
    c.shape('diamond',434,714,32,24)
    action('系统提示成功并刷新类别列表',280,780,340)
    c.shape('circle',435,872,30,30)
    c.shape('circle',441,878,18,18,MAIN)
    for points in [
        [(450,44),(450,80)], [(450,136),(450,164)],
        [(450,188),(450,216)], [(450,272),(450,300)],
        [(422,320),(280,320),(280,380)],
        [(478,320),(620,320),(620,380)],
        [(280,444),(280,490)], [(620,444),(620,490)],
        [(252,510),(180,510)], [(648,510),(720,510)],
        [(20,510),(10,510),(10,176),(434,176)],
        [(880,510),(890,510),(890,176),(466,176)],
        [(280,530),(280,610)], [(620,530),(620,610)],
        [(280,666),(280,726),(434,726)],
        [(620,666),(620,726),(466,726)],
        [(450,738),(450,780)], [(450,836),(450,872)],
    ]:c.line(points)
    guard('[新增或修改]',180,276,200)
    guard('[删除]',570,276,100)
    guard('[无效]',182,462,72)
    guard('[有相册]',646,462,78)
    guard('[有效]',292,551,100)
    guard('[无相册]',630,551,140)
    return c


def activity(name):
    if name=='相册类别管理':return category_activity()
    f=Flow(1120 if name in ('对照片评论','浏览照片') else 1040)
    f.start()
    if name=='用户注册':
        f.add('open','访客打开注册页面',system=False)
        f.add('input','访客填写并提交注册信息',system=False)
        f.obj('form','注册信息')
        f.after_obj('check','系统校验必填项、密码\n及用户名可用性')
        f.decision('valid');f.error('error','valid','系统提示修改输入','input')
        f.add('create','系统创建普通用户账户')
        f.add('show','系统提示成功并跳转登录页');f.end()
    elif name=='用户登录':
        f.add('input','登录者输入用户名与密码',system=False)
        f.obj('credentials','登录凭据')
        f.after_obj('check','系统校验输入并验证账户')
        f.decision('valid');f.error('error','valid','系统提示补全或重试','input')
        f.add('role','系统读取账户角色')
        f.decision('roles')
        y=f.y
        f.node('member','系统显示个人主页',x=65,y=y,w=220)
        f.node('admin','系统显示管理后台',x=435,y=y,w=220)
        x0,y0,_,_=f.nodes['roles']
        f.edge('roles','member',route=[(322,y0+20),(175,y0+20),(175,y)])
        f.c.text('[普通用户]',180,y0-12,130,24,13)
        f.edge('roles','admin','[管理员]',True)
        f.node('merge',kind='diamond',x=334,y=y+82,w=32,h=24)
        f.edge('member','merge',route=[(175,y+48),(175,y+94),(334,y+94)])
        f.edge('admin','merge',route=[(545,y+48),(545,y+94),(366,y+94)])
        f.last='merge';f.end()
    elif name in ('创建相册','修改相册'):
        if name=='修改相册':
            f.add('read','系统读取当前用户的目标相册')
            f.decision('owned')
            y=f.nodes['owned'][1]
            f.node('absent','系统提示并返回列表',x=490,y=y-4,w=210)
            f.edge('owned','absent','[未找到]',True)
            f.node('stopped',kind='circle',x=580,y=y+80,w=30,h=30)
            f.edge('absent','stopped');f.c.shape('circle',586,y+86,18,18,MAIN)
            f.y=y+84;f.last='owned'
        f.add('form','系统读取类别并显示表单')
        f.add('input','用户填写并提交相册信息',system=False)
        f.obj('data','相册信息')
        f.after_obj('check','系统校验名称、类别\n与公开或私有设置')
        f.decision('valid');f.error('error','valid','系统提示修改输入','input')
        f.add('save','系统创建相册并关联用户' if name=='创建相册' else '系统更新原相册')
        f.add('show','系统提示成功并显示相册列表');f.end()
    elif name=='上传图片':
        f.add('input','用户选择本人相册并提交图片',system=False)
        f.obj('file','图片文件')
        f.after_obj('check','系统校验归属、格式与大小')
        f.decision('valid');f.error('error','valid','系统提示重新选择','input')
        f.add('save','系统保存原图')
        f.add('thumb','系统生成缩略图')
        f.add('meta','系统记录路径、相册与上传者')
        f.add('show','系统提示成功并显示照片');f.end()
    elif name=='浏览照片':
        f.add('enter','用户进入浏览入口',system=False)
        f.decision('entry')
        # Keep the normal flow on one centre line. Only the direct-link
        # bypass and the return loop need to go around intervening actions.
        f.node('list','系统读取可见相册列表',y=236)
        f.edge('entry','list','[列表浏览]')
        f.node('direct','用户打开相册直达链接',x=490,y=152,w=220,system=False)
        f.edge('entry','direct','[链接直达]',True)
        f.node('empty',kind='diamond',x=322,y=316,w=56,h=40)
        f.edge('list','empty')
        f.node('none','系统显示暂无相册',x=24,y=312,w=220)
        f.edge('empty','none',route=[(322,336),(244,336)])
        f.c.text('[空]',250,306,60,24,13)
        f.node('stop',kind='circle',x=119,y=400,w=30,h=30)
        f.edge('none','stop');f.c.shape('circle',125,406,18,18,MAIN)
        f.node('select','用户选择相册',y=396,system=False)
        f.edge('empty','select','[非空]')
        f.node('merge',kind='diamond',x=334,y=480,w=32,h=24)
        f.edge('select','merge')
        f.edge('direct','merge',route=[(600,200),(600,492),(366,492)])
        f.last='merge';f.add('check','系统检查相册可见性',y=536)
        f.decision('visible')
        f.node('denied','系统提示无权查看',x=490,y=612,w=220)
        f.edge('visible','denied','[拒绝]',True)
        f.c.line([(710,636),(718,636),(718,60),(430,60),(430,76)])
        f.last='visible';f.add('grid','系统显示照片缩略图网格',y=696)
        f.add('photo','用户选择照片',system=False)
        f.add('data','照片详情',kind='rect',x=263,w=174,h=44,system=False)
        f.add('show','系统显示大图、评论\n及点赞状态与数量');f.end()
    elif name=='对照片评论':
        f.add('input','用户输入并提交评论',system=False)
        f.obj('content','评论内容')
        f.after_obj('check','系统校验照片可见性\n及内容为 1 至 200 字')
        f.decision('valid');f.error('error','valid','系统提示修改评论','input')
        f.add('save','系统保存评论并显示列表')
        f.decision('remove');y=f.y
        f.node('confirm','系统确认删除本人评论',y=y)
        f.edge('remove','confirm','[删除]')
        f.node('done','用户结束浏览',x=520,y=y,w=170,system=False)
        f.edge('remove','done','[不删除]',True)
        f.last='confirm';f.decision('yes');y=f.y
        f.node('delete','系统删除评论并刷新列表',y=y)
        f.edge('yes','delete','[确认]')
        f.node('keep','系统保留评论',x=520,y=y,w=170)
        f.edge('yes','keep','[取消]',True)
        f.node('merge',kind='diamond',x=334,y=y+84,w=32,h=24)
        f.edge('delete','merge')
        f.node('sideMerge',kind='diamond',x=589,y=y+84,w=32,h=24)
        f.edge('keep','sideMerge',route=[(605,y+48),(605,y+84)])
        f.c.line([(690,f.nodes['done'][1]+24),(710,f.nodes['done'][1]+24),(710,y+96),(621,y+96)])
        f.edge('sideMerge','merge',route=[(589,y+96),(366,y+96)])
        f.last='merge';f.end()
    else:
        f.add('open','用户打开可见照片详情',system=False)
        f.add('state','系统显示点赞状态与数量')
        f.add('input','用户点击点赞或取消点赞',system=False)
        f.obj('request','点赞请求')
        f.after_obj('check','系统确认照片可见\n并读取当前点赞记录')
        f.decision('visible')
        vy=f.nodes['visible'][1]
        f.node('denied','系统提示照片不可访问',x=490,y=vy-4,w=210)
        f.edge('visible','denied','[拒绝]',True)
        f.node('stopped',kind='circle',x=580,y=vy+80,w=30,h=30)
        f.edge('denied','stopped');f.c.shape('circle',586,vy+86,18,18,MAIN)
        f.y=vy+72;f.last='visible'
        f.decision('op');y=f.y
        f.node('like','系统新增点赞记录\n已有记录则保持',x=35,y=y,w=290,h=60)
        f.edge('op','like',route=[(322,f.nodes['op'][1]+20),(180,f.nodes['op'][1]+20),(180,y)])
        f.c.text('[点赞]',205,y-42,110,24,13)
        f.node('unlike','系统移除本人点赞记录\n无记录则保持',x=395,y=y,w=290,h=60)
        f.edge('op','unlike','[取消点赞]',True)
        f.node('merge',kind='diamond',x=334,y=y+96,w=32,h=24)
        f.edge('like','merge',route=[(180,y+60),(180,y+108),(334,y+108)])
        f.edge('unlike','merge',route=[(540,y+60),(540,y+108),(366,y+108)])
        f.last='merge';f.add('show','系统重新统计并显示\n点赞状态与数量');f.end()
    # Guard every binary decision's default downward continuation.
    for key in ('valid','owned','visible'):
        if key in f.nodes and name!='相册类别管理':
            x,y,w,h=f.nodes[key]
            f.c.text('[有效]' if key=='valid' else '[找到]' if key=='owned' else '[允许]',x+w/2+9,y+h+1,85,24,13,align='left')
    return f.c


def class_model(name):
    s=CASES[name];entities=s['entities'];c=Canvas(760,1120)
    c.actor(60,77,s['actor'])
    c.obj(170,77,s['page'],'boundary')
    c.line([(81,77),(136,77)])
    c.line([(192,77),(318,77)])
    def box(title,attrs,ops,x,y,w):
        hh=38; ah=max(1,len(attrs))*24+12;mh=max(1,len(ops))*24+12
        c.shape('rect',x,y,w,hh,LIGHT,value=title,bold=True,size=15)
        c.shape('rect',x,y+hh,w,ah,value='')
        c.shape('rect',x,y+hh+ah,w,mh,value='')
        for i,a in enumerate(attrs):c.text(a,x+4,y+hh+6+i*24,w-8,24,14,align='left')
        for i,a in enumerate(ops):c.text('+ '+a,x+4,y+hh+ah+6+i*24,w-8,24,14,align='left')
        return x,y,w,hh+ah+mh
    ctl=box(s['ctl'],[],s['ops'],318,26,294)
    c.text('+ handler',218,42,96,24,13)
    boxes={}
    if len(entities)==1:
        positions=[(318,330,294)]
    elif len(entities)==2:
        positions=[(28,360,320),(406,360,326)]
    else:
        # Comment/Like entities sit above the two endpoint entities, as in the reference.
        positions=[(28,280,352),(460,360,272),(28,730,352)]
    for (entity,ops),(x,y,w) in zip(entities,positions):
        boxes[entity]=box(entity,ATTRS[entity],ops,x,y,w)
    # Controller navigation, separate anchor per entity; reference's actor-interface-controller structure.
    for i,(entity,_) in enumerate(entities[:2]):
        x,y,w,h=boxes[entity]
        if len(entities)==1:
            pts=[(465,ctl[1]+ctl[3]),(465,y)]
        elif i==0:
            pts=[(350,ctl[1]+ctl[3]),(350,242),(x+w/2,242),(x+w/2,y)]
        else:
            pts=[(580,ctl[1]+ctl[3]),(580,y)]
        c.line(pts)
        if len(entities)<3 or i==0:
            c.text('+ '+entity[0].lower()+entity[1:],x+w/2+12,y-32,min(w/2-16,145),24,13,align='left')
    for a,b,ma,mb,role,aggregate in s['relations']:
        x,y,w,h=boxes[a];X,Y,W,H=boxes[b]
        if len(entities)==2:
            level=max(y+h,Y+H)+44
            pts=[(x+w/2,y+h),(x+w/2,level),(X+W/2,level),(X+W/2,Y+H)]
            c.line(pts,False,diamond=aggregate)
            c.text(ma,x+w/2+12,y+h+9,55,24,13)
            c.text(mb,X+W/2+12,Y+H+9,65,24,13)
            c.text(role,340,level-30,100,24,13)
        else:
            # Relationship to author/photo comes from the record, with endpoint multiplicities.
            ex,ey,ew,eh=boxes[entities[0][0]]
            if a=='User':
                pts=[(x+w/2,y),(ex+ew/2,ey+eh)]
                c.line(pts,False);c.text('1',x+w/2+12,y-32,30,24,13)
                c.text('0..*',ex+ew/2+12,ey+eh+4,60,24,13)
                c.text(role,x+w/2+20,(y+ey+eh)/2-12,110,24,13)
            else:
                pts=[(ex+ew,430),(x,430)]
                c.line(pts,False);c.text('1',x-24,437,20,24,13)
                c.text('0..*',ex+ew+2,437,50,24,13)
                c.text(role,ex+ew+2,400,76,24,13)
    if name=='对照片点赞':
        c.text('{unique (userId, photoId)}',394,690,352,28,14)
    bottom=max(y+h for x,y,w,h in boxes.values())+95
    if len(entities)>=3:bottom=max(bottom,990)
    # Expand to include all attributes rather than shrinking type.
    if bottom>c.h:
        new=Canvas(c.w,bottom);new.im.paste(c.im,(0,0));new.cells=c.cells;new.svg=c.svg;new.rects=c.rects;new.texts=c.texts;new.edges=c.edges;new.n=c.n;c=new
    return c


def collaboration(name):
    s=CASES[name]
    c=Canvas(760,1600)
    font=ImageFont.truetype(str(FONT_DIR/'msyh.ttc'),14*3)
    def wrapped(t,w):
        if c.d.textlength(t,font=font)/3<=w-13:return t
        if '] ' in t:
            guard,operation=t.split('] ',1)
            return guard+']\n'+operation
        prefix,operation=t.split(': ',1)
        return prefix+':\n'+operation
    def height(messages,w=300):
        return sum(30 if '\n' not in wrapped(t,w) else 52 for t in messages)
    upper=s['entity_messages'][0]
    controller_y=max(360,145+height(upper)+45,
                     158+height(s['actor_messages'],545)+20+height(s['requests'],600)+30)
    c.actor(65,65,s['actor'],True)
    c.obj(65,controller_y,s['page'],'boundary',True)
    c.obj(405,controller_y,s['ctl'],'control',True)
    c.line([(65,136),(65,controller_y-22)],False)
    c.line([(87,controller_y),(383,controller_y)],False)
    def msgs(msgs,x,y,w,direction='right'):
        for t in msgs:
            t=wrapped(t,w);h=28 if '\n' not in t else 50;yy=y
            c.text(t,x,yy,w,h,14,align='left')
            if direction=='right':c.line([(x-26,yy+14),(x-8,yy+14)])
            elif direction=='down':c.line([(x-15,yy+3),(x-15,yy+23)])
            elif direction=='up':c.line([(x-15,yy+23),(x-15,yy+3)])
            elif direction=='left':c.line([(x+w+23,yy+14),(x+w+5,yy+14)])
            y+=h+2
        return y
    msgs(s['actor_messages'],106,158,545,'down')
    msgs(s['requests'],118,controller_y-30-len(s['requests'])*30,600)
    bottom=controller_y+100
    for i,((entity,_),messages) in enumerate(zip(s['entities'],s['entity_messages'])):
        if not messages:continue
        if i==0:
            c.obj(405,70,entity,'entity',True)
            c.line([(405,controller_y-22),(405,130)],False)
            msgs(messages,440,145,300,'up')
        elif i==1:
            cy=max(controller_y+280,controller_y+105+height(messages)+70)
            c.obj(405,cy,entity,'entity',True)
            c.line([(405,controller_y+70),(405,cy-22)],False)
            msgs(messages,440,controller_y+105,300,'down')
            bottom=cy+95
    for note in COLLABORATION_NOTES.get(name,[]):
        c.text(note,28,bottom,704,25,13,align='left');bottom+=28
    c.h=bottom+24;c.im=c.im.crop((0,0,c.w*3,c.h*3))
    return c


def report_module_usecases():
    """Report modules follow the four groups in the functional framework."""
    figures={}
    c=Canvas(760,540)
    c.shape('rect',210,30,520,470,fs.CONTAINER_FILL,fs.CONTAINER_STROKE)
    c.text('电子相册系统',280,44,380,30,16,bold=True)
    c.actor(80,210,'普通用户');c.actor(80,398,'管理员')
    for label,y in [('创建相册',90),('修改相册',225),('相册类别管理',360)]:
        c.shape('circle',410,y,250,66,value=label)
    c.line([(98,210),(165,210),(165,123),(410,123)],False)
    c.line([(165,210),(165,258),(410,258)],False)
    c.line([(98,393),(410,393)],False)
    figures['相册管理模块用例图']=c
    c=Canvas(760,430)
    c.shape('rect',210,30,520,360,fs.CONTAINER_FILL,fs.CONTAINER_STROKE)
    c.text('电子相册系统',280,44,380,30,16,bold=True)
    c.actor(80,205,'普通用户')
    for label,y in [('对照片评论',110),('对照片点赞',245)]:
        c.shape('circle',410,y,250,66,value=label)
    c.line([(98,205),(165,205),(165,143),(410,143)],False)
    c.line([(165,205),(165,278),(410,278)],False)
    figures['评论与点赞模块用例图']=c
    return figures


def main():
    records=[]
    for name,s in CASES.items():
        base=ROOT/'docs/交付'/s['module']/'images'
        for kind,func in [('活动图',activity),('类模型图',class_model),('协作图',collaboration)]:
            records.append(func(name).save(base/(name+'_'+kind)))
    # Like is one use case; unlike is its alternative flow.
    c=Canvas(600,360)
    c.actor(90,135,'普通用户')
    c.shape('rect',210,35,355,275,fs.CONTAINER_FILL,fs.CONTAINER_STROKE)
    c.text('电子相册系统',245,53,280,30,16,bold=True)
    c.shape('circle',280,135,220,72,value='对照片点赞')
    c.line([(110,135),(180,135),(180,171),(280,171)],False)
    c.text('取消点赞为扩展流程',250,240,280,30,14)
    records.append(c.save(ROOT/'docs/交付/5-点赞功能/images/点赞功能用例图'))
    for title,diagram in report_module_usecases().items():
        diagram.save(ROOT/'docs/图稿'/title)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':main()
