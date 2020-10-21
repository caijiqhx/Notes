# Tmux

所有快捷键都要通过前缀键  `Ctrl+b` 唤起。


| Command/Shortcut     | Description     |
| ---- | ---- |
| 会话管理 |  |
| `tmux new -s <session_name>`     | 新建会话，默认从 0 开始编号 |
| `tmux detach` / `Ctrl+b d` | 分离会话 |
| `tmux list-session/ls` / `Ctrl+b s` | 查看所有会话 |
| `tmux attach -t <session_name>` | 接入会话 |
| `tmux kill-session -t <session_name>` | 杀死会话 |
| `tmux switch -t <session_name>` | 切换会话 |
| `tmux rename-session -t <old> <new>` / `Ctrl+b $` | 重命名会话 |
| pane 管理 |  |
| `tmux split-window` / `Ctrl+b "` | 划分上下两个 pane |
| `tmux split-window -h` / `Ctrl+b %` | 划分左右两个 pane |
| `tmux select-pane -U/D/L/R` / `Ctrl+b <arrow_key>` | 光标切换到上下左右 pane |
| `tmux swap-pane -U/D` | 当前 pane 上移下移 |
| `Ctrl+b ;/o` | 光标切换到上一个/下一个pane |
| `Ctrl+b {/}` | 当前 pane 与上一个/下一个交换 |
| `Ctrl+b Ctrl+o/Atrl+o` | 所有 pane 向前/后移动一个位置 |
| `Ctrl+b x` | 关闭当前 pane |
| `Ctrl+b !` | 将当前 pane 拆分成一个独立窗口 |
| `Ctrl+b z` | 当前 pane 全屏显示/恢复 |
| `Ctrl+b Ctrl+<arrow_key>` | 按箭头方向调整 pane 大小 |
| `Ctrl+b q` | 显示 pane 编号 |
| 窗口管理 |  |
| `tmux new-window -n <window_name>` / `Ctrl+b c` | 创建新窗口 |
| `tmux select-window -t <window_name>` | 切换到窗口 |
| `tmux rename-window <new_name>` / `Ctrl+b ,` | 重命名当前窗口 |
| `Ctrl+b p/n` | 切换到上一个/下一个窗口 |
| `Ctrl+b number` | 切换到指定编号的窗口 |
|  |  |
| `tmux list-keys` | 列出所有快捷键及对应命令 |
| `tmux list-commands` | 列出所有命令及其参数 |
| `tmux info` | 列出所有会话信息 |
| `tmux source-file ~/.tmux.conf` | 加载配置 |
