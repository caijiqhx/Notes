# QHX's Notes

菜鸡 qhx 的学习笔记。

## Material color palette 颜色主题

### Primary colors 主色

> 默认 `teal`

点击色块可更换主题的主色

<style>
  .md-typeset button[data-md-color-primary] {
    width: 6.5rem;
    margin-bottom: .2rem;
    padding: 1.2rem .4rem .2rem;
    -webkit-transition: background-color .25s,opacity .25s;
    transition: background-color .25s,opacity .25s;
    border-radius: .1rem;
    font-size: .64rem;
    color: #fff;
    text-align: left;
    cursor: pointer;
    cursor: pointer;
    transition: opacity 250ms;
  }
  .md-typeset button[data-md-color-primary]:hover {
    opacity: 0.75;
  }
  .md-typeset button[data-md-color-primary] {
    display: inline-block;
    color: var(--md-primary-bg-color);
    background-color: var(--md-primary-fg-color);
  }
</style>

<button data-md-color-primary="red">Red</button>
<button data-md-color-primary="pink">Pink</button>
<button data-md-color-primary="purple">Purple</button>
<button data-md-color-primary="deep-purple">Deep Purple</button>
<button data-md-color-primary="indigo">Indigo</button>
<button data-md-color-primary="blue">Blue</button>
<button data-md-color-primary="light-blue">Light Blue</button>
<button data-md-color-primary="cyan">Cyan</button>
<button data-md-color-primary="teal">Teal</button>
<button data-md-color-primary="green">Green</button>
<button data-md-color-primary="light-green">Light Green</button>
<button data-md-color-primary="lime">Lime</button>
<button data-md-color-primary="yellow">Yellow</button>
<button data-md-color-primary="amber">Amber</button>
<button data-md-color-primary="orange">Orange</button>
<button data-md-color-primary="deep-orange">Deep Orange</button>
<button data-md-color-primary="brown">Brown</button>
<button data-md-color-primary="grey">Grey</button>
<button data-md-color-primary="blue-grey">Blue Grey</button>
<button data-md-color-primary="black">Black</button>

<script>
  var buttons = document.querySelectorAll("button[data-md-color-primary]");
  Array.prototype.forEach.call(buttons, function(button) {
    button.addEventListener("click", function() {
      document.body.dataset.mdColorPrimary = this.dataset.mdColorPrimary;
      localStorage.setItem("data-md-color-primary",this.dataset.mdColorPrimary);
    })
  })
</script>

### Accent colors 辅助色

> 默认 `red`

点击色块更换主题的辅助色

<style>
  .md-typeset button[data-md-color-accent] {
    cursor: pointer;
    transition: opacity 250ms;
    width: 6.5rem;
    margin-bottom: .2rem;
    padding: 1.2rem .4rem .2rem;
    -webkit-transition: background-color .25s,opacity .25s;
    transition: background-color .25s,opacity .25s;
    border-radius: .1rem;
    color: #fff;
    font-size: .64rem;
    text-align: left;
    cursor: pointer;
  }
  .md-typeset button[data-md-color-accent]:hover {
    opacity: 0.75;
  }
  .md-typeset button[data-md-color-accent]   {
    display: inline-block;
    color: black;
    background-color: var(--md-accent-fg-color);
  }
</style>

<button data-md-color-accent="red">Red</button>
<button data-md-color-accent="pink">Pink</button>
<button data-md-color-accent="purple">Purple</button>
<button data-md-color-accent="deep-purple">Deep Purple</button>
<button data-md-color-accent="indigo">Indigo</button>
<button data-md-color-accent="blue">Blue</button>
<button data-md-color-accent="light-blue">Light Blue</button>
<button data-md-color-accent="cyan">Cyan</button>
<button data-md-color-accent="teal">Teal</button>
<button data-md-color-accent="green">Green</button>
<button data-md-color-accent="light-green">Light Green</button>
<button data-md-color-accent="lime">Lime</button>
<button data-md-color-accent="yellow">Yellow</button>
<button data-md-color-accent="amber">Amber</button>
<button data-md-color-accent="orange">Orange</button>
<button data-md-color-accent="deep-orange">Deep Orange</button>
<button data-md-color-accent="black">Black</button>

<script>
  var buttons = document.querySelectorAll("button[data-md-color-accent]");
  Array.prototype.forEach.call(buttons, function(button) {
    button.addEventListener("click", function() {
      document.body.dataset.mdColorAccent = this.dataset.mdColorAccent;
      localStorage.setItem("data-md-color-accent",this.dataset.mdColorAccent);
    })
  })
</script>
