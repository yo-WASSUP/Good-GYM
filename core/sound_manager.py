import os
from PyQt5.QtCore import QUrl, QObject
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent

class SoundManager(QObject):
    """Sound effect management class for playing various notification sounds"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_sounds()
    
    def init_sounds(self):
        """Initialize all sound effects"""
        # Set paths for various sound effects
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.count_sound_path = os.path.join(base_dir, "assets", "count.mp3")
        self.succeed_sound_path = os.path.join(base_dir, "assets", "succeed.mp3")
        self.milestone_sound_path = os.path.join(base_dir, "assets", "milestone.mp3")
        
        # Verify files exist
        self.count_file_exists = os.path.exists(self.count_sound_path)
        self.succeed_file_exists = os.path.exists(self.succeed_sound_path)
        self.milestone_file_exists = os.path.exists(self.milestone_sound_path)
        
        # Initialize players
        self.init_sound_players()
    
    def init_sound_players(self):
        """Initialize players"""
        # Initialize count player
        self.count_sound = QMediaPlayer(self)
        if self.count_file_exists:
            self.count_sound.setMedia(QMediaContent(QUrl.fromLocalFile(self.count_sound_path)))
            self.count_sound.setVolume(80)  
        
        # Initialize success player
        self.succeed_player = QMediaPlayer(self)
        if self.succeed_file_exists:
            self.succeed_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.succeed_sound_path)))
            self.succeed_player.setVolume(80)  # Set volume (0-100)
            
        # Initialize milestone player
        self.milestone_player = QMediaPlayer(self)
        if self.milestone_file_exists:
            self.milestone_player.setMedia(QMediaContent(QUrl.fromLocalFile(self.milestone_sound_path)))
            self.milestone_player.setVolume(85)  # Set volume (0-100)
    
    def play_count_sound(self):
        """Play count sound effect"""
        if self.count_file_exists:
            # Use count sound file
            self.count_sound.play()
    
    def play_milestone_sound(self, count):
        """Play milestone notification sound (e.g., special sound every 10 counts)"""
        if count > 0 and count % 10 == 0:
            if self.milestone_file_exists:
                # Use milestone sound file
                self.milestone_player.setPosition(0)  # Reset playback position
                self.milestone_player.play()
    
    def play_completion_sound(self):
        """Play completion notification sound (can be used after achieving specific goals)"""
        if self.succeed_file_exists:
            # Use success notification sound
            self.succeed_player.setPosition(0)  # Reset playback position
            self.succeed_player.play()
