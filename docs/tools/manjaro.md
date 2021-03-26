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

```shell
sudo pacman -S ttf-roboto noto-fonts ttf-dejavu
# 文泉驿
sudo pacman -S wqy-bitmapfont wqy-microhei wqy-microhei-lite wqy-zenhei
# 思源字体
sudo pacman -S noto-fonts-cjk adobe-source-han-sans-cn-fonts adobe-source-han-serif-cn-fonts
```

对比了一下感觉文泉驿的等宽微米黑比较好用。

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

`ohmyzsh` 手动更新：

```shell
proxychains ~/.oh-my-zsh/tools/upgrade.sh
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

## 多屏幕显示

先通过 `xrandr` 命令得到屏幕的名字，例如这样

```shell
$ xrandr
Screen 0: minimum 8 x 8, current 3840 x 1080, maximum 32767 x 32767
eDP1 connected primary 1920x1080+0+0 (normal left inverted right x axis y axis) 290mm x 170mm
   1920x1080     60.02*+  59.93  
   1680x1050     59.88    60.00  
   ...
DP1 disconnected (normal left inverted right x axis y axis)
HDMI1 connected 1920x1080+1920+0 (normal left inverted right x axis y axis) 530mm x 290mm
   1024x768      60.00 +
   1920x1080     60.00*   59.94  
   ...
HDMI2 disconnected (normal left inverted right x axis y axis)
VIRTUAL1 disconnected (normal left inverted right x axis y axis)
```

得到主屏幕 `eDP1` 和 外接屏幕 `HDMI1`，然后执行 `xrandr --output eDP1 --left-of HDMI1` 实现左右屏幕拼接扩展显示。

## QQ & WeChat 

字体调整 `env WINEPREFIX="$HOME/.deepinwine/Deepin-WeChat" winecfg`

## Firefox 字体

不爱用 manjaro 的最大原因就是在 chrome 用不了（代理问题）的情况下 Firefox 的字体太小了。。。终于找到了解决方案。

地址栏输入 `about:config` 进入配置界面，搜索 `layout.css.devPixelsPerPx`，默认 tmd 竟然是 -1，这是要折磨死我，修改为 1.25 左右就差不多了。

## 双系统时间差 8 小时

`sudo timedatectl set-local-rtc true`

## KDE 配置 Meta 绑定程序菜单

[KDE userbase](https://userbase.kde.org/Plasma/Tips#Windows.2FMeta_Key)

Open “Start Menu” with Windows/Meta key

Feature has been added by default since Plasma 5.8.
1. If it's not working, make sure your "Start Menu" widget has a global shortcut like Alt+F1 set (you can't assign it directly to Meta, but it will open with Meta if another shortcut is assigned).
2. Right Click the KDE Icon → Application Menu Settings
3. Keyboard Shortcuts Tab → Shortcut: Alt+F1

- Latte Dock: If you're using Latte Dock, you will need to run the following commands mentioned in it's Wiki.

```shell
kwriteconfig5 --file ~/.config/kwinrc --group ModifierOnlyShortcuts --key Meta "org.kde.lattedock,/Latte,org.kde.LatteDock,activateLauncherMenu"
qdbus org.kde.KWin /KWin reconfigure
```

