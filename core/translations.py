class Translations:
    """Translation module, provides Chinese-English text support"""
    
    # Current language (default Chinese)
    current_language = "en"
    
    # Chinese-English translation dictionary
    translations = {
        # Application title and general
        "app_title": {
            "zh": "AI健身助手 Good-GYM",
            "en": "AI Workout Assistant Good-GYM",
        },
        "ready": {
            "zh": "准备就绪",
            "en": "Ready",
        },
        "app_subtitle": {
            "zh": "AI 姿态健身计数器",
            "en": "AI pose workout counter",
        },
        "camera_feed": {
            "zh": "摄像头画面",
            "en": "Camera feed",
        },
        "tracking_status": {
            "zh": "RTMPose 跟踪中",
            "en": "RTMPose tracking",
        },
        "live_session": {
            "zh": "实时训练",
            "en": "LIVE SESSION",
        },
        "camera_fps": {
            "zh": "摄像头 FPS",
            "en": "CAM FPS",
        },
        "ai_fps": {
            "zh": "AI FPS",
            "en": "AI FPS",
        },
        
        # Menu items
        "tools_menu": {
            "zh": "工具",
            "en": "Tools",
        },
        "mode_menu": {
            "zh": "模式",
            "en": "Mode",
        },
        "help_menu": {
            "zh": "帮助",
            "en": "Help",
        },
        "language_menu": {
            "zh": "语言",
            "en": "Language",
        },
        "chinese": {
            "zh": "中文",
            "en": "Chinese",
        },
        "english": {
            "zh": "英文",
            "en": "English",
        },
        "skeleton_display": {
            "zh": "显示骨架",
            "en": "Show Skeleton",
        },
        "video_file": {
            "zh": "打开视频文件",
            "en": "Open Video File",
        },
        "camera_mode": {
            "zh": "切换到摄像头模式",
            "en": "Switch to Camera Mode",
        },
        "rotation_mode": {
            "zh": "竖屏模式",
            "en": "Vertical Mode",
        },
        "workout_mode": {
            "zh": "健身运动模式",
            "en": "Workout Mode",
        },
        "stats_mode": {
            "zh": "统计管理模式",
            "en": "Statistics Mode",
        },
        "about": {
            "zh": "关于",
            "en": "About",
        },
        
        # Control panel
        "exercise_data": {
            "zh": "运动数据",
            "en": "Exercise Data",
        },
        "count_completed": {
            "zh": "完成次数:",
            "en": "Count:",
        },
        "current_angle": {
            "zh": "当前角度:",
            "en": "Current Angle:",
        },
        "control_options": {
            "zh": "控制选项",
            "en": "Control Options",
        },
        "exercise_type": {
            "zh": "运动类型:",
            "en": "Exercise Type:",
        },
        "counter_controls": {
            "zh": "计数控制:",
            "en": "Counter Controls:",
        },
        "camera": {
            "zh": "摄像头:",
            "en": "Camera:",
        },
        "increase": {
            "zh": "增加",
            "en": "Increase",
        },
        "decrease": {
            "zh": "减少",
            "en": "Decrease",
        },
        "reset": {
            "zh": "重置",
            "en": "Reset",
        },
        "confirm": {
            "zh": "确认记录",
            "en": "Confirm",
        },
        "phase_display": {
            "zh": "阶段显示",
            "en": "Phase Display",
        },
        "current_phase": {
            "zh": "当前阶段:",
            "en": "Current Phase:",
        },
        "up": {
            "zh": "上升",
            "en": "Up",
        },
        "down": {
            "zh": "下降",
            "en": "Down",
        },
        "rest": {
            "zh": "休息",
            "en": "Rest",
        },
        
        # Exercise types
        "squat": {
            "zh": "深蹲",
            "en": "Squat",
        },
        "pushup": {
            "zh": "俯卧撑",
            "en": "Push-up",
        },
        "situp": {
            "zh": "仰卧起坐",
            "en": "Sit-up",
        },
        "bicep_curl": {
            "zh": "弯举",
            "en": "Bicep Curl",
        },
        "lateral_raise": {
            "zh": "侧平举",
            "en": "Lateral Raise",
        },
        "overhead_press": {
            "zh": "推举",
            "en": "Overhead Press",
        },
        "leg_raise": {
            "zh": "抬腿",
            "en": "Leg Raise",
        },
        "knee_raise": {
            "zh": "抬膝",
            "en": "Knee Raise",
        },
        "knee_press": {
            "zh": "压膝",
            "en": "Knee Press",
        },
        "crunch": {
            "zh": "卷腹",
            "en": "Crunch",
        },
        
        # Status bar messages
        "welcome": {
            "zh": "欢迎使用AI健身助手",
            "en": "Welcome to AI Workout Assistant",
        },
        "language_changed": {
            "zh": "语言已更改",
            "en": "Language changed",
        },
        "switched_to_workout": {
            "zh": "已切换到健身运动模式",
            "en": "Switched to workout mode",
        },
        "switched_to_stats": {
            "zh": "已切换到统计管理模式",
            "en": "Switched to statistics mode",
        },
        "counter_reset": {
            "zh": "计数器已重置",
            "en": "Counter reset",
        },
        "goal_reached": {
            "zh": "目标达成！",
            "en": "Goal reached!",
        },
        "goal_updated": {
            "zh": "目标已更新",
            "en": "Goal updated",
        },
        
        # Statistics panel
        "fitness_statistics": {
            "zh": "健身统计",
            "en": "Fitness Statistics",
        },
        "today_tab": {
            "zh": "今日进度",
            "en": "Today",
        },
        "week_tab": {
            "zh": "本周统计",
            "en": "Week",
        },
        "month_tab": {
            "zh": "本月统计",
            "en": "Month",
        },
        "goals_tab": {
            "zh": "目标设置",
            "en": "Goals",
        },
        
        # Content for each tab
        "today_exercise_progress": {
            "zh": "今日运动进度",
            "en": "Today's Exercise Progress",
        },
        "no_goals_message": {
            "zh": "未设置任何运动目标",
            "en": "No exercise goals set",
        },
        "today_total": {
            "zh": "今日总计完成",
            "en": "Today's Total",
        },
        "total_completion": {
            "zh": "今日总计完成: {count} 次",
            "en": "Today's Total: {count} reps",
        },
        "weekly_progress": {
            "zh": "本周运动进度",
            "en": "Weekly Exercise Progress",
        },
        "weekly_workout_days": {
            "zh": "本周运动天数",
            "en": "Weekly Workout Days",
        },
        "monthly_progress": {
            "zh": "本月运动进度",
            "en": "Monthly Exercise Progress",
        },
        "monthly_stats": {
            "zh": "本月运动统计",
            "en": "Monthly Workout Stats",
        },
        "workout_goals": {
            "zh": "运动目标设置",
            "en": "Workout Goal Settings",
        },
        "daily_goals": {
            "zh": "每日运动目标",
            "en": "Daily Workout Goals",
        },
        "weekly_goals": {
            "zh": "每周运动目标",
            "en": "Weekly Workout Goals",
        },
        "days_per_week": {
            "zh": "每周运动天数",
            "en": "Workout Days Per Week",
        },
        "save_goals": {
            "zh": "保存目标",
            "en": "Save Goals",
        },
        
        # About dialog
        "about_title": {
            "zh": "关于AI健身助手",
            "en": "About AI Workout Assistant",
        },
        "about_content": {
            "zh": "AI健身助手 v1.0\n\n基于AI姿态识别的健身辅助系统\n\n支持多种健身动作的自动计数和姿态分析",
            "en": "AI Workout Assistant v1.0\n\nAI-based pose recognition fitness system\n\nSupports automatic counting and pose analysis for various exercises",
        },
        "about_text": {
            "zh": "AI健身助手-GoodGYM\n\n版本1.2\n\n基于PyQt5和RTMpose开发的健身运动计数器应用，支持多种运动姿态识别和自动计数。\n\n特点：\n\n·实时姿态检测和角度计算\n\n·健身统计~跟踪您的健身进度\n\n·实时帧显示和状态反馈\n\n·支持自定义多种运动类型\n\n·美观的用户界面和多语言支持\n\n作者：Spike Don\n\nGitHub: Good-GYM\nhttps://github.com/yo-WASSUP/Good-GYM\n\n小红书：想吃好果计\nhttps://www.xiaohongshu.com/user/profile/5fdf34b50000000001008057",
            "en": "AI Workout Assistant - GoodGYM\n\nVersion 1.2\n\nA fitness exercise counter application developed based on PyQt5 and RTMPose, supporting multiple exercise pose recognition and automatic counting.\n\nFeatures:\n\n·Real-time pose detection and angle calculation\n\n·Fitness Statistics - Track your fitness progress\n\n·Real-time frame display and status feedback\n\n·Support for custom multiple exercise types\n\n·Beautiful user interface and multi-language support\n\nAuthor: Spike Don\n\nGitHub: Good-GYM\nhttps://github.com/yo-WASSUP/Good-GYM\n\nXiaohongshu: 想吃好果计\nhttps://www.xiaohongshu.com/user/profile/5fdf34b50000000001008057",
        },
        
        # Video related
        "open_video": {
            "zh": "打开视频文件",
            "en": "Open Video File",
        },
        "video_files": {
            "zh": "视频文件 (*.mp4 *.avi *.mov *.wmv *.mkv)",
            "en": "Video Files (*.mp4 *.avi *.mov *.wmv *.mkv)",
        },
        "error_opening_video": {
            "zh": "无法打开视频文件",
            "en": "Failed to open video file",
        },
        "video_loaded": {
            "zh": "视频已加载: ",
            "en": "Video loaded: ",
        },
        
        # Model related
        "model_type": {
            "zh": "模型选择:",
            "en": "Model:",
        },
        "lightweight": {
            "zh": "轻量级模型",
            "en": "Lightweight",
        },
        "balanced": {
            "zh": "平衡模型",
            "en": "Balanced",
        },
        "performance": {
            "zh": "高性能模型",
            "en": "Performance",
        },
        "changing_model": {
            "zh": "正在切换模型到",
            "en": "Changing model to",
        },
        "model_changed_to": {
            "zh": "模型已切换为",
            "en": "Model changed to",
        },
        "model_change_failed": {
            "zh": "模型切换失败",
            "en": "Model change failed",
        },
        "severe_error": {
            "zh": "发生严重错误，请重启应用",
            "en": "Severe error occurred, please restart application",
        },
        "mirror_mode": {
            "zh": "镜像模式",
            "en": "Mirror Mode",
        },
        "gpu_acceleration": {
            "zh": "GPU加速",
            "en": "GPU Acceleration",
        },
        "gpu_enabled": {
            "zh": "已启用GPU加速",
            "en": "GPU acceleration enabled",
        },
        "gpu_disabled": {
            "zh": "已切换到CPU模式",
            "en": "Switched to CPU mode",
        },
        "gpu_not_available": {
            "zh": "未检测到GPU，仅支持CPU模式",
            "en": "No GPU detected, CPU mode only",
        },

    }
    
    @classmethod
    def get(cls, key):
        """Get translation text for current language"""
        if key in cls.translations:
            return cls.translations[key][cls.current_language]
        return key
    
    @classmethod
    def get_language(cls):
        """Get current language setting"""
        return cls.current_language
    
    @classmethod
    def set_language(cls, language):
        """Set current language"""
        if language in ["zh", "en"]:
            cls.current_language = language
            return True
        return False
