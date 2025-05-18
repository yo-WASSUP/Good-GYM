import os
from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

class SoundManager(QObject):
    """音效管理类，用于播放各种提示音"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_sounds()
    
    def init_sounds(self):
        """初始化所有声音效果"""
        # 设置各种音效的路径
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.count_sound_path = os.path.join(base_dir, "assets", "count.mp3")
        self.succeed_sound_path = os.path.join(base_dir, "assets", "succeed.mp3")
        self.milestone_sound_path = os.path.join(base_dir, "assets", "milestone.mp3")
        
        # 验证文件是否存在
        self.count_file_exists = os.path.exists(self.count_sound_path)
        self.succeed_file_exists = os.path.exists(self.succeed_sound_path)
        self.milestone_file_exists = os.path.exists(self.milestone_sound_path)
        
        # 初始化播放器
        self.init_sound_players()
    
    def init_sound_players(self):
        """初始化播放器"""
        # 初始化计数播放器
        self.count_sound = QMediaPlayer(self)
        if self.count_file_exists:
            self.count_sound.setMedia(QMediaContent(QUrl.fromLocalFile(self.count_sound_path)))
            self.count_sound.setVolume(80)  
        
        # 初始化成功播放器
        self.succeed_player = QMediaPlayer(self)
        if self.succeed_file_exists:
            self.succeed_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.succeed_sound_path)))
            self.succeed_player.setVolume(80)  # 设置音量 (0-100)
            
        # 初始化里程碑播放器
        self.milestone_player = QMediaPlayer(self)
        if self.milestone_file_exists:
            self.milestone_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.milestone_sound_path)))
            self.milestone_player.setVolume(85)  # 设置音量 (0-100)
    
    def play_count_sound(self):
        """播放计数音效"""
        if self.count_file_exists:
            # 使用计数音效文件
            self.count_sound.play()
    
    def play_milestone_sound(self, count):
        """播放里程碑提示音 (如每10次播放特殊声音)"""
        if count > 0 and count % 10 == 0:
            if self.milestone_file_exists:
                # 使用里程碑音效文件
                self.milestone_player.setPosition(0)  # 重置播放位置
                self.milestone_player.play()
    
    def play_completion_sound(self):
        """播放完成提示音 (可用于特定目标达成后)"""
        if self.succeed_file_exists:
            # 使用成功提示音
            self.succeed_player.setPosition(0)  # 重置播放位置
            self.succeed_player.play()
