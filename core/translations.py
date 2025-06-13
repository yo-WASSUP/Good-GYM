class Translations:
    """翻译模块，提供中英文文本支持"""
    
    # 当前语言（默认中文）
    current_language = "zh"
    
    # 中英文翻译字典
    translations = {
        # 应用标题和通用
        "app_title": {
            "zh": "AI健身助手-GoodGYM",
            "en": "AI Workout Assistant-GoodGYM",
            "es": "Asistente de Ejercicio AI-GoodGYM",
            "hi": "एआई व्यायाम सहायक-GoodGYM"
        },
        "ready": {
            "zh": "准备就绪",
            "en": "Ready",
            "es": "Listo",
            "hi": "तैयार"
        },
        
        # 菜单项
        "tools_menu": {
            "zh": "工具",
            "en": "Tools",
            "es": "Herramientas",
            "hi": "उपकरण"
        },
        "mode_menu": {
            "zh": "模式",
            "en": "Mode",
            "es": "Modo",
            "hi": "मोड"
        },
        "help_menu": {
            "zh": "帮助",
            "en": "Help",
            "es": "Ayuda",
            "hi": "मदद"
        },
        "language_menu": {
            "zh": "语言",
            "en": "Language",
            "es": "Idioma",
            "hi": "भाषा"
        },
        "chinese": {
            "zh": "中文",
            "en": "Chinese",
            "es": "Chino",
            "hi": "चीनी"
        },
        "english": {
            "zh": "英文",
            "en": "English",
            "es": "Inglés",
            "hi": "अंग्रेज़ी"
        },
        "spanish": {
            "zh": "西班牙语",
            "en": "Spanish",
            "es": "Español",
            "hi": "स्पेनिश"
        },
        "hindi": {
            "zh": "印地语",
            "en": "Hindi",
            "es": "Hindi",
            "hi": "हिंदी"
        },
        "skeleton_display": {
            "zh": "显示骨架",
            "en": "Show Skeleton",
            "es": "Mostrar esqueleto",
            "hi": "कंकाल दिखाएं"
        },
        "video_file": {
            "zh": "打开视频文件",
            "en": "Open Video File",
            "es": "Abrir archivo de video",
            "hi": "वीडियो फ़ाइल खोलें"
        },
        "camera_mode": {
            "zh": "切换到摄像头模式",
            "en": "Switch to Camera Mode",
            "es": "Cambiar a modo cámara",
            "hi": "कैमरा मोड पर स्विच करें"
        },
        "rotation_mode": {
            "zh": "竖屏模式",
            "en": "Vertical Mode",
            "es": "Modo vertical",
            "hi": "वर्टिकल मोड"
        },
        "workout_mode": {
            "zh": "健身运动模式",
            "en": "Workout Mode",
            "es": "Modo de entrenamiento",
            "hi": "व्यायाम मोड"
        },
        "stats_mode": {
            "zh": "统计管理模式",
            "en": "Statistics Mode",
            "es": "Modo de estadísticas",
            "hi": "आँकड़े मोड"
        },
        "about": {
            "zh": "关于",
            "en": "About",
            "es": "Acerca de",
            "hi": "के बारे में"
        },
        
        # 控制面板
        "exercise_data": {
            "zh": "运动数据",
            "en": "Exercise Data",
            "es": "Datos de ejercicio",
            "hi": "व्यायाम डेटा"
        },
        "count_completed": {
            "zh": "完成次数:",
            "en": "Count:",
            "es": "Recuento:",
            "hi": "गिनती:"
        },
        "current_angle": {
            "zh": "当前角度:",
            "en": "Current Angle:",
            "es": "Ángulo actual:",
            "hi": "वर्तमान कोण:"
        },
        "control_options": {
            "zh": "控制选项",
            "en": "Control Options",
            "es": "Opciones de control",
            "hi": "नियंत्रण विकल्प"
        },
        "exercise_type": {
            "zh": "运动类型:",
            "en": "Exercise Type:",
            "es": "Tipo de ejercicio:",
            "hi": "व्यायाम प्रकार:"
        },
        "counter_controls": {
            "zh": "计数控制:",
            "en": "Counter Controls:",
            "es": "Controles de contador:",
            "hi": "गिनती नियंत्रण:"
        },
        "camera": {
            "zh": "摄像头:",
            "en": "Camera:",
            "es": "Cámara:",
            "hi": "कैमरा:"
        },
        "increase": {
            "zh": "增加",
            "en": "Increase",
            "es": "Aumentar",
            "hi": "बढ़ाना"
        },
        "decrease": {
            "zh": "减少",
            "en": "Decrease",
            "es": "Disminuir",
            "hi": "घटाना"
        },
        "reset": {
            "zh": "重置",
            "en": "Reset",
            "es": "Restablecer",
            "hi": "रीसेट करें"
        },
        "confirm": {
            "zh": "确认记录",
            "en": "Confirm",
            "es": "Confirmar",
            "hi": "पुष्टि करें"
        },
        "phase_display": {
            "zh": "阶段显示",
            "en": "Phase Display",
            "es": "Pantalla de fase",
            "hi": "चरण प्रदर्शन"
        },
        "current_phase": {
            "zh": "当前阶段:",
            "en": "Current Phase:",
            "es": "Fase actual:",
            "hi": "वर्तमान चरण:"
        },
        "up": {
            "zh": "上升",
            "en": "Up",
            "es": "Arriba",
            "hi": "ऊपर"
        },
        "down": {
            "zh": "下降",
            "en": "Down",
            "es": "Abajo",
            "hi": "नीचे"
        },
        "prepare": {
            "zh": "准备",
            "en": "Prepare",
            "es": "Preparar",
            "hi": "तैयार करें"
        },
        
        # 运动类型
        "overhead_press": {
            "zh": "推举",
            "en": "Overhead Press",
            "es": "Pressión sobre la cabeza",
            "hi": "ओवरहेड प्रेस"
        },
        "bicep_curl": {
            "zh": "二头弯举",
            "en": "Bicep Curl",
            "es": "Curl de bíceps",
            "hi": "बाइसेप कर्ल"
        },
        "squat": {
            "zh": "深蹲",
            "en": "Squat",
            "es": "Sentadilla",
            "hi": "स्क्वाट"
        },
        "pushup": {
            "zh": "俯卧撑",
            "en": "Push Up",
            "es": "Flexión de brazos",
            "hi": "पुश अप"
        },
        "situp": {
            "zh": "仰卧起坐",
            "en": "Sit Up",
            "es": "Abdominales",
            "hi": "सिट अप"
        },
        "lateral_raise": {
            "zh": "侧平举",
            "en": "Lateral Raise",
            "es": "Elevación lateral",
            "hi": "लैटरल रेज़"
        },
        "leg_raise": {
            "zh": "左右交替抬腿",
            "en": "Leg Raise",
            "es": "Elevación de piernas",
            "hi": "लेग रेज़"
        },
        "knee_raise": {
            "zh": "交替提膝",
            "en": "Knee Raise",
            "es": "Elevación de rodilla",
            "hi": "घुटने उठाना"
        },
        "knee_press": {
            "zh": "提膝下压",
            "en": "Knee Press",
            "es": "Presión de rodilla",
            "hi": "घुटने का दबाव"
        },
        
        # 状态栏信息
        "welcome": {
            "zh": "欢迎使用AI健身助手! 已加载健身计划功能",
            "en": "Welcome to AI Workout Assistant! Workout plan loaded",
            "es": "Bienvenido al Asistente de Ejercicio AI! Plan de entrenamiento cargado",
            "hi": "एआई व्यायाम सहायक में आपका स्वागत है! व्यायाम योजना लोड हो गई"
        },
        "gpu_enabled": {
            "zh": "(GPU加速已启用)",
            "en": "(GPU acceleration enabled)",
            "es": "(Aceleración por GPU habilitada)",
            "hi": "(GPU त्वरण सक्षम है)"
        },
        "cpu_mode": {
            "zh": "(CPU模式)",
            "en": "(CPU mode)",
            "es": "(Modo CPU)",
            "hi": "(सीपीयू मोड)"
        },
        "switched_to_workout": {
            "zh": "已切换到健身运动模式，正在重新启动摄像头...",
            "en": "Switched to workout mode, restarting camera...",
            "es": "Cambiado al modo de entrenamiento, reiniciando la cámara...",
            "hi": "व्यायाम मोड पर स्विच किया गया, कैमरा फिर से शुरू किया जा रहा है..."
        },
        "switched_to_stats": {
            "zh": "已切换到统计管理模式",
            "en": "Switched to statistics mode",
            "es": "Cambiado al modo de estadísticas",
            "hi": "आँकड़े मोड पर स्विच किया गया"
        },
        "language_changed": {
            "zh": "语言已更改为中文",
            "en": "Language changed to English",
            "es": "Idioma cambiado a español",
            "hi": "भाषा हिंदी में बदल गई"
        },
        
        # 统计面板
        "workout_stats_panel": {
            "zh": "健身计划与统计",
            "en": "Workout Plan and Statistics",
            "es": "Plan de entrenamiento y estadísticas",
            "hi": "व्यायाम योजना और आँकड़े"
        },
        "today_progress": {
            "zh": "今日进度",
            "en": "Today's Progress",
            "es": "Progreso de hoy",
            "hi": "आज की प्रगति"
        },
        "week_stats": {
            "zh": "本周统计",
            "en": "Weekly Stats",
            "es": "Estadísticas semanales",
            "hi": "साप्ताहिक आँकड़े"
        },
        "month_stats": {
            "zh": "本月统计",
            "en": "Monthly Stats",
            "es": "Estadísticas mensuales",
            "hi": "मासिक आँकड़े"
        },
        "fitness_goals": {
            "zh": "目标设置",
            "en": "Goals Setting",
            "es": "Configuración de objetivos",
            "hi": "लक्ष्य सेट करना"
        },
        
        # 每个标签页的内容
        "today_exercise_progress": {
            "zh": "今日运动进度",
            "en": "Today's Exercise Progress",
            "es": "Progreso del ejercicio de hoy",
            "hi": "आज की व्यायाम प्रगति"
        },
        "no_goals_message": {
            "zh": "未设置任何运动目标",
            "en": "No exercise goals set",
            "es": "No se han establecido objetivos de ejercicio",
            "hi": "कोई व्यायाम लक्ष्य निर्धारित नहीं है"
        },
        "today_total": {
            "zh": "今日总计完成",
            "en": "Today's Total",
            "es": "Total de hoy",
            "hi": "आज का कुल"
        },
        "total_completion": {
            "zh": "今日总计完成: {count} 次",
            "en": "Today's Total: {count} reps",
            "es": "Total de hoy: {count} repeticiones",
            "hi": "आज का कुल: {count} रेप्स"
        },
        "weekly_progress": {
            "zh": "本周运动进度",
            "en": "Weekly Exercise Progress",
            "es": "Progreso del ejercicio semanal",
            "hi": "साप्ताहिक व्यायाम प्रगति"
        },
        "weekly_workout_days": {
            "zh": "本周运动天数",
            "en": "Weekly Workout Days",
            "es": "Días de entrenamiento semanal",
            "hi": "साप्ताहिक व्यायाम के दिन"
        },
        "monthly_progress": {
            "zh": "本月运动进度",
            "en": "Monthly Exercise Progress",
            "es": "Progreso del ejercicio mensual",
            "hi": "मासिक व्यायाम प्रगति"
        },
        "monthly_stats": {
            "zh": "本月运动统计",
            "en": "Monthly Workout Stats",
            "es": "Estadísticas del entrenamiento mensual",
            "hi": "मासिक व्यायाम आँकड़े"
        },
        "workout_goals": {
            "zh": "运动目标设置",
            "en": "Workout Goal Settings",
            "es": "Configuración de objetivos de entrenamiento",
            "hi": "व्यायाम लक्ष्य सेटिंग"
        },
        "daily_goals": {
            "zh": "每日运动目标",
            "en": "Daily Workout Goals",
            "es": "Objetivos de entrenamiento diario",
            "hi": "दैनिक व्यायाम लक्ष्य"
        },
        "weekly_goals": {
            "zh": "每周运动目标",
            "en": "Weekly Workout Goals",
            "es": "Objetivos de entrenamiento semanal",
            "hi": "साप्ताहिक व्यायाम लक्ष्य"
        },
        "days_per_week": {
            "zh": "每周运动天数",
            "en": "Workout Days Per Week",
            "es": "Días de entrenamiento por semana",
            "hi": "प्रति सप्ताह व्यायाम के दिन"
        },
        "save_goals": {
            "zh": "保存目标",
            "en": "Save Goals",
            "es": "Guardar objetivos",
            "hi": "लक्ष्य सहेजें"
        },
        
        # 关于对话框
        "about_title": {
            "zh": "关于AI健身助手",
            "en": "About AI Workout Assistant",
            "es": "Acerca del Asistente de Ejercicio AI",
            "hi": "एआई व्यायाम सहायक के बारे में"
        },
        "about_content": {
            "zh": "AI健身助手 v1.0\n\n基于AI姿态识别的健身辅助系统\n\n支持多种健身动作的自动计数和姿态分析",
            "en": "AI Workout Assistant v1.0\n\nAI-based pose recognition fitness system\n\nSupports automatic counting and pose analysis for various exercises",
            "es": "Asistente de Ejercicio AI v1.0\n\nSistema de fitness basado en reconocimiento de pose AI\n\nSoporta conteo automático y análisis de pose para varios ejercicios",
            "hi": "एआई व्यायाम सहायक v1.0\n\nएआई आधारित पोस पहचान फिटनेस सिस्टम\n\nविभिन्न व्यायामों के लिए स्वचालित गिनती और पोस विश्लेषण का समर्थन करता है"
        },
        
        # 视频相关
        "open_video": {
            "zh": "打开视频文件",
            "en": "Open Video File",
            "es": "Abrir archivo de video",
            "hi": "वीडियो फ़ाइल खोलें"
        },
        "video_files": {
            "zh": "视频文件 (*.mp4 *.avi *.mov *.wmv *.mkv)",
            "en": "Video Files (*.mp4 *.avi *.mov *.wmv *.mkv)",
            "es": "Archivos de video (*.mp4 *.avi *.mov *.wmv *.mkv)",
            "hi": "वीडियो फ़ाइलें (*.mp4 *.avi *.mov *.wmv *.mkv)"
        },
        "error_opening_video": {
            "zh": "无法打开视频文件",
            "en": "Failed to open video file",
            "es": "No se pudo abrir el archivo de video",
            "hi": "वीडियो फ़ाइल खोलने में असफल"
        },
        "video_loaded": {
            "zh": "视频已加载: ",
            "en": "Video loaded: ",
            "es": "Video cargado: ",
            "hi": "वीडियो लोड किया गया: "
        },
        
        # 模型相关
        "model_type": {
            "zh": "模型选择:",
            "en": "Model:",
            "es": "Modelo:",
            "hi": "मॉडल:"
        },
        "lightweight": {
            "zh": "轻量级模型",
            "en": "Lightweight",
            "es": "Modelo ligero",
            "hi": "हल्का मॉडल"
        },
        "balanced": {
            "zh": "平衡模型",
            "en": "Balanced",
            "es": "Modelo equilibrado",
            "hi": "संतुलित मॉडल"
        },
        "performance": {
            "zh": "高性能模型",
            "en": "Performance",
            "es": "Modelo de alto rendimiento",
            "hi": "उच्च प्रदर्शन मॉडल"
        },
        "changing_model": {
            "zh": "正在切换模型到",
            "en": "Changing model to",
            "es": "Cambiando el modelo a",
            "hi": "मॉडल बदलना"
        },
        "model_changed_to": {
            "zh": "模型已切换为",
            "en": "Model changed to",
            "es": "Modelo cambiado a",
            "hi": "मॉडल में बदलाव किया गया"
        },
        "model_change_failed": {
            "zh": "模型切换失败",
            "en": "Model change failed",
            "es": "Cambio de modelo fallido",
            "hi": "मॉडल परिवर्तन विफल"
        },
        "severe_error": {
            "zh": "发生严重错误，请重启应用",
            "en": "Severe error occurred, please restart application",
            "es": "Ocurrió un error grave, por favor reinicie la aplicación",
            "hi": "गंभीर त्रुटि हुई, कृपया एप्लिकेशन को पुनरारंभ करें"
        },
        "mirror_mode": {
            "zh": "镜像模式",
            "en": "Mirror Mode",
            "es": "Modo espejo",
            "hi": "दर्पण मोड"
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
        if language in ["zh", "en", "es", "hi"]:
            cls.current_language = language
            return True
        return False
