"""本地图片存储：在仓库根目录 uploads/ 下读写和清理图片文件。"""
import shutil
from pathlib import Path

from ..config import get_settings


class LocalPhotoStorage:
    """照片服务持有并调用；路径一律使用相对 uploads/ 的 POSIX 路径。"""

    def __init__(self, root: Path | None = None):
        self.root = root or get_settings().uploads_root

    def resolve(self, relative_path: str) -> Path:
        path = (self.root / relative_path).resolve()
        if self.root.resolve() not in path.parents:
            raise ValueError(f"路径越界: {relative_path}")
        return path

    def save(self, relative_path: str, data: bytes) -> None:
        path = self.resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(data)
            handle.flush()

    def exists(self, relative_path: str) -> bool:
        return self.resolve(relative_path).is_file()

    def remove_dir(self, relative_dir: str) -> None:
        """清理本次上传尝试的独立目录（uploads/albums/{album_id}/{file_key}/）。"""
        path = (self.root / relative_dir).resolve()
        if self.root.resolve() not in path.parents:
            return
        shutil.rmtree(path, ignore_errors=True)

    def ensure_root(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
