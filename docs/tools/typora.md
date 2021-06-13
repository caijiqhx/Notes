# Typora

> 使用 Typora 的一些问题

### Typora 导出 pdf 页边距

Typora 导出 pdf 页边距太大，可以通过 CSS 配置文件设置。

参考 [Export PDF or print support page option · Issue #998 · typora/typora-issues (github.com)](https://github.com/typora/typora-issues/issues/998)

```css
@media print {
    html {
        font-size: 14px!important;
        padding: 0 !important;
        margin: 0 !important;
    }
    body.typora-export {
        padding: 0 !important;
        margin: 0 !important;
    }
    .typora-export #write {
        padding: 0 !important;
        margin-top: -2mm !important;
        margin-right: 0mm !important;
        margin-bottom: -2mm !important;
        margin-left: 0mm !important;
    }
}
```

把以上代码复制到 *themes* 下的 *base.user.css* 文件，就会对所有主题适用。 

### Typora 导出 pdf 页眉页脚

更新到 `0.10.10(beta)` 之后，偏好设置中新增了导出各种格式的配置。