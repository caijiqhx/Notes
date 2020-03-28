# SQL

## 基础

模式定义了数据如何存储、存储什么样的数据以及数据如何分解等信息，数据库和表都有模式。

主键的值不允许修改，也不允许复用（不能将已删除的主键值赋给新数据行的主键），

SQL：Structured Query Language

SQL 语句不区分大小写，但数据库表明、列名和值是否区分依赖于具体的 DBMS。

支持三种注释：`#, --, /**/`。

数据库创建与使用：

```mysql
create database test;
use test;
```

## 创建表

```mysql
create table mytable (
   	# int 不可空，自增
	id int not null auto_increment,
    # int 不可控，默认为 1
    col1 int not null default 1,
    # 变长字符串，最长 45 字符，可为空
    col2 varchar(45) null,
    # 日期类型，可空
    col3 date null,
    primary key (`id`));
```

## 修改表

```mysql
# 添加列
alter table mytable
add col char(20);
# 删除列
alter table mytable
drop column col;
# 删除表
drop table mytable;
```

## 插入

```mysql
# 普通插入
insert into mytable(col1, col2)
values(val1, val2);
# 插入检索出来的数据
insert into mytable1(col1, col2)
select col1, col2
from mytable2;
# 将一个表的内容插入到一个新表
create table newtable as
select * from mytable;
```

## 更新

```mysql
update mytable
set col = val
where id = 1;
```

## 删除

```mysql
delete from mytable
where id = 1;
# 清空表
truncate table mytable;
```

使用更新和删除一定要有 where，不然会破坏整张表，可以先用 select 测试。

## 查询

### DISTINCT

相同的值只会出现一次，作用于所有列，所有列值相同才算相同。

```mysql
select distinct col1, col2
from mytable;
```

### LIMIT

限制返回的行数，可以有两个参数：起始行、总行数。

```mysql
# 返回前 5 行
select *
from mytable
limit 0, 5; -- 0 可省略
# 返回 3 ~ 5 行
select *
from mytable
limit 2, 3;
```

## 排序

ASC 升序，默认；DESC 降序。

可以按多个列排序，且每个列指定不同的排序方式。

```mysql
select *
from mytable
order by col1 DESC, col2 ASC;
```

## 过滤

where 子句可用的操作符：

`=, <, >, <>, !=, <=, !>, >=, !<, between, is null`

- and 和 or 连接多个过滤条件；
- in 操作符用于匹配一组值，可以接 select 子句；
- not 操作符用于否定一个条件。

## 通配符

也是用于过滤，仅限文本字符。

- `%` 匹配任意字符；
- `_` 匹配 1 个任意字符；
- `[]` 匹配集合内的字符，可用 `^` 进行否定。

使用 like 进行通配符匹配：

```mysql
select *
from mytable
where col like '[^AB]%';
```

## 计算字段

使用 `as` 取别名：

```mysql
select col1 * col2 as alias
from mytable;
```

`concat()` 用于连接两个字段：

```mysql
select concat(trim(col1), '(', trim(col2), ')') as concat_col
from mytable;
```

## 函数

介绍 MySQL 的主要函数。

### 汇总

| 函数      | 说明                   |
| --------- | ---------------------- |
| `avg()`   | 列均值，会忽略 null 行 |
| `count()` | 列行数                 |
| `max()`   | 列最大                 |
| `min()`   | 列最小                 |
| `sum()`   | 列之和                 |

可使用 distinct 汇总不同的值。

### 文本处理

| 函数        | 说明         |
| ----------- | ------------ |
| `left()`    | 左侧子串     |
| `right()`   | 右侧子串     |
| `lower()`   | 转小写       |
| `upper()`   | 转大写       |
| `ltrim()`   | 去左空格     |
| `rtrim()`   | 去右空格     |
| `length()`  | 长度         |
| `soundex()` | 转换为语音值 |

### 日期和时间处理

- 日期格式：`YYYY-MM-DD`
- 时间格式：`HH:MM:SS`

