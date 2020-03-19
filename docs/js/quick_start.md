# JS 快速入门

- 关于分号 `;`，强迫症觉得还是加上看着更舒服。
- js 严格区分大小写

## 数据类型和变量

### Number

不区分整数和浮点数，统一用 Number 表示。

### 字符串

用单引号或双引号

### 布尔值

`true` or `false`

#### 比较运算符

- `==`：自动转换数据类型再比较。
- `===`：类型不一致返回 `false`。

`NaN === NaN` 返回 `false`，因此唯一判断 NaN 的方法就是 `isNaN()` 函数。

`null` 表示空，`undefined` 未定义。

### 数组

js 的数组可以包括任意数据类型。

### 对象

js 的对象是一组由键-值组成的无序集合。

对象的键都是字符串类型。

### 变量

变量名可以是 `$`, `_` 以及英文字母、数字的组合。

### strict 模式

第一行写上 `'use strict';`

## 字符串

多行字符串，使用反引号 `` `...` ``。

### 模板字符串

使用 `+` 连接字符串，模板字符串 `` `${varname}` ``，要使用反引号。

### 操作字符串

字符串是不可变的。

`.length, toUpperCase, toLowerCase, indexOf, substring`

## 数组

js 的数组可以包含任意数据类型。

可以给 array.length 赋值，给超范围的索引赋值时数组也会增大。

- `slice` 对应 `substring`，都是左闭右开。
- `push` 和 `pop` 在末尾增删元素。
- `unshift` 和 `shift` 在头部增删元素。
- `sort` 排序，默认升序。
- `reverse` 翻转。
- `splice` 从指定索引开始删除若干元素，然后从该位置添加若干元素。
- `concat` 连接数组，返回新的 array。
- `join` 把数组元素用字符串连起来。

## 对象

js 的对象由若干键值对组成，键就是字符串。

- 可以用 `.` 或 `[]` 访问。
- 使用 `in` 操作符判断对象是否拥有某一属性，对于继承得到的属性也会返回 `true`。
- 使用 `hasOwnProperty` 判断属性是否是自身拥有的。

## 条件判断

`null, undefined, 0, NaN` 和空字符串 `''` 视为 `false`。

## 循环

`for` 或 `for ... in` 循环，后者可以遍历对象的属性，数组的索引被视为属性。

`while` 和 `do ... while` 循环。

## Map 和 Set

js 的默认对象表示方式 `{}` 可以视为其他语言中的 `Map`，即一组键值对。

js 的对象的键必须是字符串，ES6 引入 Map，可以用其他类型作为键。用二维数组初始化 Map。

`set` 添加新的键值对，`get` 获取键对应的值，`delete` 删除键值。

Set 是键的集合，键不可重复。

## iterable

遍历 Map 和 Set 无法使用下标，ES6 引入 iterable 类型，可以使用 `for ... of` 循环遍历。

使用 iterable 内置的 `forEach` 方法，接收一个函数，会迭代调用这个函数。

- Array 的函数参数为 function(element, index, array)
- Set 的函数参数为 function(element, sameElement, set)
- Map 的函数参数为 function(value, key, map)