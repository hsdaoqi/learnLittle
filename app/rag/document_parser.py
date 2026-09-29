"""把上传文件转成纯文本。

支持 TXT / Markdown 直接解码，PDF 用 pypdf（未安装则明确报错）。
解析失败不静默吞掉：调用方据此回滚落盘文件。
"""

from pathlib import Path

from app.core.failed_response import BusinessError, ErrorCode


def parse_document(content: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".markdown":
        ext = ".md"

    if ext in {".txt", ".md"}:
        return content.decode("utf-8", errors="replace")

    if ext == ".pdf":
        return _parse_pdf(content)

    raise BusinessError(
        code=ErrorCode.UNSUPPORTED_FILE_TYPE,
        detail=f"无法解析的文件类型: {ext}",
    )


def _parse_pdf(content: bytes) -> str:
    try:
        from io import BytesIO

        from pypdf import PdfReader
    except ImportError as exc:
        raise BusinessError(
            code=ErrorCode.INTERNAL_ERROR,
            message="PDF 解析依赖未安装",
            detail="请安装 pypdf",
            http_status=500,
        ) from exc

    try:
        reader = PdfReader(BytesIO(content))
        pages = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text)
        return "\n\n".join(pages)
    except Exception as exc:
        raise BusinessError(
            code=ErrorCode.INVALID_PARAMETER,
            message="PDF 解析失败",
            detail=str(exc),
        ) from exc
