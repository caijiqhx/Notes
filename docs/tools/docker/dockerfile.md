## Dockerfile

Dockerfile 是一个用来构造镜像的文本文件，包含了构建镜像所需的指令和说明。上下文通常是一个本地文件路径，目录下的所有文件都会被打包发送到守护程序，因此一般目录中仅存放 Dockerfile 以及构建所需的文件。也可以通过创建 `.dockerignore` 文件排除文件和目录。Dockerfile 的位置默认在上下文路径中，也可以通过 `-f` 选项单独指定 Dockerfile 的位置。

### Dockerfile 指令

#### FROM

指定构建的基础镜像

- `[--platform=<platform>]`：指定镜像的平台。
- `[AS <name>]`：指定镜像名。

#### RUN

用于执行后面的命令行命令

- `RUN <command>`：相当于在 shell 中运行。
- `RUN ["executable", "param1", "param2"]`：运行指定的可执行文件。
    
RUN 指令将在当前镜像顶部的新层中执行所有指令，并提交结果，生成的提交镜像将用于下一步的 Dockerfile。因此一般将多行命令写在一个 RUN 后。

#### COPY
复制文件到容器内指定路径。
- `COPY <src> ... <dest>`
- `COPY ["src", ... "<dest>"]`：路径带空格就需要用这种。
- `[--chown=<user>:<group>]`：指定复制到容器内文件的拥有者和属组。
- `[--from=<name|index>]`：默认源路径是在上下文路径，此选项可以将源设置为先前构建阶段的镜像。具体可查看 [Dockerfile 多阶段构建](https://maichong.io/help/docker/dockerfile-multi-stage.html)。

源文件或目录，可以是通配符表达式，规则要满足 golang 的 [filepath.Match](http://golang.org/pkg/path/filepath/#Match) 规则。

对于目录，只复制内容而不包含自身。

#### ADD

命令格式与 COPY 相同。除了多阶段构建以外，可以完成 COPY 命令的所有功能。并且还可以完成两个功能：

- 解压压缩文件到镜像中，但是在不解压的前提下，无法复制压缩文件。
- 从 url 复制文件到镜像中，官方并不建议这样做，从 url 获取文件可以用 curl 或 wget 以减少镜像层数。

#### CMD

类似于 RUN 指令，只不过是在 `docker run` 阶段运行，仅最后一个 CMD 生效，且可以被 `docker run` 的命令行参数覆盖。

- `CMD ["<param1>", "<param2>", ...]`：为 ENTRYPOINT 指令指定的程序提供默认参数。

#### ENTRYPOINT

类似于 CMD 指令，`docker run` 的命令行参数会当作参数送给 ENTRYPOINT 指定的程序。仅最后一个 ENTRYPOINT 生效。可以使用 `--entrypoint` 选项覆盖。

CMD 与 ENTRYPOINT：

- Dockerfile 应至少指定 CMD 和 ENTRYPOINT 中的一个。
- 使用容器作为可执行文件时应定义 ENTRYPOINT。
- CMD 用于为 ENTRYPOINT 指定默认参数或使用容器执行临时命令。
- CMD 会被 `docker run` 的命令行参数覆盖。

#### ENV

设置环境变量，在后续的指令中使用。

- `ENV <key> <value>`
- `ENV <key1>=<value1> <key2>=<value2>`

#### ARG

构建参数，与 ENV 类似，但只在构建阶段有效，`docker build --build-arg <key>=<value>` 覆盖。

#### VOLUME

定义匿名数据卷，在启动容器时忘记挂在数据卷，会自动挂在到匿名卷。

在 `docker run` 命令中，可以通过 `-v <hostdir>:<dir>` 参数设置挂载点，`<hostdir>` 指定主机上的目录，`<dir>` 指定容器内的目录。

在 Dockerfile 中用 `VOLUME ["<dir1>", "<dir2>", ...]` 指定挂载点。

```shell
# in Dockerfile 
# VOLUME ["data1", "data2"]

docker build -t testimage .
docker run --name test1 -itd testimage /bin/bash

docker run --name test2 -itd --volumes-from test1 ubuntu /bin/bash
docker run --name test3 -itd --volumes-from test1 testimage /bin/bash
```

以上的例子，在 Dockerfile 中指定了两个挂载点并以此构建镜像 testimage。

test1 是基于 testimage 的容器，其中就有 /data1 和 /data2 两个挂载点。

`docker run` 使用 `--volumes-from` 指定来源于 test1 的共享卷，可以是来自不同镜像。

test1, test2, test3 均有 /data1, /data2 两个目录，且内容共享。

#### EXPOSE

`EXPOSE <port> [<port>/<protocol>]`

仅声明端口，未指定协议则默认为 TCP，`docker run -P` 使用随机端口映射时，会自动随机映射 EXPOSE 的端口。

#### WORKDIR

对以后的 RUN, CMD, ENTRYPOINT, COPY, ADD 等指令指定工作目录。多条 WORKDIR 时，使用相对路径则是相对于上一个 WORKDIR 的路径。

#### USER

用于指定后续命令的用户和用户组，用户必须已存在。

#### HEALTHCHECK

- `HEALTHCHECK [options] CMD <command>`：设置检查容器健康状况的命令。
- `HEALTHCHECK NONE`：禁用从基础镜像集成的任何健康检查指令。

容器启动初始状态为 starting，在健康检查成功后变为 healthy，连续一定次数失败则变为 unhealthy。HEALTHCHECK 支持以下选项：

- `--interbal=<time>`：健康检查的间隔，默认为 30s。
- `--timeout=<time>`：健康检查命令超时时间，默认为 30s。
- `--start-period=<time>`：为需要时间进行引导的容器提供了初始化时间，此期间检查失败不计入次数。
- `--retries=<times>`：连续失败指定次数后，容器状态变为 unhealthy，默认 3 次。

后面的命令和 CMD 的格式一行，返回 0 成功，1 失败，2 保留。命令在 stdout 和 stderr 上的任何输出都存储在健康状态里，可以使用 `docker inspect` 查看。

#### ONBUILD

用于延迟构建命令的执行，后面跟的是其他指令，在当前镜像构建时并不会被执行。只有当以当前镜像为基础镜像构建下一级镜像时才会执行。

`ONBUILD <COMMAND>`