# Gitbook

## gitbook 自动生成 summary

gitbook 用的不多，今天想把一个带哥的文章在本地部署，但是太多了，写 `mkdocs.yml` 太麻烦，搜了一下找到了一个自动生成 gitbook 的 `summary.md` 的工具（虽然其实好像就写个目录扫描，但还是懒得写。

```shell
npm install -g gitbook-summary
book sm
```

生成之后直接 `gitbook serve` 就行了，真方便。