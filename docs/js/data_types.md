# 数据类型

## 原始类型的方法

- js 允许访问字符串、数字、布尔值和符号的方法和属性。
- js 创建了提供额外功能的对象包装器，`String, Number, Boolean, Symbol`，提供了不同的方法。
- 访问原始类型的属性或方法时，会创建一个对象包装器，属性和方法的访问都基于这个包装器。结束后对象被销毁。
- `null` 和 `undefined` 没有对应的对象包装器，也不提供任何方法。
- 原始类型虽然可以像对象一样访问方法和属性，但是不能存储额外的数据，因此不是对象。

## 数字类型

js 中的所有数字都以 64 位 IEEE-754 格式存储。

- 支持科学计数 `1e6` 格式。
- 支持十六进制 `0x`、二进制 `0b` 和八进制 `0o`。

### toString(base)

返回指定进制的字符串表示，base = 36 是最大值。

数字直接调用方法可以使用 `..`，`123..toString(2)`。

### 数值修约 Rounding

- 内置的数值修约，`Math.floor` 向下舍入，`Math.ceil` 向上舍入，`Math.round` 最近整数舍入，`Math.trunc` 删除小数点后内容。
- `toFixed(n)`，舍入到小数点后第 n 位，返回一个字符串。

### 不精确计算

js 内使用 64 位 IEEE-754 格式表示，数字太大会溢出。精度问题可能会影响浮点数的比较及运算。

- 使用 `isNaN()` 检查是否为 `NaN`，不可用 `===`。
- `isFinite()`，检查是否是常规数字，而不是 `NaN/Infinity/-Infinity`。
- 使用 `Object.is()` 比较 `===` 等值，对 `NaN` 会返回 `true`，对 `+-0` 会返回 `false`。

### parseInt 和 parseFloat

- 使用 `+` 或 `Number()` 的数字转换很严格，除了首尾的空格外，其他非数字字符都会使转换结果为 `NaN`。
- 使用 `parseInt` 和 `parseFloat` 从字符串中读出一个数字，知道无法读取位置。
- `parseInt` 有一个可选的参数，用于指定进制，因此可以解析十六进制。

### 其他数学函数

js 有一个内置的 Math 对象，它包含了一个小型的数学函数和常量库。

- `Math.random()`，返回从 `[0, 1)` 的随机数。
- `Math.max(a, b, ...)/Math.min(a, b, ...)`
- `Math.pow(n, power)`
- 更多函数参见 [MDN](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Math)

## 字符串

js 中，文本数据以字符串存储，内部格式为 `utf-16`。

### 引号 Quotes

- 反引号 ` `` ` 允许通过 `${...}` 将任何表达式嵌入到字符串中，且允许字符串跨行。

