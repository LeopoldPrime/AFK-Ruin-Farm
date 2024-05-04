import time
from pathlib import Path
from loguru import logger

X_SIMILARITY_CHECK_INTERVAL = 4
BOSS_HP_BAR_CHECK_INTERVAL = 0.5


def run():
    from pydirectinput import press
    from screenshot import (
        get_x_similarity,
        get_boss_hp_bar_mask_ratio,
        get_finish_hp_bar_mask_ratio,
        get_normal_hp_bar_mask_ratio,
    )
    from directx import (
        kick_boss_by_indebted_kindess,
        start_next_round,
        refresh_checkpoint,
        hide_indebted_kindess,
    )
    from settings import base_settings, monitor_settings

    logger.add("./logs/d2-ruin-farm_{time}.log", level=base_settings.log_level)
    logger.info(base_settings)
    logger.info(monitor_settings)

    start_count = 0
    finish_count = 0
    success_count = 0
    continuous_fail_count = 0
    need_refresh_checkpoint = False

    logger.info("Script Started")

    if base_settings.debug:
        logger.info("Debug Mode Enabled")
        Path("./debug").mkdir(exist_ok=True)

    time.sleep(2)

    while True:
        while True:
            x_similarity = get_x_similarity()
            if x_similarity > 0.9:
                logger.info("Shadowdive Ready To Use")
                break
            time.sleep(X_SIMILARITY_CHECK_INTERVAL)

        if continuous_fail_count >= 30:
            logger.info("Script reached maximum failure threshold, please restart script")
            start_next_round()
            need_refresh_checkpoint = True
            continuous_fail_count = 0
            continue

        if need_refresh_checkpoint:
            refresh_checkpoint()
            need_refresh_checkpoint = False
            continue

        logger.info(
            f"start_count: {start_count}, finish_count: {finish_count}, success_count: {success_count}"
        )
        start_count += 1

        kick_boss_by_indebted_kindess()
        time.sleep(0.1)

        hp_bar_mask_ratio = get_finish_hp_bar_mask_ratio()

        if not hp_bar_mask_ratio >= 0.8:
            continuous_fail_count += 1
            logger.info("Overshield not active, wiping to retry")

            press(base_settings.classAbilityBind)
            time.sleep(1.5)
            press(base_settings.unchargedMeleeBind)
            time.sleep(10)

            continue

        finish_count += 1
        logger.info("Overshield activated successfully")

        start_time = time.monotonic()

        # 躲起来等待boss血条消失
        time.sleep(2)
        hide_indebted_kindess()

        while True:
            if time.monotonic() - start_time >= 25:
                continuous_fail_count += 1
                logger.info("Reached maximum waiting period for boss healthbar to disappear, wiping to retry")

                press(base_settings.unchargedMeleeBind)
                time.sleep(10)

                break

            boss_hp_bar_mask_ratio = get_boss_hp_bar_mask_ratio()

            # 如果boss血条消失，进行玩家血条的检测
            if boss_hp_bar_mask_ratio <= 0.1:
                logger.info("Boss healthbar has disappeared")

                normal_hp_bar_mask_ratio = get_normal_hp_bar_mask_ratio()

                # 如果再检测到玩家血条，说明正常结算
                if normal_hp_bar_mask_ratio >= 0.8:
                    success_count += 1
                    continuous_fail_count = 0
                    need_refresh_checkpoint = True
                    logger.success("Player healthbar has been detected, boss has been defeated. Reloading dungeon")

                    time.sleep(2)
                    start_next_round()

                    break
                # 如果没有检测到玩家血条，说明灭了
                else:
                    logger.info("Player healthbar has not been detected, wiping to retry")
                    continuous_fail_count += 1
                    break

            time.sleep(BOSS_HP_BAR_CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        ...
    except Exception as e:
        import sys

        logger.exception(e)
        sys.exit(1)
