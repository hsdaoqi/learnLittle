# app/utils/file_handler.py

[源码](D:/Project/learnLittle/app/utils/file_handler.py) | [任务流程 02](D:/Project/learnLittle/docs/backend-tutorial/02-account.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

文档/头像的大小和格式约束、安全文件名与受限读取，兼用于上传章节。

## 本文件导航

- [infer_mime](#fn-8e307235290f15c2)
- [calculate_md5_bytes](#fn-8f58cb0ae61b0cdb)
- [validate_upload_file](#fn-27b8519688e61803)
- [read_upload_limited](#fn-61efcb20f3f5bb82)
- [get_safe_filename](#fn-d5514be6cd27f659)
- [ensure_dir](#fn-9c16cd3f9eeb2155)
- [_match_magic](#fn-cf037804f74ba8d9)
- [validate_avatar_file](#fn-e8270dd71b0d889a)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
FORBIDDEN_EXTENSIONS = {'.exe', '.bat', '.cmd', '.com', '.msi', '.scr', '.sh', '.bash', '.csh', '.zip', '.rar', '.7z', '.tar', '.gz', '.dll', '.so', '.dylib', '.bin'}

EXT_TO_MIME = {'.pdf': 'application/pdf', '.md': 'text/markdown', '.markdown': 'text/markdown', '.txt': 'text/plain'}

AVATAR_MAGIC = {'.png': [(0, b'\x89PNG\r\n\x1a\n')], '.jpg': [(0, b'\xff\xd8\xff')], '.jpeg': [(0, b'\xff\xd8\xff')], '.webp': [(0, b'RIFF'), (8, b'WEBP')]}
```

<a id="fn-8e307235290f15c2"></a>

## infer_mime

源码：[L48](D:/Project/learnLittle/app/utils/file_handler.py:48)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

优先使用客户端声明的 MIME，未声明才按扩展名映射，.markdown 归一为 .md。只是元数据描述，不能据此证明文件真实内容。

**输入与签名**

```python
def infer_mime(filename: str, declared: str | None) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return declared or EXT_TO_MIME.get(ext, 'application/octet-stream')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Path(filename).suffix.lower
Path
EXT_TO_MIME.get
```

<a id="fn-8f58cb0ae61b0cdb"></a>

## calculate_md5_bytes

源码：[L55](D:/Project/learnLittle/app/utils/file_handler.py:55)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

为已读取字节生成 MD5 摘要，上传用来检查同用户重复文件。不是安全密码哈希，也不是用户权限凭证。

**输入与签名**

```python
def calculate_md5_bytes(data: bytes) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return hashlib.md5(data).hexdigest()
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
hashlib.md5(data).hexdigest
hashlib.md5
```

<a id="fn-27b8519688e61803"></a>

## validate_upload_file

源码：[L61](D:/Project/learnLittle/app/utils/file_handler.py:61)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

校验上传长度和支持扩展名，返回规范化 .pdf/.md/.txt。异常在流开始前可作为普通业务错误返回。

**输入与签名**

```python
def validate_upload_file(filename: str, file_size: int, max_size_mb: int=50) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ext
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
BusinessError
Path(filename or '').suffix.lower
Path
```

<a id="fn-61efcb20f3f5bb82"></a>

## read_upload_limited

源码：[L86](D:/Project/learnLittle/app/utils/file_handler.py:86)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

分块读取 UploadFile，累计超过上限立即报错，最终返回 bytes。限制内仍会积累完整内容，不是磁盘流式零内存上传。

**输入与签名**

```python
async def read_upload_limited(file: UploadFile, max_size_mb: int) -> bytes
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return bytes(content)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
getattr
BusinessError
bytearray
file.read
content.extend
len
bytes
```

<a id="fn-d5514be6cd27f659"></a>

## get_safe_filename

源码：[L110](D:/Project/learnLittle/app/utils/file_handler.py:110)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

取文件 basename，替换残留分隔符并删除空字节，空名返回 unnamed。随机前缀由 knowledge service 另加，这个函数不生成随机名称。

**输入与签名**

```python
def get_safe_filename(filename: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return safe_name or 'unnamed'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Path
safe_name.replace('/', '_').replace('\\', '_').replace
safe_name.replace('/', '_').replace
safe_name.replace
```

<a id="fn-9c16cd3f9eeb2155"></a>

## ensure_dir

源码：[L116](D:/Project/learnLittle/app/utils/file_handler.py:116)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

确保目录存在，允许已有目录。是文件系统副作用，不属于数据库回滚范围。

**输入与签名**

```python
def ensure_dir(dir_path: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Path(dir_path).mkdir
Path
```

<a id="fn-cf037804f74ba8d9"></a>

## _match_magic

源码：[L120](D:/Project/learnLittle/app/utils/file_handler.py:120)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

比较允许的图片文件头特征，辅助头像格式检查。只做签名字节检查，不完成完整图片解码。

**输入与签名**

```python
def _match_magic(content: bytes, signatures: list[tuple[int, bytes]]) -> bool
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return False
return all((content[offset:offset + len(magic)] == magic for offset, magic in signatures))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
all
len
```

<a id="fn-e8270dd71b0d889a"></a>

## validate_avatar_file

源码：[L128](D:/Project/learnLittle/app/utils/file_handler.py:128)；任务：[第 02 章](D:/Project/learnLittle/docs/backend-tutorial/02-account.md)。

结合大小、扩展名和 magic bytes 检查头像并返回规范扩展名。不等于恶意内容扫描或重新编码图片。

**输入与签名**

```python
def validate_avatar_file(filename: str, file_size: int, content: bytes, max_size_mb: int=5) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ext
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
BusinessError
Path(filename or '').suffix.lower
Path
_match_magic
```
