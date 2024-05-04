import re
import tomllib
import dataclasses
from pathlib import Path
from loguru import logger

from size import MONITOR_HEIGHT

SETTINGS_PATH = Path(f"./settings.toml")


@dataclasses.dataclass
class BaseSettings:
    log_level: str
    debug: bool

    classAbilityBind: str # 职业技能按键
    unchargedMeleeBind: str # 未充能近战按键
    shadowdiveBind: str # 跳隐身按键
    finishedBind: str # 终结技按键
    emoteBind: str # 埋头表情按键


@dataclasses.dataclass
class Config:
    bossOnScreenCoords: tuple[int]
    leftRotationDuration: float
    postRotationDuration: float

    adOnScreenCoord: tuple[int]
    adSpawnWaitDuration: float

    cameraEmotePerpectiveOne: tuple[int]
    persepectiveDurationOne: float

    cameraEmotePerpectiveTwo: tuple[int]
    persepectiveDurationTwo: float


settings = tomllib.loads(SETTINGS_PATH.read_text("utf-8"))
base_settings = BaseSettings(**settings.pop("base"))
monitor_settings = Config(**settings.pop(f"{MONITOR_HEIGHT}p"))
