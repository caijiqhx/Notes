# JavaScript 基础知识

> - [JavaScript 基础知识](https://zh.javascript.info/first-steps)

`'use strict';` 使用现代模式。

## 变量

推荐使用 `let` 而不是 `var`声明变量，之后会介绍它们的区别。

### 变量命名

- 字母、数字、`$` 或 `_`。
- 首字母非数字。
- 区分大小写。
- `const` 定义常量。

## 数据类型

### Number

- 整数和浮点数。
- `Infinity, -Infinity`
- `NaN`，任何对 `NaN` 操作结果都会返回 `NaN`。

### BitInt

通过整数末尾附加 `n` 创建 `BigInt` 类型的变量，用于表示任意长度的整数。

### String

- `"", '', `` `，反引号表示功能扩展，允许将变量和表达式包装到 `${...}` 中嵌入字符串。

### Boolean

- `true, false`

### null

`null` 仅表示空，值未知。

### undefined

`undefined` 表示未被赋值。

### object 和 symbol

- `object` 用于存储数据集合和更复杂的实体。
- `symbol` 用于创建对象的唯一标识符。

### typeof

- 返回参数的类型。

## 类型转换

- 字符串转换：需要字符串形式时，就会进行字符串转换，或显式使用 `string()`。
- 数字转换：算术函数和表达式中，自动进行数字类型转换，显式使用 `number()`。`null` 转换成 0，`undefined` 转换为 `NaN`。
- `boolean` 转换：直观上为空的值 `0, '', null, undefined, NaN` 转为 `false`。

## 运算符

- 单目运算符 `+` 会把变量转换为数字。

```js
// 类型转换示例
"" + 1 + 0      // "10"
"" - 1 + 0      // -1
true + false    // 1
6 / "3"         // 2
"2" * "3"       // 6
4 + 5 + "px"    // 9px
"$" + 4 + 5     // $45
"4" - 2         // 2
"4px" - 2       // NaN
7 / 0           // Infinity
"   -9  " + 5   // "   -9  5"
"   -9  " - 5   // -14
null + 1        // 1
undefined + 1   // NaN
" \t \n" - 2    // -2 字符串转数字会忽略首尾的空格字符
```

## 值的比较

- 不同类型的比较，会先转化为数字。

### 严格相等

`===` 比较不会做任何的类型转换。

### null 和 undefined 比较

`null` 和 `undefined` 在 `==` 下不会进行任何的类型转换，因此仅限于二者互等。

```js
// 类型转换示例
null === undefined  // false
null == undefined   // true
null == "\n0\n"     // false
null === +"\n0\n"   // false
```

## 交互

三个与用户交互的函数：

- `alert`，显示信息。
- `prompt`，要求用户输入文本。
- `confirm`，显示信息等待用户点击确定 true 或 取消 false。

## 条件判断

- `if` 语句和 `? :` 运算符。
- `switch` 语句，任何表达式都可以成为 `switch` 的参数，严格相等才匹配。

## 循环 

- `while, do...while`
- `for`

## 函数

- `return` 之后换行会自动加分号，最好加上 `{}`。

### 函数表达式 

```js
let test = function () {}
```

函数的创建也相当于变量赋值，因此可以作为参数传入。

js 在运行前会寻找全局函数声明并创建函数，因此在定义之前就可以调用。

### 箭头函数

创建函数的简单语法

```js
let func = (arg1, arg2, ...argN) => {}
```

## 调试

可以使用浏览器调试 js。