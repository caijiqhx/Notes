# 对象

## Object

对象用来存储键值对和更复杂实体。

- 使用 `.` 或 `[]` 获取对象的属性值。
- 属性名必须是字符串或 `Symbol`，其他类型自动转换为字符串。
- 保留关键字可以作为属性名。
- 使用 `in` 操作符检查属性是否存在。
- `for ... in` 循环，遍历对象的键。对象的整数属性（可转换为整数的字符串）会被排序，非整数属性会按照创建顺序排序。
- 与原始类型不同，对象通过引用存储和复制。
- 比较引用，`==` 和 `===` 只会在两个变量指向同一个对象时才为 `true`。
- 可以用 const 定义对象，const 修饰的只是对象，允许修改属性。
- 想要深拷贝一个对象，可以使用循环来复制所有属性值。
- 使用 `Object.assign(dest, [src1, src2, ...])` 来实现深拷贝，同名属性会被后面的覆盖。
- 对象的属性也可以是其他对象的引用，用 `assign` 复制时并不会深拷贝作为属性的对象。对于这种嵌套的深拷贝可以使用 `lodash` 的方法 `_.cloneDeep(obj)`。

## 垃圾回收

js 的内存管理是自动的。

### 可达性 Reachability

“可达”值即可访问或可用的值，一定存储在内存中。

1. 固有的可达值的集合，这些值不能被释放：

   - 当前函数的局部变量和参数。
   - 嵌套调用时，调用链上所有函数的变量与参数。
   - 全局变量。

    这些值称为根 roots。
2. 如果一个值可以通过引用或引用链从根访问任何其他值，则认为值是可达的。

js 中的垃圾回收器会删除不可达的变量，只有传入引用才可使对象可达。

### 内部算法

垃圾回收的基本算法成为 `mark-and-sweep`。定期执行以下的垃圾回收步骤：

1. 找到所有根，标记；
2. 遍历并标记来自它们的所有引用；
3. 遍历标记的对象并标记他们的引用，知道所有可达引用可被访问；
4. 没有被标记的对象会被删除。

## Symbol 类型

`Symbol` 类型表示唯一的标识符，使用 `Symbol()` 创建。可以传入一个字符串作为描述，描述可以重复。

- `Symbol` 允许我们创建对象的隐藏属性，代码的任何其他部分都不能意外访问或重写这些属性。并不是完全隐藏，还是有方法可以获取隐藏属性。
- `Symbol` 属性在 `for ... in` 中会被跳过。
- `Object.assign` 会同时复制 `Symbol` 属性。
- 全局 `Symbol` 注册表，可以通过描述获取已创建的符号，`Symbol.for()`。
- 通过 `Symbol.keyFor()` 获取全局符号的描述，对非全局不适用。

## this

函数可以作为对象属性，成为方法。在方法中访问对象的属性，可以使用 `this`。

- `this` 可以用于任何函数。
- `this` 值是代码运行时计算的，没有对象的情况下为 `undefined`。
- `this` 并不取决于方法声明的位置。
- `obj.method()` 的 `.` 返回的不是一个函数，而是一个特殊的引用，是三部分的集合：
    - `base`：对象本身。
    - `name`：属性值。
    - `strict`：严格模式下为真。

    通过 `()` 调用引用类型时，接收对象和方法信息，以设定正确的 `this`。
- 使用 `(expression).method()` 调用，等价于 `f = obj.method; f()`，赋值操作使得引用类型被丢弃，只获取一个函数的值，失去了 `this`。 
- 使用 `obj.method()` 或 `obj[method]()` 调用函数时，`this` 才能被正确传递。
- 箭头函数没有自己的 `this`，其 `this` 取决于外部正常的函数。

```js
// this 示例
function makeUser() {
  return {
    name: "John",
    ref: this
  };
};

let user = makeUser();

// makeUser()作为函数调用，未通过 . 符号，因此 this 为 undefined
alert( user.ref.name );     // error

function makeUser() {
  return {
    name: "John",
    ref() {
      return this;
    }
  };
};

let user = makeUser();

// user.ref() 是一个方法，this 为 user
alert( user.ref().name ); // John
```

## 对象 —— 原始值转换

- 对象在逻辑表达式中转换为 `true`；

可以使用特殊的对象方法，调整字符串和数值转换。

- 对象到字符串的转换，如 `alert(obj)`；
- 对象到数字的转换，数学运算中；
- 少数情况下，操作者不确定期望值的类型，如 `+` 可用于字符串连接和数字相加。

为了进行转换，js 会尝试查找并调用以下方法。

### Symbol.toPrimitive

名为 `Symbol.toPrimitive` 的内建 `Symbol`，用于给转换方法命令。

```js
// hint 是 string, number, default 中的一个
obj[Symbol.toPrimitive] = function(hint) {};

let user = {
  name: "John",
  money: 1000,

  [Symbol.toPrimitive](hint) {
    alert(`hint: ${hint}`);
    return hint == "string" ? `{name: "${this.name}"}` : this.money;
  }
};

alert(user); // hint: string -> {name: "John"}
alert(+user); // hint: number -> 1000
alert(user + 500); // hint: default -> 1500
```

单个方法处理了所有的转换情况。

### toString / valueOf

如果没有 `Symbol.toPrimitive` 属性，js 尝试 `toString` 或 `valueOf` 方法，方法必须返回原始值，返回对象会被忽略。

- 默认 `toString` 返回字符串 `"[object Object]"`。
- `valueOf` 返回对象本身。
- 如果没有 `valueOf`，`toString` 会处理所有原始转换。

以上转换方法并不一定返回对应 hint 类型的原始值，只是要求返回原始值。

## 构造函数和操作符 new

常规的语法允许创建一个对象，但我们经常需要创建许多类似的对象。

### 构造函数

- 命名以大写开头，只能由 `new` 操作符来执行。
- `new` 执行时，按照以下步骤：
    1. 创建一个空对象分配给 `this`；
    2. 函数体执行，通常会修改 `this`，添加属性；
    3. 返回 `this` 的值。
- 任何函数都可以通过 `new` 运行。
- 函数使用 `new.target` 属性检查是否被 `new` 调用，常规调用时为 `undefined`，`new` 调用时等于该函数。
- 构造函数的返回值如果是一个对象，则会返回这个对象，而不是 `this`，返回原始类型则忽略。
- 