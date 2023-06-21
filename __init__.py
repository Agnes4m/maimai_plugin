from pathlib import Path
from nonebot import require, load_plugins

dir_ = Path(__file__).parent
require('nonebot-plugin-htmlrender')
load_plugins(str(dir_ / "nonebot_plugin_maimai"))