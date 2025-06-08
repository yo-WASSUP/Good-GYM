class Translations:
    """翻译模块，提供中英文文本支持"""
    
    # 当前语言（默认中文）
    current_language = "zh"
    
    # 中英文翻译字典
    translations = {
        # 应用标题和通用
        "app_title": {
            "zh": "AI健身助手-GoodGYM",
            "en": "AI Workout Assistant-GoodGYM"
        },
        "ready": {
            "zh": "准备就绪",
            "en": "Ready"
        },
        
        # 菜单项
        "tools_menu": {
            "zh": "工具",
            "en": "Tools"
        },
        "mode_menu": {
            "zh": "模式",
            "en": "Mode"
        },
        "help_menu": {
            "zh": "帮助",
            "en": "Help"
        },
        "language_menu": {
            "zh": "语言",
            "en": "Language"
        },
        "chinese": {
            "zh": "中文",
            "en": "Chinese"
        },
        "english": {
            "zh": "英文",
            "en": "English"
        },
        "skeleton_display": {
            "zh": "显示骨架",
            "en": "Show Skeleton"
        },
        "video_file": {
            "zh": "打开视频文件",
            "en": "Open Video File"
        },
        "camera_mode": {
            "zh": "切换到摄像头模式",
            "en": "Switch to Camera Mode"
        },
        "rotation_mode": {
            "zh": "竖屏模式",
            "en": "Vertical Mode"
        },
        "workout_mode": {
            "zh": "健身运动模式",
            "en": "Workout Mode"
        },
        "stats_mode": {
            "zh": "统计管理模式",
            "en": "Statistics Mode"
        },
        "about": {
            "zh": "关于",
            "en": "About"
        },
        
        # 控制面板
        "exercise_data": {
            "zh": "运动数据",
            "en": "Exercise Data"
        },
        "count_completed": {
            "zh": "完成次数:",
            "en": "Count:"
        },
        "current_angle": {
            "zh": "当前角度:",
            "en": "Current Angle:"
        },
        "control_options": {
            "zh": "控制选项",
            "en": "Control Options"
        },
        "exercise_type": {
            "zh": "运动类型:",
            "en": "Exercise Type:"
        },
        "counter_controls": {
            "zh": "计数控制:",
            "en": "Counter Controls:"
        },
        "camera": {
            "zh": "摄像头:",
            "en": "Camera:"
        },
        "increase": {
            "zh": "增加",
            "en": "Increase"
        },
        "decrease": {
            "zh": "减少",
            "en": "Decrease"
        },
        "reset": {
            "zh": "重置",
            "en": "Reset"
        },
        "confirm": {
            "zh": "确认记录",
            "en": "Confirm"
        },
        "phase_display": {
            "zh": "阶段显示",
            "en": "Phase Display"
        },
        "current_phase": {
            "zh": "当前阶段:",
            "en": "Current Phase:"
        },
        "up": {
            "zh": "上升",
            "en": "Up"
        },
        "down": {
            "zh": "下降",
            "en": "Down"
        },
        "prepare": {
            "zh": "准备",
            "en": "Prepare"
        },
        
        # 运动类型
        "overhead_press": {
            "zh": "推举",
            "en": "Overhead Press"
        },
        "bicep_curl": {
            "zh": "二头弯举",
            "en": "Bicep Curl"
        },
        "squat": {
            "zh": "深蹲",
            "en": "Squat"
        },
        "pushup": {
            "zh": "俯卧撑",
            "en": "Push Up"
        },
        "situp": {
            "zh": "仰卧起坐",
            "en": "Sit Up"
        },
        "lateral_raise": {
            "zh": "侧平举",
            "en": "Lateral Raise"
        },
        "leg_raise": {
            "zh": "左右交替抬腿",
            "en": "Leg Raise"
        },
        "knee_raise": {
            "zh": "交替提膝",
            "en": "Knee Raise"
        },
        "left_knee_press": {
            "zh": "左侧提膝下压",
            "en": "Left Knee Press"
        },
        "right_knee_press": {
            "zh": "右侧提膝下压",
            "en": "Right Knee Press"
        },
        
        # 状态栏信息
        "welcome": {
            "zh": "欢迎使用AI健身助手! 已加载健身计划功能",
            "en": "Welcome to AI Workout Assistant! Workout plan loaded"
        },
        "gpu_enabled": {
            "zh": "(GPU加速已启用)",
            "en": "(GPU acceleration enabled)"
        },
        "cpu_mode": {
            "zh": "(CPU模式)",
            "en": "(CPU mode)"
        },
        "switched_to_workout": {
            "zh": "已切换到健身运动模式，正在重新启动摄像头...",
            "en": "Switched to workout mode, restarting camera..."
        },
        "switched_to_stats": {
            "zh": "已切换到统计管理模式",
            "en": "Switched to statistics mode"
        },
        "language_changed": {
            "zh": "语言已更改为中文",
            "en": "Language changed to English"
        },
        
        # 统计面板
        "workout_stats_panel": {
            "zh": "健身计划与统计",
            "en": "Workout Plan and Statistics"
        },
        "today_progress": {
            "zh": "今日进度",
            "en": "Today's Progress"
        },
        "week_stats": {
            "zh": "本周统计",
            "en": "Weekly Stats"
        },
        "month_stats": {
            "zh": "本月统计",
            "en": "Monthly Stats"
        },
        "fitness_goals": {
            "zh": "目标设置",
            "en": "Goals Setting"
        },
        
        # 每个标签页的内容
        "today_exercise_progress": {
            "zh": "今日运动进度",
            "en": "Today's Exercise Progress"
        },
        "no_goals_message": {
            "zh": "未设置任何运动目标",
            "en": "No exercise goals set"
        },
        "today_total": {
            "zh": "今日总计完成",
            "en": "Today's Total"
        },
        "total_completion": {
            "zh": "今日总计完成: {count} 次",
            "en": "Today's Total: {count} reps"
        },
        "weekly_progress": {
            "zh": "本周运动进度",
            "en": "Weekly Exercise Progress"
        },
        "weekly_workout_days": {
            "zh": "本周运动天数",
            "en": "Weekly Workout Days"
        },
        "monthly_progress": {
            "zh": "本月运动进度",
            "en": "Monthly Exercise Progress"
        },
        "monthly_stats": {
            "zh": "本月运动统计",
            "en": "Monthly Workout Stats"
        },
        "workout_goals": {
            "zh": "运动目标设置",
            "en": "Workout Goal Settings"
        },
        "daily_goals": {
            "zh": "每日运动目标",
            "en": "Daily Workout Goals"
        },
        "weekly_goals": {
            "zh": "每周运动目标",
            "en": "Weekly Workout Goals"
        },
        "days_per_week": {
            "zh": "每周运动天数",
            "en": "Workout Days Per Week"
        },
        "save_goals": {
            "zh": "保存目标",
            "en": "Save Goals"
        },
        
        # 关于对话框
        "about_title": {
            "zh": "关于AI健身助手",
            "en": "About AI Workout Assistant"
        },
        "about_content": {
            "zh": "AI健身助手 v1.0\n\n基于AI姿态识别的健身辅助系统\n\n支持多种健身动作的自动计数和姿态分析",
            "en": "AI Workout Assistant v1.0\n\nAI-based pose recognition fitness system\n\nSupports automatic counting and pose analysis for various exercises"
        },
        
        # 视频相关
        "open_video": {
            "zh": "打开视频文件",
            "en": "Open Video File"
        },
        "video_files": {
            "zh": "视频文件 (*.mp4 *.avi *.mov *.wmv *.mkv)",
            "en": "Video Files (*.mp4 *.avi *.mov *.wmv *.mkv)"
        },
        "error_opening_video": {
            "zh": "无法打开视频文件",
            "en": "Failed to open video file"
        },
        "video_loaded": {
            "zh": "视频已加载: ",
            "en": "Video loaded: "
        },
        
        # 模型相关
        "model_type": {
            "zh": "模型选择:",
            "en": "Model:"
        },
        "lightweight": {
            "zh": "轻量级模型",
            "en": "Lightweight"
        },
        "balanced": {
            "zh": "平衡模型",
            "en": "Balanced"
        },
        "performance": {
            "zh": "高性能模型",
            "en": "Performance"
        },
        "changing_model": {
            "zh": "正在切换模型到",
            "en": "Changing model to"
        },
        "model_changed_to": {
            "zh": "模型已切换为",
            "en": "Model changed to"
        },
        "model_change_failed": {
            "zh": "模型切换失败",
            "en": "Model change failed"
        },
        "severe_error": {
            "zh": "发生严重错误，请重启应用",
            "en": "Severe error occurred, please restart application"
        },
        "mirror_mode": {
            "zh": "镜像模式",
            "en": "Mirror Mode"
        },
    }
    
    @classmethod
    def get(cls, key):
        """获取当前语言的翻译文本"""
        if key in cls.translations:
            return cls.translations[key][cls.current_language]
        return key
    
    @classmethod
    def set_language(cls, language):
        """设置当前语言"""
        if language in ["zh", "en"]:
            cls.current_language = language
            return True
        return False
