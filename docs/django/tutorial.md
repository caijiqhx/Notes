# Tutorial

通过这个教程，将带你创建一个基本的投票应用程序，由两部分组成：

- 一个让人们查看和投票的公共站点。
- 一个让你能添加、修改和删除投票的管理站点。

## 安装 Django

```zsh
$ python -m pip install Django
$ python -m Django --version
3.0.4
```

## 创建项目

```zsh
$ django-admin startproject mysite
$ tree mysite
mysite
├── manage.py       
└── mysite
    ├── __init__.py 
    ├── asgi.py     
    ├── settings.py 
    ├── urls.py     
    └── wsgi.py 

1 directory, 6 files
```

生成的目录和文件的用处：

- `manage.py`：管理 Django 项目的命令行工具，[详细信息](https://docs.djangoproject.com/zh-hans/3.0/ref/django-admin/)。
- `mysite/`：项目的 Python 模块包。
- `mysite/__init__.py`：空文件，告诉 Python 这个目录是一个 Python 模块。
- `mysite/settings.py`：项目的配置文件，[详细信息](https://docs.djangoproject.com/zh-hans/3.0/topics/settings/)。
- `mysite/urls.py`：项目的 URL 声明，[详细信息](https://docs.djangoproject.com/zh-hans/3.0/topics/http/urls/)。
- `mysite/asgi.py`：项目运行在 ASGI 兼容的 Web 服务器上的入口，[详细信息](https://docs.djangoproject.com/zh-hans/3.0/howto/deployment/asgi/)。
- `mysite/wsgi.py`：项目运行在 WSGI 兼容的 Web 服务器上的入口，[详细信息](https://docs.djangoproject.com/zh-hans/3.0/howto/deployment/wsgi/)。

## 用于开发的简易服务器

在外层的 mysite 目录中运行以下命令，启动 Django 自带的用于开发的简易服务器。

```zsh
$ python manage.py runserver [<port> 8000]
```

> 不要将这个服务器用于和生成环境相关的任何地方，这个服务器只是为了开发而设计。

## 创建投票应用

### 项目 vs 应用

app 是项目中完成具体功能的应用，项目是应用和配置的集合。

app 可以在任何地方，本教程中，将 app 放在 manage.py 同级目录下：

```zsh
$ python manage.py startapp polls
$ tree polls
polls
├── __init__.py
├── admin.py
├── apps.py
├── migrations
│   └── __init__.py
├── models.py
├── tests.py
└── views.py

1 directory, 7 files
```

## 编写第一个视图

```python tab="polls/views.py"
from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello world, this is the polls index.")
```

这是 Django 中最简单的视图，我们需要将一个 URL 映射到它。在 polls 目录下创建 `urls.py` 文件。

```python tab="polls/urls.py"
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
```

下面要在根 URLconf 文件中指定我们创建的 `polls.urls` 模块。

```python tab="mysite/urls.py"
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('polls/', include('polls.urls')),
    path('admin/', admin.site.urls),
]

```

`include()` 函数允许引用其他的 URLconfs，除了 `admin.site.urls` 的 URL 模式都应该使用 `include()`。

`path()` 函数有四个参数，后两个为可选参数：

- `route`：匹配 URL 的模式串，Django 响应一个请求时，它会从 urlpatterns 的第一项开始，按序依次匹配列表中的项，直到找到匹配的项。请求不会匹配 GET 和 POST 参数或域名。
- `view`：route 参数匹配的 URL 对应的 view 函数。
- `kwargs`：任意个关键字参数可以作为一个字典传递给目标视图函数。
- `name`：为你的 URL 取名能使你在 Django 的任意地方唯一地引用它，尤其是在模板中。这个有用的特性允许你只改一个文件就能全局地修改某个 URL 模式。

## 数据库配置

`mysite/settings.py` 包含了 Django 项目设置的 Python 模块。通常使用 SQLite 作为默认数据库。

可以通过 DATABASES 的 default 键值进行设置：

- `ENGINE`：可选值有 `django.db.backends.sqlite3, django.db.backends.postgresql, django.db.backends.mysql, django.db.backends.oracle`。
- `NAME`：数据库的名称，如果使用的是 SQLite，则是文件的绝对路径。
- 不适用 SQLite，则需要添加一些额外的设置，`USER, PASSWORD, HOST` 等，[详细信息](https://docs.djangoproject.com/zh-hans/3.0/ref/settings/#std:setting-DATABASES)。

`TIME_ZONE` 可用于设置时区。

文件中的 `INSTALLED_APPS` 项包括了在项目中启用的所有 Django 应用。默认包括了以下的自带应用：

- `django.contrib.admin`：管理员站点。
- `django.contrib.auth`：认证授权系统。
- `django.contrib.contenttypes`：内容类型框架。
- `django.contrib.sessions`：会话框架。
- `django.contrib.messages`：消息框架。
- `django.contrib.staticfiles`：管理静态文件的框架。

默认开启的应用需要至少一个数据表，所以在使用它们之前需要在数据库中创建一些表。

```zsh
$ python manage.py migrate
```

`migrate` 命令根据 `INSTALLED_APPS` 设置创建必需的数据库表。

## 创建模型



