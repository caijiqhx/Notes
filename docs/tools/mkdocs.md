## MkDocs

使用 MkDocs 作为文档生成工具。

> MkDocs 快速入门
> 
> - [MkDocs 官网](https://www.mkdocs.org/)
> - [中文手册](https://markdown-docs-zh.readthedocs.io/zh_CN/latest/)
> - [material 主题](https://squidfunk.github.io/mkdocs-material/)

### 安装

MkDocs 支持 python 2.7, 3.4, 3.5, 3.6, 3.7。

```zsh
$ pip install mkdocs
```

### 开始

初始化一个新项目：

```zsh
$ mkdocs new my-project
$ tree my-project
my-project
├── docs
│   └── index.md
└── mkdocs.yml

1 directory, 2 files
```

创建的项目中有：配置文件 `mkdocs.yml`，文档源码文件夹 `docs`。

部署到本地，在配置文件目录下执行：

```zsh
$ mkdocs serve
INFO    -  Building documentation... 
INFO    -  Cleaning site directory 
[I 200128 15:50:12 server:296] Serving on http://127.0.0.1:8000
[I 200128 15:50:12 handlers:62] Start watching changes 
[I 200128 15:50:12 handlers:64] Start detecting changes
```

可以使用 `--dev-addr ip:port` 指定部署的 ip 和端口。

### 配置文件

```yml
site_name: My Docs
nav:
- Home: index.md

theme: readthedocs
```

### 站点生成

使用命令生成文档：

```zsh
$ mkdocs build
```

命令创建了 `site` 目录，文档发布时可以直接将静态页面部署到任意地方。

### 配置主题

安装 `mkdocs-material` 主题

```zsh
$ pip install mkdocs-material
```

在配置文件中添加：

```yaml
theme:
    name: 'material'
    language: 'zh'
    palette:
        primary: teal
        accent: red
    feature:
        tabs: true 
    font:
        text: 'Noto Sans'
        code: 'Source Code Pro'
```
