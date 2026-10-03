# app/rag/document_parser.py

[源码](D:/Project/learnLittle/app/rag/document_parser.py) | [任务流程 05](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

bytes->纯文本；PDF 文字提取，不含 OCR。

## 本文件导航

- [parse_document](#fn-b00a17021a4e5c53)
- [_parse_pdf](#fn-8b4fe26d58ff95b2)
<a id="fn-b00a17021a4e5c53"></a>

## parse_document

源码：[L12](D:/Project/learnLittle/app/rag/document_parser.py:12)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

按类型选择 TXT/MD 的 UTF-8 容错读取或 PDF 提取，并把读取异常转业务错误。返回纯文本，不生成向量。

**输入与签名**

```python
def parse_document(content: bytes, filename: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return content.decode('utf-8', errors='replace')
return _parse_pdf(content)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Path(filename).suffix.lower
Path
content.decode
_parse_pdf
BusinessError
```

<a id="fn-8b4fe26d58ff95b2"></a>

## _parse_pdf

源码：[L29](D:/Project/learnLittle/app/rag/document_parser.py:29)；任务：[第 05 章](D:/Project/learnLittle/docs/backend-tutorial/05-rag.md)。

使用 pypdf 逐页提取可读文本并合并。扫描图片无文字层时不会自动 OCR，空提取需由后续处理。

**输入与签名**

```python
def _parse_pdf(content: bytes) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return '\n\n'.join(pages)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
BusinessError
PdfReader
BytesIO
page.extract_text
text.strip
pages.append
'\n\n'.join
str
```
