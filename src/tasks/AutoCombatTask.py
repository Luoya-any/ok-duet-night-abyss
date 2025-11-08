from ok import TriggerTask, Logger, og
from src.tasks.BaseCombatTask import BaseCombatTask, NotInCombatException, CharDeadException

from pynput import mouse

logger = Logger.get_logger(__name__)


class AutoCombatTask(BaseCombatTask, TriggerTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "自动战斗"
        self.description = "需使用鼠标侧键主动激活"
        self.default_config.update({
            "激活键": "x2",
            "技能": "普攻",
            "释放间隔": 0.1,
        })
        self.config_type["激活键"] = {"type": "drop_down", "options": ["x1", "x2"]}
        self.config_type["技能"] = {"type": "drop_down", "options": ["普攻", "战技", "终结技"]}
        self.config_description.update({
            "激活键": "鼠标侧键",
        })
        self.connected = False

    def run(self):
        if not self.connected:
            self.connected = True
            og.my_app.clicked.connect(self.on_global_click)

        ret = False
        while self.in_combat():
            if not ret:
                n = self.config.get("释放间隔", 0.1)
                interval = 0.1 if n < 0.1 else n
                char = self.get_current_char()
            ret = True
            try:
                skill = self.config.get("技能", "普攻")
                if skill == "战技":
                    char.send_combat_key()
                elif skill == "终结技":
                    char.send_ultimate_key()
                else:
                    char.click()
                self.sleep(interval)
            except CharDeadException:
                self.log_error(f"Characters dead", notify=True)
                break
            except NotInCombatException as e:
                logger.info(f"auto_combat_task_out_of_combat {e}")
                break

        if ret:
            self.combat_end()
        return ret

    def on_global_click(self, x, y, button, pressed):
        if self._executor.paused:
            return
        if self.config.get("激活键", "x2") == "x1":
            btn = mouse.Button.x1
        else:
            btn = mouse.Button.x2
        if pressed and button == btn:
            self.manual_in_combat = not self.manual_in_combat
