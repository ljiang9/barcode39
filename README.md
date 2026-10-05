# barcode39

把文本编码成 **Code 39** 条形码的 ASCII 艺术图。纯 Python 标准库,零依赖。

```console
$ python -m barcode39 "HELLO-123"
█   █ ██ ... (条形码)
        HELLO-123
```

## 用法

```console
python -m barcode39 "HELLO-123"      # 默认高度 3 行,下方带人眼可读文本
python -m barcode39 "ABC" --height 5 # 更高的条码
python -m barcode39 "ABC" --ratio 2  # 宽窄比 2:1(更紧凑)
python -m barcode39 "ABC" --no-text  # 不打印下方文本
```

也可以当库用:

```python
from barcode39 import render
for row in render("HELLO-123"):
    print(row)
```

## 编码规则(小抄)

- Code 39 又叫 "3 of 9":每个字符由 9 个元素组成(5 条 bars + 4 个 spaces),
  其中恰好 3 个是宽的。
- 可编码 43 个字符:`0-9`、`A-Z`、`-`、`.`、`$`、`/`、`+`、`%`、空格。
  **只有大写字母**,小写会被拒绝并提示改成大写。
- 条码首尾自动加上起始/终止符 `*`,字符之间用一个窄空隙隔开。

字符表依据公开规范:Wikipedia "Code 39" 词条的编码规则、
ISO/IEC 16388:2023,并与 Scribus 的 `code39.py` 脚本字符表逐项交叉核对一致。
详见 `barcode39.py` 顶部注释。

## 已知局限(诚实说明)

- 这是**装饰/教学用途**的 ASCII 渲染,等宽字体下才对齐;**不要拿去做真实扫码**,
  真实条码对打印精度、宽窄比、静区有严格要求。
- 不实现可选的 mod 43 校验位、不实现 Full ASCII 扩展(大小写/控制字符的双字符编码)。
- 宽窄比用字符数近似(`--ratio`),不是精确的物理比例。
