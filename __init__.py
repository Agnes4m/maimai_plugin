from pathlib import Path
from nonebot import load_plugin

dir_ = Path(__file__).parent
load_plugin(str(dir_ / "nonebot_plugin_maimai"))