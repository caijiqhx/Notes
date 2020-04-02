# MkDocs 中文搜索

> - [MkDocs 中文搜索和图片放大](https://segmentfault.com/a/1190000018592279)

东西多了就需要搜索了，然后就发现 MkDocs 不支持中文搜索。。。当然，由于是改了 mkdocs 的代码，只适用于在自己的环境上部署，

## 添加中文搜索支持

`pip install jieba`，修改 `search_index.py` 中的 `generate_search_index` 函数：

```python tab="search_index.py"
 def generate_search_index(self):
        """python to json conversion"""
        page_dicts = {
            'docs': self._entries,
            'config': self.config
        }
        for doc in page_dicts['docs']: # 调用jieba的cut接口生成分词库，过滤重复词，过滤空格
            tokens = list(set([token.lower() for token in jieba.cut_for_search(doc['title'].replace('\n', ''), True)]))
            if '' in tokens:
                tokens.remove('')
            doc['title_tokens'] = tokens

            tokens = list(set([token.lower() for token in jieba.cut_for_search(doc['text'].replace('\n', ''), True)]))
            if '' in tokens:
                tokens.remove('')
            doc['text_tokens'] = tokens

        data = json.dumps(page_dicts, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

        if self.config['prebuild_index']:
            try:
                script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prebuild-index.js')
                p = subprocess.Popen(
                    ['node', script_path],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                idx, err = p.communicate(data.encode('utf-8'))
                if not err:
                    idx = idx.decode('utf-8') if hasattr(idx, 'decode') else idx
                    page_dicts['index'] = json.loads(idx)
                    data = json.dumps(page_dicts, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
                    log.debug('Pre-built search index created successfully.')
                else:
                    log.warning('Failed to pre-build search index. Error: {}'.format(err))
            except (OSError, IOError, ValueError) as e:
                log.warning('Failed to pre-build search index. Error: {}'.format(e))

```

```js tab="lunr.js"
// 仅替换前15行
lunr.Builder.prototype.add = function (doc, attributes) {
  var docRef = doc[this._ref],
      fields = Object.keys(this._fields)

  this._documents[docRef] = attributes || {}
  this.documentCount += 1

  for (var i = 0; i < fields.length; i++) {
    var fieldName = fields[i],
        extractor = this._fields[fieldName].extractor,
        field = extractor ? extractor(doc) : doc[fieldName],
        tokens = doc[fieldName + '_tokens'],
        terms = this.pipeline.run(tokens),
        fieldRef = new lunr.FieldRef (docRef, fieldName),
        fieldTerms = Object.create(null)

...

lunr.trimmer = function (token) {
  return token.update(function (s) {
    return s.replace(/^\s+/, '').replace(/\s+$/, '')
  })
}
```

