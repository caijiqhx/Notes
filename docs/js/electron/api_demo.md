# Electron API Demo

> - [electron api demos](https://github.com/electron/electron-api-demos)

感觉 electron 的入门做的挺不错的，学习官网提供的 API demos。

## 主进程和渲染进程

`package.json` 中指定的 `main` 脚本的进程成为主进程，主进程中运行的脚本通过创建 web 页面来展示用户界面。一个 electron 应用总是有且只有一个主进程。

每个 electron 中的 web 页面运行在它自己的渲染进程中。主进程使用 `BrowserWindos` 实例创建页面。每个实例都在自己的渲染进程里运行页面，实例销毁后，相应的渲染进程也会被终止。

主进程管理所有的 web 页面和它们对应的渲染进程。每个渲染进程都是独立的，它只关心它所运行的 web 页面。

```js
// main.js
const { BrowserWindow } = require('electron');

const win = new BrowserWindow();

// render.js
const { remote } = require('electron');
const { BrowserWindow } = remote;

const win = new BrowserWindow();
```

electron 同时对主进程和渲染进程暴露了 nodejs 的接口，可以使用 nodejs 的API，以及 npm 模块。

## Create and Manage Windows

### Create a New Window

```js
// render.js
const { BrowserWindow } = require("electron").remote;
const path = require("path");

const newWindowBtn = document.getElementById("new-window");

newWindowBtn.addEventListener("click", event => {
  let win = new BrowserWindow({ width: 400, height: 320 });
  const modalPath = path.join(__dirname, "./modal.html");
  win.on("close", () => {
    win = null;
  });
  win.loadURL(modalPath);
  win.show();
});
```

### Manage Window State

可以通过 `win.on(event, func(){})` 来监听窗口事件，如 `resize`, `move`, `close` 等。