---

layout: post
title: Vim as your daily log notebook

---

There are probably hundreds of methods and software that have been written that can help you maintain a notebook that contains your daily logs and notes.

I have tried tens of methods and software and after a few days they just feel like bloat or take up too much time to maintain regularly.

So, I decided to break down my own problem and found a simplisitic method/solution that suits me. My need was to write two logs, one life log and one dev log which was distraction free and would not take more than a second to get started with.

I finally ended up with editing my `zshrc` and `vimrc`. Now, I just end up doing the following every morning:

1. Open the terminal `(ctrl + t)`
2. type `today` [This opens a split window having my life log and dev log side by side]
3. type `nlog<space>` to start a new log entry.

You can look at my commits [here](https://github.com/rhnvrm/dotfiles/commit/04a61fdb0a671e6de64f37730845b85fa7bf6109) and [here](https://github.com/rhnvrm/dotfiles/commit/81ebfa3f804032c8386d741232daa9744c54429c) to see how I have done it and modify it for yourself. 

