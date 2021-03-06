# Vim tutorial

> [简明 VIM 练级攻略](https://coolshell.cn/articles/5426.html)

### 存活

- `i` -> insert 模式，`ESC` 回到 normal 模式
- `x` -> 删除当前光标所在的一个字符
- `:wq` -> 保存 + 退出， `:w` 后可跟文件名
- `dd` -> 删除当前行并存到剪贴板
- `p` -> 粘贴剪贴板
- `hjkl` -> 左下上右
- `:help <command>` -> 显示相关命令帮助

### 感觉良好

所有的命令都在 normal 模式下使用

#### 各种插入模式

- `a` -> 在光标后插入
- `o` -> 在当前行后插入一个新行
- `O` -> 在当前行前插入一个新行
- `cw` -> 替换从光标所在位置后到一个单词结尾的字符

#### 简单地移动光标

- `0` -> 到行头
- `^` -> 到本行第一个非 blank 字符的位置，即空格、tab、换行、回车等
- `$` -> 到本行行尾
- `g_` -> 到本行最后一个非 blank 字符的位置
- `/pattern` -> 搜索 pattern 的字符串，多个匹配使用 `n` 到下一个，`N` 到前一个

#### 拷贝/粘贴

- `P` -> 当前位置之前粘贴，`p` 则是当前位置之后粘贴
- `yy` -> 拷贝当前行，相当于 `ddp`

#### undo/redo

- `u` -> undo
- `<C-r>` -> redo

#### 打开/保存/退出/改变文件(Buffer)

- `:e <path/to/file>` -> 打开一个文件
- `:saveas <path/to/file>` -> 另存为
- `:x`,`ZZ` 或 `:wq` -> 保存并退出，`:x` 表示仅需要时保存
- `:q!` -> 退出不保存，`:qa!` 退出所有正在编辑的文件
- `:bn`, `:bp` -> 同时打开多个文件时，切换到下一个或上一个文件

### 更好，更强，更快 

#### Better

vim 是怎么重复自己的：

- `.` -> 重复上一次的命令
- `N<command>` -> 重复某个命令 N 次

以下示例：

> - `2dd` -> 删除两行
> - `3p` -> 粘贴文本 3 次
> - `100itest [ESC]` -> 会写 'test ' 100 次
> - `.` -> 重复上一个命令，写 100 次
> - `3.` -> 重复 3 次 'test '，而不是 300 次 （真·智能）

#### Stronger

光标移动更有效率

- `NG` -> 到第 N 行，另外可用 `:N` 到第 N 行
- `gg` -> 到第一行
- `G` -> 到最后一行
- 按单词移动
    - `w` -> 到下一个单词开头
    - `e` -> 到单词结尾
    - `W`, `E` -> 按照 blank 字符分隔，小写则默认单词由字母、数字和下划线组成。

程序员的最强光标移动

- `%` -> 括号匹配移动，包括 `( [ {`，光标需要在括号上
- `*` 和 `#` -> 匹配光标当前单词移动到下一个或上 一个

#### Faster

一定要记住光标的移动

`<start position><command><end position>`

- `0y$` 命令：
    - `0` -> 先到行头
    - `y` -> 拷贝
    - `$` -> 拷贝到本行最后一个字符

- `ye` -> 从当前位置拷贝到本单词的最后一个字符
- `y2/pattern` -> 拷贝 2 个 pattern 之间的字符串

### Vim 超能力

掌握前面的命令就可以很流畅地使用 vim，现在将介绍 vim 的杀手级命令，这些才是使用 vim 的原因。

#### 在当前行上移动光标：`0` `^` `$` `f` `F` `t` `T` `,` `;`

- `0` -> 到行头
- `^` -> 到本行第一个非 blank 字符
- `$` -> 到行尾
- `g_` -> 到本行最后一个非 blank 字符
- `fa` -> 到下一个为 a 的字符
- `t,` -> 到逗号前的第一个字符
- `3fa` -> 在当前行查找第 3 个出现的 a（试了一下，似乎是从当前位置出发）
- `F` 和 `T` 与小写类似，都是反方向
- `dt"` -> 删除所有内容，知道双引号

#### 区域选择 `<action>a<object>` 或 `<action>i<object>`

action 可以是任何命令，如 `d` `y` `v` 等。

object 可能是 `w` 单词，`W` blank 分隔的单词，`s` 句子，`p` 段落。也可以是特别的字符 `" ' ) } ]` 等。

假设有一个字符串 `(map (+) ("foo"))`，而光标在第一个 `o` 的位置：

```text
----------------- v2a)
 ~~~~~~~~~~~~~~~  v2i)
            *    
(map (+) ("foo"))
           ---    vi"
          +++++   va" and vi)
         =======  va)
```

#### 块操作 `<C-v>`

块操作，典型的操作：`0<C-v><C-d>I--[ESC]`
- `0` -> 到行头
- `<C-v>` -> 开始块操作
- `<C-d>` -> 向下移动，也可以使用 hjkl 等其他移动光标命令
- `I--[ESC]` -> I 是插入，插入 `--`，按 ESC 键来为每一行生效

Windows 下的 vim 需要使用 `<C-q>`。

#### 自动提示：`<C-n>` 和 `<C-p>`

在 insert 模式下，可以输入一个词的开头，然后按 `<C-n>` 或 `<C-p>`，自动补齐功能就出现了。

#### 宏录制：`qa`操作序列`q`, `@a`, `@@`

- `qa` -> 把操作序列记录在寄存器 a 中
- `@a` -> replay 被记录的宏
- `@@` -> replay 最新录制的宏

#### 可视化选择：`v`, `V`, `<C-v>`

- `V` -> 行选择模式

一旦选择完毕，可以做以下的事：
 
- `J` -> 将所有行连接在一起
- `<` 或 `>` -> 左右缩进
- `=` -> 自动缩进
 
在所有被选择的行后：
 
- `<C-v>`
- 选中相关的行（可使用 `j` 或 `<C-d>` 或 /pattern 或是 `%` 等）
- `$` -> 到行末
- `A`，输入字符串，`ESC`

#### 分屏：`:split` 和 `vsplit`

可以使用 `:help split` 查看 vim 的帮助。

- `:split` -> 创建分屏，`:vsplit` 创建垂直分屏
- `<C-w><dir>` -> `<dir>` 表示方向，可以是 `hjkl` 中的一个，用来切换分屏 
- `<C-w>_` 或 `<C-w>|` -> 最大化尺寸，分别应用于水平和垂直分屏
- `<C-w>+` 或 `<C-w>-` -> 缩放尺寸

### 结语

以上就是常用的 vim 命令，vim 的学习曲线很丧心病狂，学会之后，受益无穷。

运行 `vimtutor` 命令来熟悉基本命令，还可以仔细阅读 `:help usr_02.txt`，还会学习到诸如 `!`，目录，寄存器，插件等更多其他功能。