| 函 数         | 说 明                          |
| ------------- | ------------------------------ |
| `ADDDATE()`   | 增加一个日期（天、周等）       |
| `ADDTIME()`     | 增加一个时间（时、分等）       |
| `CURDATE()`     | 返回当前日期                   |
| `CURTIME()`     | 返回当前时间                   |
| `DATE()`        | 返回日期时间的日期部分         |
| `DATEDIFF()`    | 计算两个日期之差               |
| `DATE_ADD()`    | 高度灵活的日期运算函数         |
| `DATE_FORMAT()` | 返回一个格式化的日期或时间串   |
| `DAY()`         | 返回一个日期的天数部分         |
| `DAYOFWEEK()`   | 对于一个日期，返回对应的星期几 |
| `HOUR()`        | 返回一个时间的小时部分         |
| `MINUTE()`      | 返回一个时间的分钟部分         |
| `MONTH()`       | 返回一个日期的月份部分         |
| `NOW()`         | 返回当前日期和时间             |
| `SECOND()`      | 返回一个时间的秒部分           |
| `TIME()`       | 返回一个日期时间的时间部分     |
| `YEAR()`        | 返回一个日期的年份部分         |

### 数值处理

| 函数   | 说明   |
| ------ | ------ |
| `SIN()`  | 正弦   |
| `COS()`  | 余弦   |
| `TAN()`  | 正切   |
| `ABS()`  | 绝对值 |
| `SQRT()` | 平方根 |
| `MOD()`  | 余数   |
| `EXP()`  | 指数   |
| `PI()`   | 圆周率 |
| `RAND()` | 随机数 |

## 分组

把具有相同的数据值的行放在同一组，对同一分组使用汇总函数处理。

按指定字段分组并排序。

```mysql
# order by 可根据汇总字段排序
select col, count(*) as num
from mytable
group by col
order by num;
# where 过滤行，having 过滤分组，行过滤应优先
select col, count(*) as num
from mytable
where col > 2
group by col
having num >= 2
```

分组规定：

- group by 子句出现在 where 之后，order by 之前；
- 除了汇总字段外，select 字段语句中每一字段都必须在 group by 子句中给出；
- null 的行会单独成为一组；
- 大多数 SQL 实现不支持 group by 列具有可变长度的数据类型。

## 子查询

子查询只能返回一个字段的数据。子查询结果可作为 where 子句的过滤条件：

```mysql
select *
from mytable1
where col1 in (select col2
              from mytable2);
# 检索客户的订单数量，子查询语句会对第一个查询检索出的每个客户执行依次：
select cust_name, (select count(*)
                   from Orders
                   where Orders.cust_id = Customers.cust_id)
                   as orders_num
from Customers
order by cust_name;
```

## 连接

连接用于连接多个表，使用 join 关键字，条件语句用 on 而不是 where。

连续可以替换子查询，并且比子查询效率高。

可以用 as 给列名、计算字段和表名取别名，给表名取别名是为了简化 SQL 语句以及连接相同表。

### 内连接

内连接，又称等值连接，使用 inner join 关键字。

```mysql
select A.value, B.value
from tablea as A inner join tableb as B
on A.key = B.key;
```

可以不明确使用 inner join，而是使用普通查询并在 where 中将两个表要连接的列用等值方式连接：

```mysql
select A.value, B.value
from tablea as A, tableb as B
where A.key = B.key;
```

### 自连接

```mysql
# 子查询
select name
from employee
where department = (
	select department
	from employee
	where name = "Jim");
# 自连接
select e1.name
from employee as e1 inner join employee as e2
on e1.department = e2.department
	and e2.name = "Jim";
```

### 外连接

外连接保留了没有关联的行，分为左外连接，右外连接以及全外连接，左外连接就是保存左表没有关联的行。

```mysql
# 检索所有顾客的订单信息，包括没有订单的顾客
select Customers.cust_id, Orders.order_num
from Customers left outer join Orders
on Customers.cust_id = Orders.cust_id;
```

## 组合查询

使用 union 来组合两个查询，每个查询必须包含相同的列、表达式和聚集函数。

默认去除相同行，保留使用 union all。

只能包含一个 order by 语句，且放在最后。

```mysql
select col
from mytable
where col = 1
union
select col 
from mytable
where col = 2;
```

## 视图

视图是虚拟的表，本身不包含数据，不能对其进行索引操作。

对视图的操作和对普通表的操作一样。

- 简化复杂的 SQL 操作，比如复杂的连接。
- 只使用实际表的一部分数据。
- 通过只给用户访问视图的权限，保证数据的安全性。
- 更改数据格式和表示。

```mysql
create view myview as
select concat(col1, col2) as concat_col, col3 * col4 as compute_col
from mytable
where col5 = val;
```

