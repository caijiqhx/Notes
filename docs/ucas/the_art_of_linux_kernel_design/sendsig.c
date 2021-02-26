#include <stdio.h>
int main(int argc, char **argv)
{
	int pid, ret, signo;
	int i;
	if (argc != 3)
	{
		printf("Usage: sendsig <signo> <pid>\n");
		return -1;
	}
	signo = atoi(argv[1]);
	pid = atoi(argv[2]);
	ret = kill(pid, signo); // 发送信号
	for (i = 0; i < 1000000;)
		if (ret != 0)
			printf("send signal error\n");
	return 0;
}
