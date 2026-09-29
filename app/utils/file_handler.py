"""知识库上传校验与文件名处理。

知识库只接受 PDF / Markdown / TXT。头像只接受 PNG / JPG / WebP。
"""

from pathlib import Path

from fastapi import UploadFile

from app.core.failed_response import BusinessError, ErrorCode

FORBIDDEN_EXTENSIONS = {
    ".exe",
    ".bat",
    ".cmd",
    ".com",
    ".msi",
    ".scr",
    ".sh",
    ".bash",
    ".csh",
    ".zip",
    ".rar",
    ".7z",
    ".tar",
    ".gz",
    ".dll",
    ".so",
    ".dylib",
    ".bin",
}

EXT_TO_MIME = {
    ".pdf": "application/pdf",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".txt": "text/plain",
}

AVATAR_MAGIC = {
    ".png": [(0, b"\x89PNG\r\n\x1a\n")],
    ".jpg": [(0, b"\xff\xd8\xff")],
    ".jpeg": [(0, b"\xff\xd8\xff")],
    ".webp": [(0, b"RIFF"), (8, b"WEBP")],
}


def infer_mime(filename: str, declared: str | None) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".markdown":
        ext = ".md"
    return declared or EXT_TO_MIME.get(ext, "application/octet-stream")


def calculate_md5_bytes(data: bytes) -> str:
    import hashlib

    return hashlib.md5(data).hexdigest()


def validate_upload_file(filename: str, file_size: int, max_size_mb: int = 50) -> str:
    """校验大小与扩展名，返回标准化扩展名（.pdf / .md / .txt）。"""
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise BusinessError(
            code=ErrorCode.FILE_TOO_LARGE,
            detail=f"文件大小 {file_size / 1024 / 1024:.1f}MB 超过限制 {max_size_mb}MB",
        )

    ext = Path(filename or "").suffix.lower()
    if ext in FORBIDDEN_EXTENSIONS:
        raise BusinessError(
            code=ErrorCode.UNSUPPORTED_FILE_TYPE,
            detail=f"禁止上传 {ext} 类型的文件",
        )
    if ext == ".markdown":
        ext = ".md"
    if ext not in {".pdf", ".md", ".txt"}:
        raise BusinessError(
            code=ErrorCode.UNSUPPORTED_FILE_TYPE,
            detail=f"不支持的文件类型: {ext or '(无扩展名)'}，仅支持 PDF / Markdown / TXT",
        )
    return ext


async def read_upload_limited(file: UploadFile, max_size_mb: int) -> bytes:
    """分块读取，超过上限立即中断，避免超大文件打爆内存。"""
    max_size_bytes = max_size_mb * 1024 * 1024
    declared_size = getattr(file, "size", None)
    if declared_size is not None and declared_size > max_size_bytes:
        raise BusinessError(
            code=ErrorCode.FILE_TOO_LARGE,
            detail=f"文件大小 {declared_size / 1024 / 1024:.1f}MB 超过限制 {max_size_mb}MB",
        )

    content = bytearray()
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        content.extend(chunk)
        if len(content) > max_size_bytes:
            raise BusinessError(
                code=ErrorCode.FILE_TOO_LARGE,
                detail=f"文件超过大小限制 {max_size_mb}MB，已中断读取",
            )
    return bytes(content)


def get_safe_filename(filename: str) -> str:
    safe_name = Path(filename).name
    safe_name = safe_name.replace("/", "_").replace("\\", "_").replace("\x00", "")
    return safe_name or "unnamed"


def ensure_dir(dir_path: str) -> None:
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def _match_magic(content: bytes, signatures: list[tuple[int, bytes]]) -> bool:
    if not content:
        return False
    return all(
        content[offset : offset + len(magic)] == magic for offset, magic in signatures
    )


def validate_avatar_file(
    filename: str, file_size: int, content: bytes, max_size_mb: int = 5
) -> str:
    """校验头像：大小 + 扩展名白名单 + magic bytes。返回标准化扩展名。"""
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise BusinessError(
            code=ErrorCode.FILE_TOO_LARGE,
            detail=f"头像文件大小 {file_size / 1024 / 1024:.1f}MB 超过限制 {max_size_mb}MB",
        )

    ext = Path(filename or "").suffix.lower()
    if ext == ".jpeg":
        ext = ".jpg"
    if ext not in AVATAR_MAGIC:
        raise BusinessError(
            code=ErrorCode.UNSUPPORTED_FILE_TYPE,
            detail=f"不支持的头像格式: {ext or '(无扩展名)'}，仅支持 PNG / JPG / WebP",
        )
    if not _match_magic(
        content, AVATAR_MAGIC[ext] if ext != ".jpg" else AVATAR_MAGIC[".jpg"]
    ):
        raise BusinessError(
            code=ErrorCode.UNSUPPORTED_FILE_TYPE,
            detail="文件内容与扩展名不符",
        )
    return ext
