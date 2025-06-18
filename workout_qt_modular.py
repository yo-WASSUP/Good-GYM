import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QSplitter, QStatusBar, QMessageBox, QAction, QActionGroup, QMenu, QTableWidgetItem, QFileDialog)
from PyQt5.QtCore import Qt, QTimer

# Import custom modules
from core.video_thread import VideoThread
from core.rtmpose_processor import RTMPoseProcessor
from core.sound_manager import SoundManager
from core.workout_tracker import WorkoutTracker
from core.translations import Translations as T
from exercise_counters import ExerciseCounter
from ui.video_display import VideoDisplay
from ui.control_panel import ControlPanel
from ui.workout_stats_panel import WorkoutStatsPanel
from ui.styles import AppStyles

class WorkoutTrackerApp(QMainWindow):
    """AI Fitness Assistant Main Window Class"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(T.get("app_title"))
        self.setMinimumSize(900, 900)
        
        # Only use CPU device
        self.device = 'cpu'
        
        # Set default model mode
        self.model_mode = 'balanced'
        
        # Create exercise counter instance
        self.exercise_counter = ExerciseCounter()
        
        # Initialize RTMPose pose processor
        print(f"Initializing RTMPose processor (mode: {self.model_mode}, device: {self.device})")
        self.pose_processor = RTMPoseProcessor(
            exercise_counter=self.exercise_counter,
            mode=self.model_mode,
            backend='onnxruntime',
            device=self.device
        )
        
        # Set default exercise type
        self.exercise_type = "overhead_press"
        
        # Create sound manager
        self.sound_manager = SoundManager()
        
        # Create workout tracker
        self.workout_tracker = WorkoutTracker()
        
        # Create UI
        self.setup_ui()
        
        # Initialize video thread
        self.setup_video_thread()
        
        # Create timer for animation effects
        self.setup_animation_timer()
        
        # Initialize fitness stats panel
        self.init_workout_stats()
        
        # Start video processing
        self.start_video()
        
        # Current counter value
        self.current_count = 0
        
        # Manual count tracking
        self.manual_count = 0
        
        # Reset operation flag, used to avoid automatic recording triggered by reset operations
        self.is_resetting = False
        
        # Default to not showing fitness stats panel
        self.stats_panel.setVisible(False)
        
        # Show welcome message on first startup
        self.statusBar.showMessage(f"{T.get('welcome')} - RTMPose ({self.model_mode}) on {self.device}")
        
        # Add mirror mode related attributes
        self.mirror_mode = True
    
    def setup_ui(self):
        """Setup user interface"""
        # Apply styles
        self.setPalette(AppStyles.get_window_palette())
        self.setStyleSheet(AppStyles.get_global_stylesheet())
        
        # Create main window layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create left area (video and fitness stats)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add video display section
        self.video_display = VideoDisplay()
        left_layout.addWidget(self.video_display)
        
        # Add left area to main layout
        main_layout.addWidget(left_widget, 7)  # Allocate 70% space to left area
        
        # Add control panel
        self.control_panel = ControlPanel()
        main_layout.addWidget(self.control_panel, 3)  # Allocate 30% space to control panel
        
        # Add status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(T.get("ready"))
        
        # Setup menu bar
        self.setup_menu_bar()
        
        # Current language
        self.current_language = "zh"
        
        # Connect control panel signals
        self.connect_signals()
    
    def connect_signals(self):
        """Connect signals and slots"""
        # Connect control panel signals
        self.control_panel.exercise_changed.connect(self.change_exercise)
        self.control_panel.counter_reset.connect(self.reset_counter)
        self.control_panel.camera_changed.connect(self.change_camera)
        self.control_panel.rotation_toggled.connect(self.toggle_rotation)
        self.control_panel.skeleton_toggled.connect(self.toggle_skeleton)
        self.control_panel.model_changed.connect(self.change_model)  # Connect model switching signal
        self.control_panel.mirror_toggled.connect(self.toggle_mirror)
        
        # Connect new button signals
        self.control_panel.counter_increase.connect(self.increase_counter)
        self.control_panel.counter_decrease.connect(self.decrease_counter)
        self.control_panel.record_confirmed.connect(self.confirm_record)
        
        # Connect stats panel signals
        # Note: These need to be called after self.stats_panel is initialized
        if hasattr(self, 'stats_panel'):
            self.stats_panel.goal_updated.connect(self.update_goal)
            self.stats_panel.weekly_goal_updated.connect(self.update_weekly_goal)
            self.stats_panel.month_changed.connect(self.load_month_stats)
    
    def setup_video_thread(self):
        """Setup video processing thread"""
        # Use lower resolution to improve performance
        self.video_thread = VideoThread(
            camera_id=0,
            width=640,  # Reduce resolution to 640x480
            height=360,
            rotate=True
        )
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        
        # Initialize FPS value
        self.current_fps = 0
    
    def setup_animation_timer(self):
        """Setup animation timer"""
        self.count_animation_timer = QTimer()
        self.count_animation_timer.setSingleShot(True)
        self.count_animation_timer.timeout.connect(self.control_panel.reset_counter_style)
    
    def start_video(self):
        """Start video processing"""
        self.video_thread.start()
    
    def update_image(self, frame, fps=0):
        """Update image display and process pose detection"""
        try:
            # Update FPS value
            self.current_fps = fps
            
            # Pose processor processes current frame (process every frame, no frame skipping)
            processed_frame, current_angle, keypoints = self.pose_processor.process_frame(
                frame, self.exercise_type
            )
            
            # If mirror mode is enabled, apply mirror processing
            if self.mirror_mode:
                import cv2
                processed_frame = cv2.flip(processed_frame, 1)
            
            # Update video display
            self.video_display.update_image(processed_frame)
            
            # Update UI components
            self.update_ui_components(current_angle, keypoints)
            
        except Exception as e:
            print(f"Error updating image: {e}")
    
    def update_ui_components(self, current_angle, keypoints):
        """Update UI component display"""
        try:
            # Update angle display - comment out this part of the code
            # if current_angle is not None:
            #     self.control_panel.update_angle(str(int(current_angle)), self.exercise_type)
            
            # Update phase display (up/down)
            if hasattr(self.exercise_counter, 'stage'):
                self.control_panel.update_phase(self.exercise_counter.stage)
            
            # Get current count - directly use counter attribute
            current_count = self.exercise_counter.counter
            
            # If count increases and it's not a reset operation, play sound (but don't auto-record)
            if current_count > self.current_count and not self.is_resetting:
                # Play count sound for each count increase
                self.sound_manager.play_count_sound()
                
                # Play success sound every 10 counts
                if current_count % 10 == 0:
                    self.sound_manager.play_milestone_sound(current_count)
                    self.statusBar.showMessage(f"Congratulations on completing {current_count} {self.control_panel.exercise_display_map[self.exercise_type]}!")
                
                # Update cached current count
                self.current_count = current_count
            
            # Update counter display
            self.control_panel.update_counter(str(current_count))
            
            # Keypoint information has been processed, no need to update display separately
        except Exception as e:
            print(f"Error updating image: {str(e)}")
    
    def change_exercise(self, exercise_type):
        """Change exercise type"""
        self.exercise_type = exercise_type
        self.exercise_counter.reset_counter()
        self.current_count = 0
        self.statusBar.showMessage(f"Switched to {self.control_panel.exercise_display_map[exercise_type]} exercise")
    
    def reset_counter(self):
        """Reset counter"""
        # Set reset flag to true to avoid triggering automatic recording
        self.is_resetting = True
        
        # Reset counter
        self.exercise_counter.reset_counter()
        self.current_count = 0
        self.manual_count = 0  # Also reset manual count
        self.control_panel.update_counter(0)
        
        # Restore flag after reset is complete
        self.is_resetting = False
        
        self.statusBar.showMessage("Counter has been reset")
    
    def reset_exercise_state(self):
        """Reset exercise state, including counter and related variables"""
        # Directly call existing reset counter method
        self.reset_counter()
    
    def increase_counter(self, new_count):
        """Manually increase counter value"""
        self.current_count = new_count
        # Directly update the internal count value of the counter class
        self.exercise_counter.counter = new_count
        # Increase manual count
        self.manual_count += 1
        self.statusBar.showMessage(f"Count increased to {new_count}")
    
    def decrease_counter(self, new_count):
        """Manually decrease counter value"""
        self.current_count = new_count
        # Directly update the internal count value of the counter class
        self.exercise_counter.counter = new_count
        # Manual count won't be negative
        if self.manual_count > 0:
            self.manual_count -= 1
        self.statusBar.showMessage(f"Count decreased to {new_count}")
    
    def confirm_record(self, exercise_type):
        """Confirm recording current count result to history"""
        # Get current count value (now record all counts, not just manually increased parts)
        count = self.current_count
        
        # Record to history
        if count > 0:
            # Add record to workout tracker
            completion_percentage = self.workout_tracker.add_workout_record(exercise_type, count)
            
            # Update stats panel
            self.update_today_stats()
            self.update_stats_overview()
            
            # Get Chinese name of exercise type
            exercise_name = ""
            # Try to get from control panel mapping
            if exercise_type in self.control_panel.exercise_display_map:
                exercise_name = self.control_panel.exercise_display_map[exercise_type]
            
            # Show success message
            self.statusBar.showMessage(f"Recorded {count} {exercise_name}, {completion_percentage}% of goal completed")
            
            # Reset counter (will also reset manual_count)
            self.reset_counter()
        else:
            # If there's no manually increased count, show prompt
            self.statusBar.showMessage("No manually increased count to record")
    
    def change_camera(self, index):
        """Switch camera"""
        self.video_thread.set_camera(index)
        self.statusBar.showMessage(f"Switched to camera {index}")
    
    def toggle_rotation(self, rotate):
        """Toggle video rotation mode"""
        # Update video thread rotation settings
        self.video_thread.set_rotation(rotate)
        
        # Update video display orientation settings
        # rotate=True means portrait, False means landscape
        self.video_display.set_orientation(portrait_mode=rotate)
        
        if rotate:
            self.toggle_rotation_action.setText("Turn off rotation mode")
            self.statusBar.showMessage("Switched to portrait mode (9:16)")
        else:
            self.toggle_rotation_action.setText("Turn on rotation mode")
            self.statusBar.showMessage("Switched to landscape mode (16:9)")
            
    def toggle_skeleton(self, show):
        """Toggle skeleton display"""
        self.pose_processor.set_skeleton_visibility(show)
        if show:
            self.statusBar.showMessage("Show skeleton lines")
        else:
            self.statusBar.showMessage("Hide skeleton lines")
            
    def open_video_file(self):
        """Open video file"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            T.get("open_video"),
            "",
            T.get("video_files"),
            options=options
        )
        
        if file_name:
            try:
                # Clear current count state
                self.reset_exercise_state()
                
                # Switch to workout mode (if not currently)
                if hasattr(self, 'stacked_layout') and hasattr(self, 'exercise_container'):
                    if not self.stacked_layout.currentWidget() == self.exercise_container:
                        self.switch_to_workout_mode()
                
                # Set status bar information
                video_name = os.path.basename(file_name)
                self.statusBar.showMessage(f"Current video: {video_name}")
                
                # Pass file path to video thread, set to non-loop playback mode
                self.video_thread.set_video_file(file_name, loop=False)
            except Exception as e:
                print(f"Error opening video file: {e}")
                self.statusBar.showMessage(f"Failed to open video file: {str(e)}")
    
    def switch_to_camera_mode(self):
        """Switch back to camera mode"""
        try:
            # Clear current count state
            self.reset_exercise_state()
            
            # Switch to workout mode (if not currently)
            if hasattr(self, 'stacked_layout') and hasattr(self, 'exercise_container'):
                if not self.stacked_layout.currentWidget() == self.exercise_container:
                    self.switch_to_workout_mode()
                
            # Set status bar information
            self.statusBar.showMessage("Current mode: Camera")
            
            # Return to camera mode
            self.video_thread.set_camera(0)  # Use default camera
        except Exception as e:
            print(f"Error switching to camera mode: {e}")
            self.statusBar.showMessage(f"Failed to switch to camera mode: {str(e)}")
    
    def show_about(self):
        """Show about information"""
        about_text = """
        <h1>AI Fitness Assistant-Good-GYM</h1>
        <p>Version 1.1</p>
        <p>Fitness exercise counter application developed based on PyQt5 and rtmpose, supporting multiple exercise pose recognition and automatic counting.</p>
        <p>Features:</p>
        <ul>
            <li>Real-time pose detection and angle calculation</li>
            <li>Fitness statistics - track your fitness progress</li>
            <li>Real-time frame display and status feedback</li>
            <li>Support for multiple exercise types</li>
            <li>Beautiful user interface and multi-language support</li>
        </ul>
        <p>Author: Spike Don</p>
        <p>GitHub: <a href="https://github.com/yo-WASSUP/Good-GYM">Good-GYM</a></p>
        <p>Xiaohongshu: <a href="https://www.xiaohongshu.com/user/profile/5fdf34b50000000001008057?xsec_token=&xsec_source=pc_note">想吃好果汁</a></p>
        """
        
        QMessageBox.about(self, T.get("about_title"), about_text)
    
    def setup_menu_bar(self):
        """Setup menu bar"""
        # Create menu bar
        menubar = self.menuBar()
        
        # Tools menu
        tools_menu = menubar.addMenu(T.get("tools_menu"))
        
        # Skeleton display option
        self.toggle_skeleton_action = QAction(T.get("skeleton_display"), self, checkable=True)
        self.toggle_skeleton_action.setChecked(False)  
        self.toggle_skeleton_action.triggered.connect(lambda checked: self.toggle_skeleton(checked))
        tools_menu.addAction(self.toggle_skeleton_action)
        
        # Rotation mode option
        self.toggle_rotation_action = QAction(T.get("rotation_mode"), self, checkable=True)
        self.toggle_rotation_action.setChecked(False)
        self.toggle_rotation_action.triggered.connect(lambda checked: self.toggle_rotation(checked))
        
        # Video file option
        open_action = QAction(T.get("video_file"), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_video_file)
        
        # Add video file option
        tools_menu.addAction(self.toggle_rotation_action)
        tools_menu.addSeparator()
        tools_menu.addAction(open_action)
        
        # Camera mode option
        camera_mode_action = QAction(T.get("camera_mode"), self)
        camera_mode_action.triggered.connect(self.switch_to_camera_mode)
        tools_menu.addAction(camera_mode_action)
        
        # Mode menu
        mode_menu = menubar.addMenu(T.get("mode_menu"))
        
        # Workout mode option
        workout_mode_action = QAction(T.get("workout_mode"), self)
        workout_mode_action.triggered.connect(self.switch_to_workout_mode)
        mode_menu.addAction(workout_mode_action)
        
        # Stats mode option
        stats_mode_action = QAction(T.get("stats_mode"), self)
        stats_mode_action.triggered.connect(self.switch_to_stats_mode)
        mode_menu.addAction(stats_mode_action)
        
        # Language menu
        language_menu = menubar.addMenu(T.get("language_menu"))
        
        # Chinese option
        self.chinese_action = QAction(T.get("chinese"), self, checkable=True)
        self.chinese_action.setChecked(T.current_language == "zh")
        self.chinese_action.triggered.connect(lambda: self.change_language("zh"))
        language_menu.addAction(self.chinese_action)
        
        # English option
        self.english_action = QAction(T.get("english"), self, checkable=True)
        self.english_action.setChecked(T.current_language == "en")
        self.english_action.triggered.connect(lambda: self.change_language("en"))
        language_menu.addAction(self.english_action)

        # Spanish option
        self.spanish_action = QAction(T.get("spanish"), self, checkable=True)
        self.spanish_action.setChecked(T.current_language == "es")
        self.spanish_action.triggered.connect(lambda: self.change_language("es"))
        language_menu.addAction(self.spanish_action)

        # Hindi option
        self.hindi_action = QAction(T.get("hindi"), self, checkable=True)
        self.hindi_action.setChecked(T.current_language == "hi")
        self.hindi_action.triggered.connect(lambda: self.change_language("hi"))
        language_menu.addAction(self.hindi_action)
        
        # Help menu
        help_menu = menubar.addMenu(T.get("help_menu"))
        
        # About option
        about_action = QAction(T.get("about"), self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_workout_stats(self):
        """Initialize fitness stats panel"""
        # Create fitness stats panel
        self.stats_panel = WorkoutStatsPanel()
        self.stats_panel.setVisible(False)  # Initially not visible
        
        # Set goals
        self.stats_panel.set_goals(self.workout_tracker.get_goals())
        
        # Connect stats panel signals - connect after panel creation
        self.stats_panel.goal_updated.connect(self.update_goal)
        self.stats_panel.weekly_goal_updated.connect(self.update_weekly_goal)
        self.stats_panel.month_changed.connect(self.load_month_stats)
        
    def update_today_stats(self):
        """Update today's fitness stats"""
        # Get raw data
        today_stats_raw = self.workout_tracker.get_today_stats()
        goals = self.workout_tracker.get_goals()
        
        # Convert data structure to format expected by UI components
        today_stats = {
            "exercises": {}
        }
        
        for exercise, count in today_stats_raw.items():
            today_stats["exercises"][exercise] = {"count": count}
        
        # Update UI
        self.stats_panel.update_today_stats(today_stats, goals)
    
    def update_stats_overview(self):
        """Update all stats overview"""
        # Get data
        weekly_stats = self.workout_tracker.get_weekly_stats()
        monthly_stats = self.workout_tracker.get_monthly_stats()
        goals = self.workout_tracker.get_goals()
        
        # Update to UI
        self.stats_panel.update_week_stats(weekly_stats, goals)
        self.stats_panel.update_month_stats(monthly_stats, goals)
    
    def load_month_stats(self, year, month):
        """Load stats data for specified month
        
        Args:
            year: Year
            month: Month
        """
        try:
            # Get data for specified month
            monthly_stats = self.workout_tracker.get_monthly_stats(year, month)
            goals = self.workout_tracker.get_goals()
            
            # Update monthly stats panel
            self.stats_panel.update_month_stats(monthly_stats, goals)
        except Exception as e:
            print(f"Error loading monthly data: {e}")
            self.statusBar.showMessage(f"Failed to load monthly data: {str(e)}")
    
    def update_goal(self, exercise_type, count):
        """Update exercise goal"""
        self.workout_tracker.update_goal(exercise_type, count)
        self.update_today_stats()
        self.statusBar.showMessage(f"Updated {self.control_panel.exercise_display_map.get(exercise_type, exercise_type)} goal to {count}")
    
    def update_weekly_goal(self, count):
        """Update weekly goal"""
        self.workout_tracker.update_weekly_goal(count)
        self.update_stats_overview()
        self.statusBar.showMessage(f"Updated weekly fitness goal to {count} days")
    
    def switch_to_workout_mode(self):
        """Switch to workout mode (show camera and control panel)"""
        # Hide stats panel
        if self.stats_panel.isVisible():
            self.stats_panel.setVisible(False)
        
        # Wait for video thread to completely stop
        if self.video_thread.isRunning():
            self.video_thread.stop()
            self.video_thread.wait()  # Wait for thread to completely terminate
        
        # Reinitialize video thread
        self.setup_video_thread()
        
        # Clear main layout
        central_widget = self.centralWidget()
        main_layout = central_widget.layout()
        
        # Clear all existing widgets
        while main_layout.count():
            item = main_layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                if widget == self.stats_panel:
                    widget.setVisible(False)
        
        # Create left area (video display)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add video display section
        self.video_display.setVisible(True)
        left_layout.addWidget(self.video_display)
        
        # Add left area and control panel to main layout
        self.control_panel.setVisible(True)
        main_layout.addWidget(left_widget, 7)  # Allocate 70% space to left area
        main_layout.addWidget(self.control_panel, 3)  # Allocate 30% space to control panel
        
        # Enable related menu items
        self.toggle_skeleton_action.setEnabled(True)
        self.toggle_rotation_action.setEnabled(True)
        
        # Restore video display height
        self.video_display.setMinimumHeight(400)
        
        # Start video processing
        QTimer.singleShot(500, self.start_video)  # Delay 500ms before starting video
        
        # Update status bar
        self.statusBar.showMessage(T.get("switched_to_workout"))
    
    def switch_to_stats_mode(self):
        """Switch to stats management mode (full screen display stats panel)"""
        # Hide video display area and control panel
        self.video_display.setVisible(False)
        self.control_panel.setVisible(False)
        
        # Stop video source to save resources
        self.video_thread.stop()
        
        # Find main interface center widget
        central_widget = self.centralWidget()
        main_layout = central_widget.layout()
        
        # Clear left and right parts in existing layout
        while main_layout.count():
            item = main_layout.takeAt(0)
            if item.widget():
                widget = item.widget()
                widget.setVisible(False)
        
        # Add stats panel directly to main layout
        main_layout.addWidget(self.stats_panel)
        
        # Show fitness stats panel
        self.stats_panel.setVisible(True)
        
        # Disable related menu items
        self.toggle_skeleton_action.setEnabled(False)
        self.toggle_rotation_action.setEnabled(False)
        
        # Refresh stats data
        self.update_today_stats()
        self.update_stats_overview()
        
        # Switch to "Today's Progress" tab
        self.stats_panel.tabs.setCurrentIndex(0)  
        
        # Update status bar
        self.statusBar.showMessage(T.get("switched_to_stats"))
    
    def closeEvent(self, event):
        """Clean up resources when closing window"""
        if self.video_thread.isRunning():
            self.video_thread.stop()
        event.accept()


    def change_language(self, language):
        """Change interface language"""
        if T.set_language(language):
            self.current_language = language
            
            # Update menu item selection state
            self.chinese_action.setChecked(language == "zh")
            self.english_action.setChecked(language == "en")
            self.spanish_action.setChecked(language == "es")
            self.hindi_action.setChecked(language == "hi")
            
            # Update window title
            self.setWindowTitle(T.get("app_title"))
            
            # Update menu text
            self.menuBar().clear()
            self.setup_menu_bar()
            
            # Update control panel text
            if hasattr(self, 'control_panel'):
                self.control_panel.update_language()
            
            # Update stats panel text
            if hasattr(self, 'stats_panel'):
                self.stats_panel.update_language()
            
            # Update status bar information
            self.statusBar.showMessage(T.get("language_changed"))

    def change_model(self, model_mode):
        """Switch RTMPose model mode"""
        try:
            if model_mode == self.model_mode:
                # If it's the same mode, no need to reload
                return
                
            # Stop video processing
            self.video_thread.stop()
            
            # Show status information
            self.statusBar.showMessage(f"Switching RTMPose mode to: {model_mode}...")
            
            # Update model mode
            old_model_mode = self.model_mode
            self.model_mode = model_mode
            
            print(f"Switching RTMPose mode: {old_model_mode} -> {model_mode}")
            
            # Update RTMPose processor mode
            self.pose_processor.update_model(model_mode)
            
            # Reinitialize video thread
            self.setup_video_thread()
            
            # Restart video processing
            QTimer.singleShot(500, self.start_video)  # Delay 500ms before starting video
            
            # Update status bar
            self.statusBar.showMessage(f"Switched to RTMPose {model_mode} mode")
            
        except Exception as e:
            # If switching fails, show error message
            error_msg = f"RTMPose mode switching failed: {str(e)}"
            self.statusBar.showMessage(error_msg)
            print(error_msg)
            
            # Try to rollback to original mode
            try:
                self.model_mode = old_model_mode
                self.pose_processor.update_model(old_model_mode)
                self.setup_video_thread()
                QTimer.singleShot(500, self.start_video)
                self.statusBar.showMessage(f"Rolled back to RTMPose {old_model_mode} mode")
                
            except:
                # If rollback also fails, show critical error
                self.statusBar.showMessage("Critical error in RTMPose mode switching")

    def toggle_mirror(self, mirror):
        """Toggle mirror mode"""
        self.mirror_mode = mirror


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WorkoutTrackerApp()
    window.show()
    sys.exit(app.exec_())
