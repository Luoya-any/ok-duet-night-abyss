from qfluentwidgets import FluentIcon
import time

from ok import Logger, TaskDisabledException, Box
from src.tasks.DNAOneTimeTask import DNAOneTimeTask
from src.tasks.CommissionsTask import CommissionsTask, Mission, QuickMoveTask

logger = Logger.get_logger(__name__)


class AutoDefence(DNAOneTimeTask, CommissionsTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon = FluentIcon.FLAG
        self.description = "半自动"
        self.default_config.update({
            '轮次': 3,
            '波次超时时间': 90,
        })
        self.config_description = {
            "轮次": "打几个轮次",
            "波次超时时间": "超时后将发出提示",
        }
        self.setup_commission_config()
        self.name = "自动扼守"
        self.action_timeout = 10
        self.quick_move_task = QuickMoveTask(self)

    def run(self):
        DNAOneTimeTask.run(self)
        self.move_mouse_to_safe_position()
        try:
            return self.do_run()
        except TaskDisabledException as e:
            pass
        except Exception as e:
            logger.error("AutoDefence error", e)
            raise

    def do_run(self):
        self.init_param()
        self.load_char()
        _wave = -1
        _wait_next_wave = False
        _skill_time = 0
        _wave_start = 0
        while True:
            if self.in_team():
                self.get_wave_info()
                if self.current_wave != -1:
                    if self.current_wave != _wave:
                        _wave = self.current_wave
                        _wave_start = time.time()
                        _wait_next_wave = False
                        self.quick_move_task.reset()

                    if (not _wait_next_wave
                        and time.time() - _wave_start >= self.config.get("波次超时时间", 120)
                    ):
                        self.log_info_notify("任务超时")
                        self.soundBeep()
                        _wait_next_wave = True

                    if not _wait_next_wave:
                        _skill_time = self.use_skill(_skill_time)
                else:
                    self.quick_move_task.run()

            _status = self.handle_mission_interface(stop_func=self.stop_func)
            if _status == Mission.START:
                self.init_param()
                self.log_info_notify("任务完成")
                self.soundBeep()
            elif _status == Mission.STOP:
                self.quit_mission()
                self.init_param()
                self.log_info("任务中止")
            elif _status == Mission.CONTINUE:
                self.log_info("任务继续")
                self.wait_until(self.in_team, time_out=30)
                self.current_wave = -1

            self.sleep(0.2)

    def init_param(self):
        self.stop_mission = False
        self.current_round = -1
        self.current_wave = -1

    def stop_func(self):
        self.get_round_info()
        n = self.config.get("轮次", 3)
        if n == 1 or self.current_round >= n:
            return True
