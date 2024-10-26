#include <stdio.h>
#include <signal.h>
void sig_usr(int signo)
{
	if (signo == SIGUSR1)
		printf("received SIGUSR1\n");
	else
		printf("received %d\n", signo);
	signal(SIGUSR1, sig_usr);
}

int main(int argc, char **argv)
{
	signal(SIGUSR1, sig_usr); // 挂接 processing 进程的信号处理函数指针
	for (;;)
		pause();
	return 0;
}
