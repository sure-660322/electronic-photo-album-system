"""Numbered message traces for the nine use-case sequence diagrams."""


def call(sender, receiver, label):
    return "call", sender, receiver, label


def reply(sender, receiver, result):
    return "reply", sender, receiver, result


def action(participant, method):
    return call(participant, participant, method)


def alt(*branches):
    return "alt", *branches


def participants(actor, page, route, *others):
    return (("actor", actor, "actor"), ("page", page, "boundary"), ("api", route, "control"), *others)


ACCOUNT = ("account", ": AccountService", "control")
ALBUM = ("album", ": AlbumService", "control")
CATEGORY = ("category", ": CategoryService", "control")
PHOTO = ("photo", ": PhotoService", "control")
POLICY = ("policy", ": AlbumAccessPolicy", "control")
STORAGE = ("storage", ": LocalPhotoStorage", "infrastructure")
DB = ("db", ": Session\nSQLAlchemy", "infrastructure")


SEQUENCES = [
    (
        "用户注册", "账户服务校验表单，写入含密码哈希的普通账户，成功后进入登录页。",
        participants("访客", "Vue 注册页", "FastAPI 注册路由", ACCOUNT, DB),
        (
            call("actor", "page", "submit(form)"),
            call("page", "api", "POST /api/auth/register"),
            call("api", "account", "register(data)"),
            call("account", "db", "scalar(user_by_username)"),
            reply("db", "account", "None"),
            call("account", "db", "add(user)"),
            call("account", "db", "commit()"),
            reply("account", "api", "user"),
            reply("api", "page", "201 AccountView"),
            action("page", "open_login()"),
        ),
    ),
    (
        "用户登录", "凭据验证成功后签发会话令牌，页面按账户角色跳转。",
        participants("登录用户", "Vue 登录页", "FastAPI 认证路由", ACCOUNT, DB),
        (
            call("actor", "page", "submit(credentials)"),
            call("page", "api", "POST /api/auth/login"),
            call("api", "account", "authenticate(data)"),
            call("account", "db", "scalar(user_by_username)"),
            reply("db", "account", "user"),
            reply("account", "api", "verified_user"),
            call("api", "account", "issue_token(user)"),
            reply("account", "api", "token"),
            reply("api", "page", "200 AccountView + album_session Cookie"),
            action("page", "route_by_role(role)"),
        ),
    ),
    (
        "创建相册", "页面加载类别，服务按当前用户建立相册，成功后刷新本人列表。",
        participants("普通用户", "Vue 创建页", "相册与类别路由", CATEGORY, ALBUM, DB),
        (
            call("actor", "page", "open_create_form()"),
            call("page", "api", "GET /api/categories"),
            call("api", "category", "list_categories()"),
            reply("category", "api", "categories"),
            reply("api", "page", "200 CategoryView[]"),
            call("actor", "page", "submit(form)"),
            call("page", "api", "POST /api/albums"),
            call("api", "album", "create(actor, data)"),
            call("album", "db", "scalar(category_by_id)"),
            reply("db", "album", "category"),
            call("album", "db", "add(album)"),
            call("album", "db", "commit()"),
            reply("album", "api", "album"),
            reply("api", "page", "201 AlbumView"),
            call("page", "api", "GET /api/albums?scope=mine"),
            call("api", "album", "list_albums(actor, scope)"),
            reply("album", "api", "albums"),
            reply("api", "page", "200 AlbumView[]"),
        ),
    ),
    (
        "修改相册", "更新时核对归属和版本，版本冲突后保留草稿并重新读取相册。",
        participants("普通用户", "Vue 编辑页", "相册与类别路由", ALBUM, POLICY, DB),
        (
            call("actor", "page", "open_editor(album_id)"),
            call("page", "api", "GET /api/albums/{album_id}?scope=mine"),
            call("api", "album", "get_album(actor, album_id, scope)"),
            call("album", "policy", "require_owned(actor, album_id)"),
            reply("policy", "album", "album"),
            reply("album", "api", "album"),
            reply("api", "page", "200 AlbumView(version)"),
            call("page", "api", "GET /api/categories"),
            reply("api", "page", "200 CategoryView[]"),
            call("actor", "page", "submit(form, version)"),
            call("page", "api", "PUT /api/albums/{album_id}"),
            call("api", "album", "update(actor, album_id, data)"),
            call("album", "policy", "require_owned(actor, album_id)"),
            reply("policy", "album", "album"),
            call("album", "db", "execute(update_owned_album_at_version)"),
            reply("db", "album", "affected_rows"),
            alt(("更新成功", [
                call("album", "db", "commit()"),
                reply("album", "api", "updated_album"),
                reply("api", "page", "200 AlbumView"),
            ]), ("版本冲突", [
                call("album", "policy", "require_owned(actor, album_id)"),
                reply("policy", "album", "current_album"),
                reply("album", "api", "ALBUM_VERSION_CONFLICT"),
                reply("api", "page", "409 ALBUM_VERSION_CONFLICT"),
                action("page", "keep_draft(form)"),
                call("page", "api", "GET /api/albums/{album_id}?scope=mine"),
                call("api", "album", "get_album(actor, album_id, scope)"),
                reply("album", "api", "current_album"),
                reply("api", "page", "200 AlbumView(version)"),
            ])),
        ),
    ),
    (
        "相册类别管理", "管理员选择新增、修改或删除类别，成功后刷新列表。",
        participants("管理员", "Vue 类别管理页", "FastAPI 类别路由", CATEGORY, DB),
        (
            call("actor", "page", "open_category_list()"),
            call("page", "api", "GET /api/categories"),
            call("api", "category", "list_categories()"),
            reply("category", "api", "categories"),
            reply("api", "page", "200 CategoryView[]"),
            call("actor", "page", "submit(operation)"),
            alt(("新增", [
                call("page", "api", "POST /api/categories"),
                call("api", "category", "create(actor, data)"),
                call("category", "db", "add(category)"),
                call("category", "db", "commit()"),
                reply("category", "api", "category"),
                reply("api", "page", "201 CategoryView"),
            ]), ("修改", [
                call("page", "api", "PUT /api/categories/{category_id}"),
                call("api", "category", "update(actor, category_id, data)"),
                call("category", "db", "execute(update_category)"),
                call("category", "db", "commit()"),
                reply("category", "api", "category"),
                reply("api", "page", "200 CategoryView"),
            ]), ("删除未被相册引用的类别", [
                call("page", "api", "DELETE /api/categories/{category_id}"),
                call("api", "category", "delete(actor, category_id)"),
                call("category", "db", "delete(category)"),
                call("category", "db", "commit()"),
                reply("category", "api", "None"),
                reply("api", "page", "204 No Content"),
            ])),
            call("page", "api", "GET /api/categories"),
            call("api", "category", "list_categories()"),
            reply("category", "api", "categories"),
            reply("api", "page", "200 CategoryView[]"),
        ),
    ),
    (
        "上传图片", "新上传在原图和缩略图就绪后提交，文件处理失败时回滚并清理本次文件。",
        participants("普通用户", "Vue 相册页", "FastAPI 照片路由", PHOTO, POLICY, DB, STORAGE),
        (
            call("actor", "page", "submit(file)"),
            call("page", "api", "POST /api/albums/{album_id}/photos"),
            call("api", "photo", "upload(actor, album_id, file, upload_id)"),
            call("photo", "policy", "require_owned(actor, album_id)"),
            reply("policy", "photo", "album"),
            call("photo", "db", "execute(reserve_photo_by_upload_id)"),
            reply("db", "photo", "photo_id"),
            alt(("原图和缩略图写入成功", [
                call("photo", "storage", "save(path, stream) · original"),
                action("photo", "make_thumbnail(file)"),
                call("photo", "storage", "save(path, stream) · thumbnail"),
                call("photo", "db", "commit()"),
                reply("photo", "api", "(photo, True)"),
                reply("api", "page", "201 PhotoView"),
            ]), ("文件处理失败", [
                call("photo", "db", "rollback()"),
                call("photo", "storage", "remove(path)"),
                reply("photo", "api", "UPLOAD_FAILED"),
                reply("api", "page", "500 UPLOAD_FAILED"),
            ])),
        ),
    ),
    (
        "浏览照片", "相册、照片详情与图片读取逐次校验可见性，原图和缩略图共用读图方法。",
        participants("登录用户", "Vue 浏览与详情页", "相册与照片路由", ALBUM, PHOTO, POLICY, STORAGE),
        (
            call("actor", "page", "open_browser()"),
            call("page", "api", "GET /api/albums?scope=visible"),
            call("api", "album", "list_albums(actor, scope)"),
            reply("album", "api", "albums"),
            reply("api", "page", "200 AlbumView[]"),
            call("actor", "page", "select_album(album_id)"),
            call("page", "api", "GET /api/albums/{album_id}/photos"),
            call("api", "photo", "list_photos(actor, album_id)"),
            call("photo", "policy", "require_visible(actor, album_id)"),
            reply("photo", "api", "photos"),
            reply("api", "page", "200 PhotoView[]"),
            call("actor", "page", "select_photo(photo_id)"),
            call("page", "api", "GET /api/photos/{photo_id}"),
            call("api", "photo", "get_detail(actor, photo_id)"),
            call("photo", "policy", "require_visible(actor, album_id)"),
            reply("photo", "api", "detail"),
            reply("api", "page", "200 PhotoDetail"),
            call("page", "api", "GET /api/photos/{photo_id}/original"),
            call("api", "photo", "open_image(actor, photo_id, variant)"),
            call("photo", "policy", "require_visible(actor, album_id)"),
            call("photo", "storage", "open(path)"),
            reply("storage", "photo", "stream"),
            reply("photo", "api", "stream"),
            reply("api", "page", "200 ImageStream"),
        ),
    ),
    (
        "对照片评论", "发布后加入新评论，确认删除本人评论后重新读取详情。",
        participants("普通用户", "Vue 照片详情页", "评论与照片路由",
                     ("comment", ": CommentService", "control"), POLICY, DB),
        (
            alt(("发表评论", [
                call("actor", "page", "submit(body)"),
                call("page", "api", "POST /api/photos/{photo_id}/comments"),
                call("api", "comment", "create(actor, photo_id, body)"),
                call("comment", "policy", "require_visible(actor, album_id)"),
                call("comment", "db", "add(comment)"),
                call("comment", "db", "commit()"),
                reply("comment", "api", "comment"),
                reply("api", "page", "201 CommentView"),
            ]), ("确认删除本人评论", [
                call("actor", "page", "confirm_delete(comment_id)"),
                call("page", "api", "DELETE /api/photos/{photo_id}/comments/{comment_id}"),
                call("api", "comment", "delete(actor, photo_id, comment_id)"),
                call("comment", "policy", "require_visible(actor, album_id)"),
                call("comment", "db", "scalar(comment_by_photo_and_id)"),
                reply("db", "comment", "comment"),
                call("comment", "db", "delete(comment)"),
                call("comment", "db", "commit()"),
                reply("comment", "api", "None"),
                reply("api", "page", "204 No Content"),
                call("page", "api", "GET /api/photos/{photo_id}"),
                reply("api", "page", "200 PhotoDetail"),
            ])),
        ),
    ),
    (
        "对照片点赞", "点赞和取消写入指定状态，提交后返回本人状态和点赞总数。",
        participants("普通用户", "Vue 照片详情页", "FastAPI 点赞路由",
                     ("like", ": LikeService", "control"), POLICY, DB),
        (
            call("actor", "page", "toggle_like(liked)"),
            call("page", "api", "PUT /api/photos/{photo_id}/like"),
            call("api", "like", "set_liked(actor, photo_id, liked)"),
            call("like", "policy", "require_visible(actor, album_id)"),
            reply("policy", "like", "album"),
            alt(("liked=true", [
                call("like", "db", "execute(insert_like_if_absent)"),
            ]), ("liked=false", [
                call("like", "db", "execute(delete_own_like)"),
            ])),
            call("like", "db", "execute(select_like_state)"),
            reply("db", "like", "(liked, like_count)"),
            call("like", "db", "commit()"),
            reply("like", "api", "like_state"),
            reply("api", "page", "200 LikeState"),
        ),
    ),
]
