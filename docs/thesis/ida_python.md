# IDA python 代码阅读

## `build_add_section.py`

### 依赖

```python
from idaapi import *	# 底层数据
import idautils 		# IDA 的高级实用函数
#import pandas as pd
import struct
import lief
import pefile
```

### 函数

1. `create_pe()`
2. `instrument(origin_op, origin_address)`
3. `build_section_data(x, y, flag) -> string`
4. `insert_section(length, data)`

下面分析各个函数：

#### `create_pe`

```python
def create_pe():

    text_start = text_end = 0
    # 找到代码段
    for seg in Segments():
        if idc.SegName(seg)==".text":
            text_start=idc.SegStart(seg)
            text_end=idc.SegEnd(seg)
    # 遍历函数
    for func in idautils.Functions():
        start_address = func
        end_address = idc.FindFuncEnd(func)
        #print hex(start_address)
        # Heads: Get a list of heads (instructions or data items)
        # 遍历函数中的指令
        for each_step in idautils.Heads(start_address, end_address):
            #print hex(each_step)
            op = idc.GetDisasm(each_step)
            if each_step >= text_start and each_step <text_end:
                instrument(op,each_step)

    section_data = ''
    for index in range(len(ori_op)):
        section_data += build_section_data(args0[index],args1[index],args2[index])

    section_file = open('newSectionData','wb')
    section_file.write(section_data)
    section_file.close()
    section_size = len(section_data)
    insert_section(len(section_data),section_data)

    #ref = pd.DataFrame({'addr':ori_address,"ins":ori_op,'args0':args0,'args1':args1,'length':ori_length})
    #ref.to_csv('ref.txt',index=0)
```

就是找到代码段，遍历函数，对每一条指令都执行 `instrument`。

#### `instrument`

```python
# 传入参数为指令及其地址
def instrument(origin_op, origin_address):
    if origin_op.startswith('call'):
    	#return
        # GetOpType 获取操作数类型
        # o_void:0, o_reg:1, o_mem:2, o_phrase:3
        # o_displ:4, o_imm:5, o_far:6, o_near:7
        #if idc.GetOpType(origin_address, 0) == 1 and idc.GetOpType(origin_address, 1) == 5:
        if 1==1:
        	#print hex(origin_address)
            op_length=idaapi.decode_insn(origin_address)
            #print hex(origin_address)
            #return
            # 对应 FF 15 类型的 call 指令
            if op_length == 6 : 
                #print hex(origin_address)
                #return
                ori_op.append(origin_op)
                ori_address.append(hex(origin_address))
                # 下一条指令地址
                args0.append(origin_address + 6)
                #print origin_address + 5
                jump_add = (idc.Dword(origin_address+2))
                # 跳转地址
                args1.append(jump_add)
                #print jump_add
                #print "--------"
                print "ori_address:",hex(origin_address),"call6"
                args2.append('call6')

                #args1.append(int(idc.Dword(origin_address+1)))
                #call address
            # E8 类型的 call
            if op_length == 5 : 
                #print hex(origin_address)
                #return
                ori_op.append(origin_op)
                ori_address.append(hex(origin_address))
                args0.append(origin_address + 5)
                #print origin_address + 5
                # 跳转目的地址 = 跳转偏移 + 指令长度 + 指令地址
                jump_add = (idc.Dword(origin_address+1) + 5 + origin_address) & 0xffffffff
                args1.append(jump_add)
                #print jump_add
                #print "--------"
                print "ori_address:",hex(origin_address),"call5"
                args2.append('call5')

                #args1.append(int(idc.Dword(origin_address+1)))
                #call address
    if origin_op.startswith('mov'):
        # mov reg, imm
        if idc.GetOpType(origin_address, 0) == 1 and idc.GetOpType(origin_address, 1) == 5:

        	#print hex(origin_address)
            op_length=idaapi.decode_insn(origin_address)
            if op_length != 5: return
            ori_op.append(origin_op)
            ori_address.append(hex(origin_address))
            # 跟 call 不同，需要填入指令长度
            ori_length.append(op_length)
            # 寄存器操作数
            args0.append(idc.GetOpnd(origin_address,0))
            # 立即数操作数
            args1.append(int(idc.Dword(origin_address+1)))
            args2.append('mov')
            print "ori_address:",hex(origin_address),"mov"
            #call address
    if origin_op.startswith('jz'):
    	#sreturn
        #if idc.GetOpType(origin_address, 0) == 1 and idc.GetOpType(origin_address, 1) == 5:
        if 1==1:
        	#print hex(origin_address)
            op_length=idaapi.decode_insn(origin_address)
            #print hex(origin_address)
            #return
            if op_length != 6: return
            #print hex(origin_address)
            #return
            ori_op.append(origin_op)
            ori_address.append(hex(origin_address))
         	# 下一条指令
            args0.append(origin_address + 6)
            #print origin_address + 6
            # 跳转目的地址 = 跳转偏移 + 指令长度 + 指令地址
            jump_add = (idc.Dword(origin_address+2) + 6 + origin_address)&0xffffffff
            args1.append(jump_add)
            #print jump_add
            #print "--------"
            args2.append('jz')
            print "ori_address:",hex(origin_address),"jz"
```

