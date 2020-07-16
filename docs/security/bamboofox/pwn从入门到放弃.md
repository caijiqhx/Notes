# Pwn 从入门到放弃

## Buffer Overflow

没有控制输入长度，导致内存空间被覆盖

`gcc start.c -fno-stack-protector -o start` 关闭 canary

 canary 绕过

- local variable
- stack migration
- ret2 series

 