# Manjaro 从头配置

## 设置源

`sudo pacman-mirrors -i -c China -m rank`

在弹出窗口中选择源即可。

还需要添加 `ArchLinuxCN` 的源，在 `/etc/pacman.conf` 文件结尾添加一下内容：

```
[archlinuxcn]
SigLevel = Optional TrustedOnly
Server = https://mirrors.ustc.edu.cn/archlinuxcn/$arch
```

设置源后更新缓存并导入密钥链：

`sudo pacman -Syy && sudo pacman -S archlinuxcn-keyring`

更新系统：

`sudo pacman -Syyu`

## 字体

思源黑体 CN：

`sudo pacman -S noto-fonts-cjk adobe-source-han-sans-cn-fonts adobe-source-han-serif-cn-fonts`

## 中文输入法

`sudo pacman -S fcitx-googlepinyin fcitx-im fcitx-configtool`

在 `~/.xprofile` 文件中写入：

```
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS="@im=fcitx"
```

重启之后就可以配置输入法了。

## 终端 & shell

安装 `deepin-terminal`：

`sudo pacman -S deepin-terminal`

安装 `zsh` 和 `ohmyzsh`：

```shell
sudo pacman -S zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
chsh -s /bin/zsh
```

`~/.zshrc` 文件配置：

```
ZSH_THEME="ys"
alias s='source ~/.zshrc'
alias cls='clear'
```

## 通用文件夹设置为英文

先转成英文强制更新目录然后转回中文

```shell
export LANG=en_US.utf-8
xdg-user-dirs-update --force
export LANG=zh_CN.utf-8
```

## 常用软件安装

AUR 管理工具：`sudo pacman -S yay yaourt`

deb 包安装工具：`yay -S debtap && sudo debtap -u`

## pacman autoremove

`sudo pacman -R $(pacman -Qdtq)`