可见该函数的作用就是对传入的指令分类处理，填入全局数组。

- `ori_op`：指令；
- `ori_address`：地址；
- `ori_length`：指令长度；
- `args0`：第一个参数，对  `call, jz` 指令是下一条指令地址，对  `mov` 指令是寄存器操作数；
- `args1`：第二个参数，对 `call, jz` 是跳转的目的地址，`mov` 是立即数；
- `args2`：指令类型，有 `call6, call5, mov, jz` 几种。

这些数据都填完后，对每条指令调用 `build_section_data` 构造数据。

#### `build_section_data`

```python
# 传入参数为 args0, args1, args2
def build_section_data(x,y,flag):
    '''
    push = '\x68' 
    #print args1
    
    tmp = struct.pack("I", args1)
    print args1,'pack:',tmp
    pop = POP_DIC[args0]
    print args0,pop
    retn = '\xc3'
    return push+tmp+pop+retn    
    '''
    if flag == 'call5':
		# push retn_address
        # jmp target_address
        ins1 = '\x68'
        ret = struct.pack("I", x)
        ins2 = '\xe9' #jmp
        target = struct.pack("I", y)
        return ins1+ret+ins2+target
    if flag == 'call6':
        # push retn_address
        # push target_address
        ins1 = '\x68'
        ret = struct.pack("I", x)
        ins2 = '\xff\x25' # a type of jmp
        target = struct.pack("I", y)
        return ins1+ret+ins2+target
    if flag == 'mov':
        # push imm
        # pop reg
        # retn
        push = '\x68' 
        #print args1   
        tmp = struct.pack("I", y)
        #print args1,'pack:',tmp
        pop = POP_DIC[x]
        #print args0,pop
        retn = '\xc3'
        return push+tmp+pop+retn    

    if flag == 'jz':
        ins1 = "\x50"     #push eax
        ins2 = "\x51"     #push ecx
        ins3 = "\x9f"     #lahf
        ins4 = "\x50"     #push eax
        ins5 = "\xb1\x0e" #mov cl, 6+8
        ins6 = "\xd3\xe8" #shr eax,cl
        ins7 = "\x83\xe0\x01" #and eax,1
    
        ins8 = "\x69\xc0" + struct.pack("I", (y-x) & 0xffffffff) #struct.pack("I", y-x)imul eax,y-x
        ins9 = "\x05" + struct.pack("I", x & 0xffffffff) # add eax, x
        ins10 = "\x89\x44\x24\x0c"
        ins11 = "\x58"	# pop eax
        ins12 = "\x9e"	# sahf
        ins13 = "\x59"	# pop ecx
        ins14 = "\x58"	# pop eax
        ins15 = "\xc3"	# retn
        return ins1+ins2+ins3+ins4+ins5+ins6+ins7+ins8+ins9+ins10+ins11+ins12+ins13+ins14+ins15
```

根据传入的指令类型和参数，构造对应的替换指令。之后要做的就是把指令插入到对应的位置。

#### `insert_section`

```python
# 构造的数据及其长度
def insert_section(length, data):
    global NEW_SECTION_ADDRESS
    bin = lief.parse(INPUT_PE)
    pe = pefile.PE(INPUT_PE)
    section = lief.PE.Section('.test')
    section.virtual_address = ((
        (pe.sections[-1].VirtualAddress +
         (pe.sections[-1].Misc_VirtualSize) - 1) / 0x1000 + 1) * 0x1000)

    NEW_SECTION_ADDRESS = section.virtual_address
    tmp = open("section_address", 'w')
    tmp.write(str(NEW_SECTION_ADDRESS))
    tmp.close()
    section.virtual_size = section.size = length
    section.offset = (((pe.sections[-1].PointerToRawData +
                        (pe.sections[-1].SizeOfRawData) - 1) / 0x200 + 1) *
                      0x200)
    section.characteristics = 0x60000020
    insert_data = []
    for each in data:
        insert_data.append(ord(each))
    section.content = insert_data
    #set random address closed
    bin.optional_header.dll_characteristics = bin.optional_header.dll_characteristics & 0xffbf

    bin.add_section(section)
    bin.write(INPUT_PE + ".crafted.call")
```

将构造的替换指令插入到新建的区块 `.test` 中。

## `recover_env.py`

上个文件是构建新区块，这个就是修改原代码段中对应的区块，让他们跳转到这里。