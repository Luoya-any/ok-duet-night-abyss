from qfluentwidgets import FluentIcon
import time
import win32con
import win32gui

from ok import Logger, TaskDisabledException
from src.tasks.DNAOneTimeTask import DNAOneTimeTask
from src.tasks.CommissionsTask import CommissionsTask, Mission
from src.tasks.BaseCombatTask import BaseCombatTask

logger = Logger.get_logger(__name__)


class Auto65ArtifactTask(DNAOneTimeTask, CommissionsTask, BaseCombatTask):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon = FluentIcon.FLAG
        self.description = "全自动"
        self.default_config.update({
            '任务超时时间': 240,
            '刷几次': 999,
        })
        self.config_description.update({
            '任务超时时间': '放弃任务前等待的秒数',
        })
        self.setup_commission_config()
        self.default_config.pop("启用自动穿引共鸣", None)
        self.default_config.pop("自动选择首个密函和密函奖励", None)
        self.name = "自动65级魔之楔本"
        self.action_timeout = 10
        
    def run(self):
        DNAOneTimeTask.run(self)
        self.move_mouse_to_safe_position()
        try:
            return self.do_run()
        except TaskDisabledException as e:
            pass
        except Exception as e:
            logger.error('AutoExpulsion error', e)
            raise

    def do_run(self):
        self.load_char()
        _start_time = 0
        _skill_time = 0
        _count = 0
        if self.in_team():
            self.give_up_mission()
            self.wait_until(lambda: not self.in_team(), time_out=30)
        while True:
            if self.in_team():
                if _start_time == 0:
                    _start_time = time.time()
                _skill_time = self.use_skill(_skill_time)
                if time.time() - _start_time >= self.config.get('任务超时时间', 120):
                    logger.info("已经超时，重开任务...")
                    self.give_up_mission()
                    self.wait_until(lambda: not self.in_team(), time_out=30)

            _status = self.handle_mission_interface()
            if _status == Mission.START:
                self.log_info('任务完成')
                _count += 1
                if _count >= self.config.get('刷几次', 999):
                    return
                self.wait_until(self.in_team, time_out=30)
                _start_time = time.time()
                self.walk_to_aim()
            self.sleep(0.2)

    def walk_to_aim(self):
        win32gui.SendMessage(self.hwnd.hwnd, win32con.WM_KEYDOWN, 0xA4, 0)
        self.sleep(2)      
        self.send_key_down('w')
        self.sleep(8.5)
        self.send_key_up('w')
        self.send_key_down('a')
        self.sleep(0.2)
        self.send_key_up('a')
        self.middle_click(after_sleep=0.5)
        self.send_key_down('w')
        self.sleep(6)
        self.send_key_down('d')
        self.sleep(5.6)
        self.send_key_up('d')
        self.sleep(19)
        self.send_key_down('d')
        self.sleep(7)
        self.send_key_up('d')
        self.sleep(2.5)
        self.send_key_up('w')
        self.sleep(0.2)
        self.send_key_down('a')
        self.sleep(5)
        self.send_key_up('a')
        win32gui.SendMessage(self.hwnd.hwnd, win32con.WM_KEYUP, 0xA4, 0)