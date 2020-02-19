## Docker

使用 Docker 作为环境部署工具。

> Docker 快速入门
>
> - [Docker 官方文档](https://docs.docker.com/)
> - [菜鸟教程](https://www.runoob.com/docker/docker-tutorial.html)
> - [Docker 从入门到实践](https://yeasy.gitbooks.io/docker_practice/content/)

### 什么是 Docker

Docker 是一个开源的应用容器引擎，可以让开发者打包他们的应用以及依赖包到一个轻量级、可移植的容器中，然后发布到任何流行的 Linux 机器上，也可以实现虚拟化。

Docker 是一个用于开发、交付和运行应用程序的开放平台。

- 快速、一致地交付你的应用程序

    Docker 允许开发使用你提供的应用程序或服务的本地容器在标准化环境中工作，从而简化了开发的生命周期。容器非常适合持续集成和持续交付的工作流程。

- 响应式部署和扩展

    Docker 是基于容器的平台，允许高度可移植的工作负载。

- 在同一硬件上允许更多工作负载

    Docker 轻巧快速，为基于虚拟机管理程序的虚拟机提供了可行、经济、高效的替代方案。Docker 非常适合于高密度环境以及中小型部署，可以用更少的资源做更多的事。

### Docker 架构

Docker 包括三个基本概念：

- 镜像 Image：Docker 镜像，相当于是一个 root 文件系统。
- 容器 Container：镜像和容器的关系，就像是面向对象中类和实例一样，容器是镜像运行时的实体。容器可以被创建、启动、停止、删除、暂停等。
- 仓库 Repository：仓库可看成一个代码控制中心，用来保存镜像。

Docker 使用 C/S 架构模式，使用远程 API 来管理和创建 Docker 容器。

- Docker daemon 守护进程：侦听 Docker API 请求并管理 Docker 对象。
- Docker client 客户端：通过命令行等工具与 Docker 守护进程通信。

### Docker 安装

**设置仓库**

更新包索引，安装 https 依赖包，添加官方 GPG 密钥，设置稳定版仓库

```shell
$ apt update
$ apt install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
$ apt-key fingerprint 0EBFCD88
pub   rsa4096 2017-02-22 [SCEA]
      9DC8 5822 9FC7 DD38 854A  E2D8 8D81 803C 0EBF CD88
uid           [ unknown] Docker Release (CE deb) <docker@docker.com>
sub   rsa4096 2017-02-22 [S]
$ add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
```

要注意的是 `add-apt-repository` 其实在 `/etc/apt/sources.list` 文件中添加一项。`lsb_release -cs` 返回 ubuntu 发行版的名称。

**安装 Docker Engine-Community**

```shell
$ apt-get install docker-ce docker-ce-cli containerd.io
$ docker run hello-world
```

Windows 下载 [Docker Desktop](https://docs.docker.com/docker-for-windows/install/) 安装即可。

**添加国内源**

linux 在 `/etc/docker/daemon.json` 文件中添加：

```json
{
    "registry-mirrors":[
        "https://registry.docker-cn.com", 
        "http://hub-mirror.c.163.com", 
        "https://docker.mirrors.ustc.edu.cn"
    ]
}
```

Windows 打开 Docker Settings 添加国内源即可。

### Docker 常用命令

| command                           | function                                                           |
| --------------------------------- | ------------------------------------------------------------------ |
| `docker`                          | 查看 Docker 客户端的所有命令选项                                   |
| `docker COMMAND --help`           | 查看对应命令的使用方法                                             |
| `docker pull ubuntu`              | 获取 ubuntu 镜像                                                   |
| `docker run -it ubuntu /bin/bash` | 以命令行模式进入容器 </br> -i：交互式操作 </br> -t：终端           |
| `docker ps -a`                    | 查看所有容器                                                       |
| `docker start`                    | 启动一个已停止的容器                                               |
| `docker stop`                     | 停止容器                                                           |
| `docker restart `                 | 重启容器                                                           |
| `docker attach`                   | 进入容器的终端，退出会导致容器停止                                 |
| `docker exec`                     | 容器执行命令，退出不会导致容器停止                                 |
| `docker export`                   | 导出本地某个容器                                                   |
| `docker import`                   | 从快照文件导入镜像                                                 |
| `docker rm`                       | 删除容器                                                           |
| `docker search`                   | 搜索镜像                                                           |
| `docker rmi`                      | 删除镜像                                                           |
| `docker commit`                   | 提交修改的容器副本 </br> -m：提交的描述信息 </br> -a：指定镜像作者 |
| `docker build -t <Image> <DIR>`   | 从 `<DIR>` Dockerfile 构建镜像 </br> -t 指定镜像名，               |

### Docker 容器连接

网络端口映射

- `-P` 容器内部端口随机映射到主机的高端口
- `-p` 将容器内部端口映射到指定的主机端口

容器互联，允许多个容器连接在一起，共享连接信息。 Docker 连接会创建一个父子关系，父容器可以看到子容器的信息。

- `docker network create -d bridge test-net` 创建一个新的 docker 网络，`-d` 选项指定网络类型，包括 bridge、overlay
- `docker run -itd --name test --network test-net ubuntu /bin/bash` 创建容器添加到网络，容器间能够 ping 通，证明建立了互联关系。

### Docker 仓库管理

Docker 官方维护了公共仓库 DockerHub，可以通过 `docker login` 命令登录。登录后，可以使用 `docker push` 命令将自己的镜像推送到 DockerHub，之后可以使用 `docker search` 搜索镜像或直接用 `docker pull` 拉取镜像。