#include<stdio.h>
#include<fcntl.h>
#include<sys/mman.h>
#include<linux/kvm.h>

int main() {
    struct kvm_sregs sregs;
    int ret;
    // 获取系统中 KVM 子系统的文件描述符 kvmfd
    int kvmfd = open("/dev/kvm", O_RDWR);
    // 获取 KVM 版本号，以便查看接口
    printf("%d\n", ioctl(kvmfd, KVM_GET_API_VERSION, NULL));
    // 创建一个虚拟机，返回一个虚拟机描述符 vmfd，可用于控制虚拟机的内存、VCPU 等
    int vmfd = ioctl(kvmfd, KVM_CREATE_VM, 0);
    // 虚拟机的物理内存对应 QEMU 的进程地址空间
    // 使用 mmap 系统调用分配 1 页内存
    unsigned char *ram = mmap(NULL, 0x1000, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    int kfd = open("test.bin", O_RDONLY);
    // 将内核代码加载到分配的内存
    read(kfd, ram, 4096);
    // 用分配的内存地址初始化对象
    struct kvm_userspace_memory_region mem = {
        .slot = 0,                              // 表示不同的内存空间
        .guest_phys_addr = 0,                   // 这段空间在虚拟机物理内存中的位置
        .memory_size = 0x1000,                  // 内存大小
        .userspace_addr = (unsigned long)ram,   // 物理空间对应宿主机的虚拟内存地址
    };
    // 为虚拟机指定了一个内存条
    ret = ioctl(vmfd, KVM_SET_USER_MEMORY_REGION, &mem);
    // 创建 VCPU
    int vcpufd = ioctl(vmfd, KVM_CREATE_VCPU, 0);
    // 每个 VCPU 都有一个 struct kvm_run 结构，用来在用户态 light-qemu 和内核态 KVM 共享数据
    int mmap_size = ioctl(kvmfd, KVM_GET_VCPU_MMAP_SIZE, NULL);
    // 映射到用户空间
    struct kvm_run *run = mmap(NULL, mmap_size, PROT_READ | PROT_WRITE, MAP_SHARED, vcpufd, 0);
    // 设置 VCPU 寄存器，段寄存器和控制寄存器放在 kvm_sregs，通用寄存器放在 kvm_regs
    ret = ioctl(vcpufd, KVM_GET_SREGS, &sregs);
    sregs.cs.base = 0;
    sregs.cs.selector = 0;
    ret = ioctl(vcpufd, KVM_SET_SREGS, &sregs);
    struct kvm_regs regs = {
        .rip = 0,
    };
    ret = ioctl(vcpufd, KVM_SET_REGS, &regs);
    // 一个简单的虚拟机和虚拟机 VCPU、内存都准备完毕，寄存器设置完成，可以运行了
    while(1) {
        // 对 vcpufd 调用 KVM_RUN，遇到敏感指令就会退出
        // 如果 KVM 不能处理就就会交给应用层软件处理
        // ioctl 返回，将一些信息保存在 kvm_run 中
        ret = ioctl(vcpufd, KVM_RUN, NULL);
        if(ret == -1) {
            printf("exit unknown\n");
            return -1;
        }
        switch (run->exit_reason)
        {
        case KVM_EXIT_HLT:
            puts("KVM_EXIT_HLT");
            return 0;
        case KVM_EXIT_IO:
            putchar(*(((char*)run) + run->io.data_offset));
            break;
        case KVM_EXIT_FAIL_ENTRY:
            puts("entry error");
            return -1;
        default:
            puts("other error");
            printf("exit_reason: %d\n", run->exit_reason);
            return -1;
        }
    }

}