## 存储过程

存储过程可以看成是对一系列 SQL 操作的批处理。

- 使用存储过程的好处：代码封装，安全性、代码复用、预先编译，高性能。
- 命令行中创建存储过程需要自定义分隔符，否则会把存储过程中包含的分号作为结束符。
- 包含了 in、out 和 inout 三种参数，给变量赋值使用 select into，每次只能对一个变量赋值。

```mysql
delimiter //
create procedure myprocedure(out ret int)
	begin
		declare y int;
		select sum(col1)
		from mytable
		into y;
		select y * y into ret;
	end //
delimiter ;

call myprocedure(@ret);
select @ret;
```

## 游标

存储过程中使用游标可以对一个结果集进行移动遍历。

主要用于交互式应用，用户需要对数据集中的任意行进行浏览和修改。

使用步骤：声明游标、打开游标、取出数据、关闭游标

```mysql
delimiter //
create procedure myprocedure(out ret int)
	begin
		declare done boolean default 0;
		# 声明游标，此时没有实际检索数据
		declare mycursor cursor for
		select col1 from mytable;
		# 定义一个 continue handler，当 sqlstate ‘02000‘ 条件出现时，执行 set done
		declare continue handler for sqlstate '02000' set done = 1;
		# 打开游标
		open mycursor;
		# 取数据
		repeat
			fetch mycursor into ret;
			select ret;
		until done end repeat;
		# 关闭游标
		close mycursor;
	end //
delimiter ;
```

## 触发器

触发器会在某个表执行 delete、insert、update 时自动执行。

触发器必须指定在语句执行之前还是之后执行，before 用于数据验证和净化，after 用于审计跟踪，将修改记录到另一张表中。

- insert 触发器包含一个 NEW 虚拟表；
- delete 触发器包含一个 OLD 虚拟表，只读；
- update 触发器包含 NEW 和 OLD 虚拟表，NEW 可修改，OLD 只读。

MySQL 不允许在触发器中使用 call 语句，不能调用存储过程。

```mysql
create trigger mytrigger after insert on mytable
for each row select NEW.col into @result;
```

## 事务管理

- 事务 (transaction)：指一组 SQL 语句；
- 回退 (rollback)：指撤销指定的 SQL 语句的过程；
- 提交 (commit)：指将未存储的 SQL 语句结果写入数据库表；
- 保留点 (savepoint)：指事务处理中设置的临时占位符，可对其发布回退，与回退整个事务不同。

不能回退 select、create 和 drop 语句。

MySQL 默认是隐式提交，每执行一条语句就把这条语句当成一个事务然后提交。当出现 start transaction 语句时关闭隐式提交。当 commit 或 rollback 执行后，事务会自动关闭，重新恢复隐式提交。

设置 autocommit 为 0 可取消自动提交，仅针对每个连接而不是服务器的设置。

如果没有设置保留点，rollback 会回退到 start transaction 语句处；如果设置了保留点，且在 rollback 中指定该保留点，则会回退到该保留点。

```mysql
start transaction
...
savepoint delete1
...
rollback to delete1
...
commit
```

## 字符集

- 字符集表示字母和符号的集合；
- 编码为某个字符集成员的内部表示；
- 校对字符指定如何进行比较，主要用于排序和分组。

```mysql
create table mytable (
    # 还可以给列指定字符集和校对
	col varchar(10) character set latin collate latin1_general_ci)
default character set hebrew collate hebrew_general_ci;
# 可以在排序、分组时指定校对
select *
from mytable
order by col collate latin1_general_ci;
```

## 权限管理

MySQL 的账户信息保存在 mysql 库中。

```mysql
# 创建账户，新账户没有任何权限
create user myuser identified by 'mypassword';
# 修改账户名
rename user myuser to newuser;
# 删除账户
drop user myuser;
# 查看权限
show grants for myuser;
# 授予权限，账户以 username@host 形式定义
grant select, insert on mydatabase.* to myuser;
# 回收权限
revoke select, insert on mydatabase.* to myuser;
# 更改密码
set password for myuser = Password('new_password');
```

删除权限，grant 和 revoke 可以在几个层次控制访问权限：

- 整个服务器，使用 grant all 和 revoke all；
- 整个数据库，使用 on database.\*；
- 特定表，使用 on database.table；
- 特定的列；
- 特定的存储过程。