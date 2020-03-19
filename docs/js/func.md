# 函数

## 函数定义

js 中函数定义方式如下：

```js
function <func_name>([parameter, ..]) {
    // function
    return
}

let res = function ([parameter, ..]) {
    return 
}
```

`arguments` 关键字，参数列表的数组。

`rest` 参数，未声明的参数数组。

## 变量作用域与解构赋值

`var` 或 `let` 声明的变量是有作用域的。

### 变量提升

函数定义会扫描函数体的语句，把所有声明的变量提升到顶部，但是不提升赋值。所以最好在函数体头部声明所有变量。

### 全局作用域

js 有一个默认的全局对象 `window`，全局的变量实际上被绑定到 `window` 的一个属性。

函数也是 `window` 对象。

### 名字空间

全局变量绑定到 `window` 上，不同的 js 文件如果使用了相同的全局变量，或定义了同名函数，会造成命名冲突。

减少冲突的一个方法就是把自己的所有变量和函数都绑定到一个全局变量中。

```js
let my_namespace = {};

my_namespace.name = 'my_namespace';
my_namespace.version = 1.0;

my_namespace.foo = function() { }
```

### 局部作用域

js 的变量作用域实际是函数内部，在 for 循环等语句块中无法定义具有局部作用域的变量。

为了解决块级作用域，ES6 引入关键字 `let`，用 `let` 代替 `var` 可以声明块级作用域的变量。

### 常量

`const` 定义常量，同样具有块级作用域。

### 解构赋值

解构赋值对一组变量进行赋值。

```js
let [x, [y, z]]] = [1, [2, 3]]; // x:1, y:2, z:3
let [, , z] = [1, 2, 3];        // z:3
```

从对象中提取若干属性，也可以使用解构赋值。还可以直接对嵌套的对象属性进行赋值，保持层次一致即可。如果变量名和属性值不一致，可以使用 `:` 赋值给变量。支持默认值，以避免不存在的属性返回 `undefined`。

```js hl_lines='12'
let person = {
    name: 'qhx',
    age: 20,
    gender: 'male',
    passport: 'G-12345678',
    address: {
        city: 'tianjin'
    }
};
// 这里 address 不是变量名，而是表示嵌套的 address 对象
// id 是属性 passport 对应的变量名
let {name, age = 10, passport:id, address:{city}} = person;
```

如果变量已被声明，再次解构赋值时报错

```js
let x, y;
let a = {
    x : 1,
    y : 2
};
{x, y} = a;     // 报错
({x, y} = a);   // x:1, y:2
```

解构赋值可以简化代码，如交换变量 `[x, y] = [y, x]`。

函数接收对象作为参数，可以解构直接把对象的属性绑定到变量：

```js
function buildDate({year, month, day, hour=0, minute=0, second=0}) {
    return new Date(year + '-' + month + '-' + day + ' ' + hour + ':' + minute + ':' + second);
}
```

## 方法

对象中绑定函数，称为对象的方法。使用 `this` 获取当前对象的属性。

要保证 `this` 指向正确，应该用 `obj.func()` 的形式调用。

ECMA 让 strict 模式下的 `this` 默认为 `undefined`，当方法内嵌函数时应该先获取 `this`，然后才能在内嵌中使用：

```js
var test = {
    name: 'qhx',
    birth: 1998,
    age: function () {
        var that = this; // 在方法内部一开始就捕获this
        function getAgeFromBirth() {
            var y = new Date().getFullYear();
            return y - that.birth; // 用that而不是this
        }
        return getAgeFromBirth();
    }
};

test.age();
```

`this` 的指向并非不可修改：

- `apply` 方法，第一个参数就是需要绑定的 `this`，第二个参数是函数的参数列表。
- `call` 方法与 `apply` 类似，要将参数按序传入。

### 装饰器

利用 `apply` 可以动态改变函数行为。

比如统计函数调用次数，可以使用新的函数替换默认函数：

```js
var count = 0;
var oldParseInt = parseInt; // 保存原函数

window.parseInt = function () {
    count += 1;
    return oldParseInt.apply(null, arguments); // 调用原函数
};
```

## 高阶函数

Higher-order function

js 的函数都指向某个变量，那么函数就可以作为另一个函数的参数，称为高阶函数。

### map/reduce

`map` 方法定义在数组中，调用 `map` 方法传入自定义的函数，就可以返回新的数组：

```js
function pow(x) {
    return x * x;
}
let arr = [1, 2, 3, 4];
let res = arr.map(pow);
// res : 1, 4, 9, 16
```

`reduce` 要求传入的函数接收两个参数：

```js
[x1, x2, x3, x4].reduce(f) = f(f(f(x1, x2), x3), x4)
```

### filter

`filter` 用于把数组中某些元素过滤掉，返回剩下的元素。接收一个函数，通过返回值判断是保留还是丢弃。

`filter` 接收的回调函数可以有多个参数，即 `element, index, self`，可以巧妙地去重：

```js
let arr = [1, 2, 2, 3, 4, 5];
let res = arr.filter(function (element, index, self) {
    return self.indexOf(element) === index;
});
```

### sort

`sort` 默认把元素转换为字符串再排序。可以接收一个比较函数自定义排序。

`sort` 方法会直接对数组修改。

### 数组的高阶函数

除了以上的 `map, reduce, filter, sort`，数组还提供了很多使用的高阶函数。

- `every`：判断数组中所有元素是否满足条件。
- `find`：找到符合条件的第一个元素，未找到返回 `undefined`。
- `findIndex`：返回第一个符合条件元素的下标，没找到返回 -1。
- `forEach`，与 `map` 类似，每个元素一次作用于传入的函数，但不会返回新数组。

## 闭包

高阶函数除了可以接收函数参数，还可以把函数作为返回值。

内部函数可以引用外部函数的参数和局部变量，内部函数作为返回值时，相关参数和变量都保存在返回的函数中，称为闭包。

```js
function count() {
    var arr = [];
    for (var i=1; i<=3; i++) {
        arr.push(function () {
            return i * i;
        });
    }
    return arr;
}

var results = count();
var f1 = results[0];
var f2 = results[1];
var f3 = results[2];
```

当运行时，三个函数的结果都是 16，因为它们都引用了变量 i，但没有立即执行。等到 3 个函数返回时，它们引用的变量 i 已经变成了 4。

这里是因为 `var` 声明的变量不具有块级作用域，循环遍历作用域在整个函数之内。我们可以用 `let` 声明变量解决这个问题。

或者创建一个匿名函数立即执行：

```js
(function (n) {
    return function () {
        return n * n;
    }
})(i);
```

> 廖雪峰网站这个教程看到这我就不想再往下看了，因为它并没有提到用 let 解决这个问题，用 let 能解决是我在尝试的时候偶然发现的。这个教程似乎很久没更新了。。。因此，到此为止。

