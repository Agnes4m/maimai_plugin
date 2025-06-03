<!-- markdownlint-disable MD024 MD026 MD031 MD033 MD036 MD041 MD052 -->
<div align="center">
  <img src="https://raw.githubusercontent.com/Agnes4m/nonebot_plugin_l4d2_server/main/image/logo.png" width="180" height="180" alt="NoneBotPluginLogo">
  <br>
  <p><img src="https://s2.loli.net/2022/06/16/xsVUGRrkbn1ljTD.png" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot_plugin_maimai

_✨maimaiDX，nonebot2插件版本✨_

<a href="https://github.com/Umamusume-Agnes-Digital/nonebot_plugin_maimai/stargazers">
        <img alt="GitHub stars" src="https://img.shields.io/github/stars/Umamusume-Agnes-Digital/nonebot_plugin_maimai" alt="stars">
</a>
<a href="https://github.com/Umamusume-Agnes-Digital/nonebot_plugin_maimai/issues">
        <img alt="GitHub issues" src="https://img.shields.io/github/issues/Umamusume-Agnes-Digital/nonebot_plugin_maimai" alt="issues">
</a>
<a href="https://jq.qq.com/?_wv=1027&k=l82tMuPG">
        <img src="https://img.shields.io/badge/QQ%E7%BE%A4-424506063-orange?style=flat-square" alt="QQ Chat Group">
</a>
    <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
    <img src="https://img.shields.io/badge/nonebot-2.0.0-red.svg" alt="NoneBot">
</div>

## 说明（已更新图片素材）

从[mai-bot](https://github.com/Diving-Fish/mai-bot)适配nonebot2插件，测试环境nonebot2.1.0

修改部分：

- b40/b50可以艾特人查询
- static文件可以放maimai插件文件夹中，或机器人路径下/data/maimai/static
- （可循）env设置 `maimai_font`,是str对象的`字体`
- 新增指令检查mai资源可以初始化下载，或者强制检查mai资源强制下载覆盖

我做的适配有问题请冲我来不要打扰原作者捏，可以提iss或者[加群qq](https://jq.qq.com/?_wv=1027&k=l82tMuPG)反馈,

## env(可选)

        maimai_font = 'simsun.ttc'  # 替换你有的字体

## 前置步骤（和原项目一样）

安装（仍选其一）:

    pip3 install nonebot_plugin_maimai
    nb plugin install nonebot_plugin_maimai
    git clone https://github.com/Agnes4m/nonebot_plugin_maimai.git

您需要从[此链接](https://www.diving-fish.com/maibot/static.zip)下载资源文件并，并将其static文件解压到:(以下方法2选1)

- pypi`nonebot_plugin_maimai`文件夹中 - 最终路径类似是/path/to/nonebot_plugin_maimai/static
- 机器人目录下 - 最终路径类似是/path/to/data/maimai/static中。其中bot.py文件在/path/to位置

> 资源文件仅供学习交流使用，请自觉在下载 24 小时内删除资源文件。

## FAQ

配置 nonebot 或 cq-http 过程中出错？
> 请查阅 <https://github.com/nonebot/nonebot2> 以及 <https://github.com/Mrs4s/go-cqhttp> 中的文档。

部分消息发不出来？
> 被风控了。解决方式：换号或者让这个号保持登陆状态和一定的聊天频率，持续一段时间。

## 说明

本 bot 提供了如下功能：

命令 | 功能
--- | ---
help | 查看帮助文档
今日舞萌 | 查看今天的舞萌运势
XXXmaimaiXXX什么 | 随机一首歌
随个[dx/标准][绿黄红紫白]<难度> | 随机一首指定条件的乐曲
查歌<乐曲标题的一部分> | 查询符合条件的乐曲
[绿黄红紫白]id<歌曲编号> | 查询乐曲信息或谱面信息
定数查歌 <定数> <br> 定数查歌 <定数下限> <定数上限> |  查询定数对应的乐曲
分数线 <难度+歌曲id> <分数线> | 展示歌曲的分数线
搜<手元><理论><谱面确认> | 从b站获取对应的手元视频

## 原作者

[Diving-Fish](https://github.com/Diving-Fish),感谢大佬为音游人的无私奉献

## License

MIT

您可以自由使用本项目的代码用于商业或非商业的用途，但必须附带 MIT 授权协议。
