from nonebot import get_driver, require

require("nonebot_plugin_alconna")

from nonebot.plugin import PluginMetadata, inherit_supported_adapters  # noqa: E402

from . import __main__ as __main__  # noqa: E402

driver = get_driver()

__version__ = "0.5.3"
__plugin_meta__ = PluginMetadata(
    name="舞萌DX成绩查询",
    description="水鱼自建服务器的改适配版本",
    usage="b50",
    config=None,
    type="application",
    homepage="https://github.com/Agnes4m/nonebot_plugin_l4d2_server",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={
        "version": __version__,
        "author": "Agnes4m <Z735803792@163.com>",
    },
)
