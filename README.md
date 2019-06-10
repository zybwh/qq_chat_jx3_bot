# 神小隐
深感糖小果没什么太多用处，于是花了2天时间写了个神小隐，添加了更多的趣味聊天功能，做一个真正的剑三云玩家。

本插件依赖 酷Q https://cqp.cc/ 

旧版本 1.x 基于 python sdk https://cqp.cc/t/27497 （2.7版本）编写，非常的古老但是简单。

新版本 2.x 基于 nonebot https://github.com/richardchien/nonebot 编写，比较复杂但是强大。

旧版本没有stress testing，可能在多个群使用时会比较慢。遇到这种情况你就少开几个群就好了。

新版本可以支持多个coolq端连接，而且基于asyncio，所以理论上在处理大批量数据的时候会更强

写的比较垃圾，以后会慢慢改进，看有没有时间吧。

插件开源@MIT_LICENSE，欢迎大家改进。如果有什么功能需求请raise issue。有时间尽量做，当然你要是想自己写也可以。

最后推广一下：
剑三中恶小帮 神隐@乾坤一掷

# 使用
1.x版本：开启coolq开发者模式，把python_sdk下内容复制进coolq/app即可。

2.x版本：需要设置nonebot，参考：https://none.rclab.tk/guide/installation.html

需要安装nonebot scheduler，pip install "nonebot[scheduler]"

需要安装bs4，pip install bs4

然后python bot.py 即可。
