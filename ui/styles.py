from PyQt5.QtGui import QColor, QPalette


class AppStyles:
    """Application style definitions."""

    EXERCISE_COLORS = {
        "squat": "#6DB4FF",
        "pushup": "#E05C7B",
        "situp": "#7DD67A",
        "bicep_curl": "#F2AA4C",
        "tricep_extension": "#F2AA4C",
        "lateral_raise": "#B78CFF",
        "overhead_press": "#38D6B2",
        "leg_raise": "#FF8D5C",
        "knee_raise": "#4EC9D8",
        "knee_press": "#A88BFF",
        "crunch": "#7DD67A",
        "pullup": "#6DB4FF",
        "Squat": "#6DB4FF",
        "Push-up": "#E05C7B",
        "Push Up": "#E05C7B",
        "Sit-up": "#7DD67A",
        "Sit Up": "#7DD67A",
        "Bicep Curl": "#F2AA4C",
        "Tricep Extension": "#F2AA4C",
        "Lateral Raise": "#B78CFF",
        "Overhead Press": "#38D6B2",
        "Leg Raise": "#FF8D5C",
        "Knee Raise": "#4EC9D8",
        "Knee Press": "#A88BFF",
        "Left Knee Press": "#A88BFF",
        "Right Knee Press": "#8E75EF",
        "Crunch": "#7DD67A",
        "Pull-up": "#6DB4FF",
        "Pull Up": "#6DB4FF",
    }

    @staticmethod
    def get_window_palette():
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#05080C"))
        palette.setColor(QPalette.WindowText, QColor("#F4F7F5"))
        palette.setColor(QPalette.Base, QColor("#071018"))
        palette.setColor(QPalette.AlternateBase, QColor("#0A151D"))
        palette.setColor(QPalette.Text, QColor("#F4F7F5"))
        palette.setColor(QPalette.Button, QColor("#1A222B"))
        palette.setColor(QPalette.ButtonText, QColor("#F4F7F5"))
        palette.setColor(QPalette.Highlight, QColor("#38D6B2"))
        return palette

    @staticmethod
    def get_global_stylesheet():
        return """
            QWidget#RootSurface {
                background-color: #05080C;
            }
            QWidget {
                font-family: 'Segoe UI', 'Microsoft YaHei UI', Arial, sans-serif;
                font-size: 10pt;
                color: #F4F7F5;
                background-color: #05080C;
            }
            QLabel {
                color: #F4F7F5;
                background-color: transparent;
                letter-spacing: 0px;
            }
            QMainWindow {
                background-color: #05080C;
            }
            QMenuBar {
                background-color: #05080C;
                color: #D8E0E7;
                padding: 4px 8px;
                border-bottom: 1px solid #1E2832;
            }
            QMenuBar::item {
                background: transparent;
                padding: 6px 10px;
                border-radius: 6px;
            }
            QMenuBar::item:selected {
                background-color: #172028;
                color: #FFFFFF;
            }
            QMenu {
                background-color: #11171E;
                color: #EAF0F5;
                border: 1px solid #2A3541;
                padding: 6px;
            }
            QMenu::item {
                padding: 7px 26px 7px 12px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: #23313E;
            }
            QStatusBar {
                background-color: #05080C;
                color: #8AA0AD;
                border-top: 1px solid #15303A;
                padding: 4px 10px;
            }
            QFrame#TopBar {
                background-color: #071018;
                border: 1px solid #174353;
                border-radius: 8px;
            }
            QLabel#BrandLogo {
                background-color: #0B1620;
                border: 1px solid #1D5666;
                border-radius: 8px;
                color: #38D6B2;
                font-size: 18pt;
                font-weight: 900;
            }
            QLabel#BrandLabel {
                color: #FFFFFF;
                font-size: 18pt;
                font-weight: 800;
            }
            QLabel#MutedLabel {
                color: #8997A4;
                font-size: 9pt;
                font-weight: 600;
            }
            QLabel#TopMetaLabel {
                color: #B7C3CD;
                background-color: #151D25;
                border: 1px solid #263341;
                border-radius: 8px;
                padding: 7px 12px;
                font-size: 9pt;
                font-weight: 700;
            }
            QLabel#LivePill {
                color: #061210;
                background-color: #38D6B2;
                border-radius: 8px;
                padding: 7px 12px;
                font-size: 9pt;
                font-weight: 900;
            }
            QWidget#WorkoutView {
                background-color: transparent;
            }
            QFrame#VideoShell {
                background-color: #060A0F;
                border: 1px solid #153A49;
                border-radius: 8px;
            }
            QFrame#VideoHeader {
                background-color: transparent;
                border: none;
            }
            QLabel#SectionTitle {
                color: #F4F7F5;
                font-size: 12pt;
                font-weight: 800;
            }
            QSplitter#WorkoutSplitter::handle {
                background-color: transparent;
            }
            QFrame#StatusRail {
                background-color: #071018;
                border: 1px solid #174353;
                border-radius: 8px;
            }
            QLabel#RailTitle {
                color: #7CE5D2;
                font-size: 9pt;
                font-weight: 900;
            }
            QLabel#RailLabel {
                color: #8EA4B1;
                font-size: 9pt;
                font-weight: 800;
            }
            QLabel#RailCount {
                color: #38D6B2;
                background-color: #020806;
                border: 1px solid #2BE1BC;
                border-radius: 8px;
                font-size: 48pt;
                font-weight: 900;
            }
            QLabel#RailValue {
                color: #EAF6F3;
                font-size: 12pt;
                font-weight: 900;
            }
            QFrame#RailCountTile,
            QFrame#StatusTile {
                background-color: #0A151D;
                border: 1px solid #1A3B48;
                border-radius: 8px;
            }
            QFrame#ControlDock {
                background-color: #071018;
                border: 1px solid #174353;
                border-radius: 8px;
            }
            QFrame#DockField,
            QFrame#DockSwitches,
            QFrame#DockButtons {
                background-color: transparent;
                border: none;
            }
            QLabel#DockLabel {
                color: #8EA4B1;
                font-size: 8.5pt;
                font-weight: 800;
            }
            QScrollArea#ControlScroll {
                background-color: transparent;
                border: none;
            }
            QScrollArea#ControlScroll > QWidget > QWidget {
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 10px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background-color: #2B3946;
                border-radius: 5px;
                min-height: 36px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #3A4A58;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QComboBox {
                border: 1px solid #2A3541;
                border-radius: 7px;
                padding: 6px 10px;
                color: #EEF4F0;
                background-color: #0F151B;
            }
            QComboBox:hover {
                border-color: #38D6B2;
                background-color: #121A21;
            }
            QComboBox:focus {
                border-color: #6DB4FF;
            }
            QComboBox::drop-down {
                border: 0px;
                width: 28px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #2A3541;
                background-color: #10171E;
                color: #EEF4F0;
                selection-background-color: #21483F;
                selection-color: #FFFFFF;
                outline: 0px;
            }
        """

    @staticmethod
    def get_card_style():
        return """
            QFrame#PanelCard {
                background-color: #11171E;
                border: 1px solid #24303A;
                border-radius: 8px;
            }
            QFrame#CounterMetric {
                background-color: #0C1116;
                border: 1px solid #202B35;
                border-radius: 8px;
            }
            QFrame#SwitchList {
                background-color: transparent;
                border: none;
            }
        """

    @staticmethod
    def get_exercise_combo_style():
        return """
            QComboBox {
                font-size: 10.5pt;
                min-height: 24px;
                border: 1px solid #2A3541;
                border-radius: 7px;
                padding: 6px 10px;
                background-color: #0F151B;
                color: #EEF4F0;
            }
            QComboBox:hover {
                border-color: #38D6B2;
                background-color: #121A21;
            }
            QComboBox:focus {
                border-color: #6DB4FF;
            }
            QComboBox::drop-down {
                border: 0px;
                width: 28px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #2A3541;
                background-color: #10171E;
                color: #EEF4F0;
                selection-background-color: #21483F;
                selection-color: #FFFFFF;
            }
        """

    @staticmethod
    def get_counter_value_style(color="#38D6B2"):
        return f"""
            color: {color};
            background-color: #07100E;
            border-radius: 8px;
            padding: 6px;
            border: 1px solid {color};
            min-width: 104px;
            text-align: center;
            font-size: 42pt;
            font-weight: 900;
            letter-spacing: 0px;
        """

    @staticmethod
    def get_success_counter_style():
        return """
            color: #07100E;
            background-color: #38D6B2;
            border-radius: 8px;
            padding: 6px;
            border: 1px solid #38D6B2;
            min-width: 104px;
            text-align: center;
            font-size: 42pt;
            font-weight: 900;
        """

    @staticmethod
    def get_angle_value_style(color="#38D6B2", highlight=False):
        border_color = "#E05C7B" if highlight else color
        text_color = "#E05C7B" if highlight else color
        return f"""
            color: {text_color};
            background-color: #0C1116;
            border-radius: 8px;
            padding: 6px;
            border: 1px solid {border_color};
            min-width: 100px;
            text-align: center;
            font-size: 30pt;
            font-weight: 800;
        """

    @staticmethod
    def get_phase_indicator_style(active=False, color="#38D6B2"):
        bg_color = color if active else "#0F151B"
        text_color = "#07100E" if active else "#738291"
        border_color = color if active else "#2A3541"
        return f"""
            font-size: 10pt;
            color: {text_color};
            background-color: {bg_color};
            border: 1px solid {border_color};
            border-radius: 8px;
            font-weight: 900;
            letter-spacing: 0px;
        """

    @staticmethod
    def get_group_box_style():
        return """
            QGroupBox {
                font-weight: 800;
                color: #BAC6D0;
                background-color: #11171E;
                border: 1px solid #24303A;
                border-radius: 8px;
                margin-top: 14px;
                padding: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #8F9DAA;
                background-color: #0A0D10;
            }
        """

    @staticmethod
    def get_phase_group_style():
        return AppStyles.get_group_box_style()

    @staticmethod
    def get_camera_combo_style():
        return AppStyles.get_exercise_combo_style()

    @staticmethod
    def get_increase_button_style():
        return AppStyles._button_style("#38D6B2", "#061210", "#4BE1C0", "#25BA99")

    @staticmethod
    def get_decrease_button_style():
        return AppStyles._button_style("#F2AA4C", "#171009", "#F7BC6E", "#D98E32")

    @staticmethod
    def get_reset_button_style():
        return AppStyles._button_style("#1B2530", "#D5DEE6", "#25313D", "#141B23", border="#33424F")

    @staticmethod
    def get_confirm_button_style():
        return AppStyles._button_style("#6DB4FF", "#07101A", "#88C4FF", "#509DEA")

    @staticmethod
    def get_success_button_style():
        return AppStyles._button_style("#38D6B2", "#061210", "#4BE1C0", "#25BA99")

    @staticmethod
    def _button_style(bg, fg, hover, pressed, border="transparent"):
        border_rule = "none" if border == "transparent" else f"1px solid {border}"
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: {border_rule};
                border-radius: 8px;
                padding: 8px 10px;
                font-weight: 900;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:pressed {{
                background-color: {pressed};
            }}
            QPushButton:disabled {{
                background-color: #202932;
                color: #65727E;
                border: 1px solid #2A3541;
            }}
        """

    @staticmethod
    def get_panel_title_style():
        return """
            color: #FFFFFF;
            font-size: 21pt;
            font-weight: 900;
            padding: 0px;
            letter-spacing: 0px;
        """

    @staticmethod
    def get_field_label_style():
        return """
            color: #8F9DAA;
            font-size: 9.5pt;
            font-weight: 700;
            padding: 0px;
        """

    @staticmethod
    def get_section_label_style():
        return """
            color: #F4F7F5;
            font-size: 11.5pt;
            font-weight: 900;
        """

    @staticmethod
    def get_stage_value_style():
        return """
            color: #DFF8F3;
            background-color: #0C1116;
            border: 1px solid #24303A;
            border-radius: 8px;
            font-size: 15pt;
            font-weight: 900;
        """

    @staticmethod
    def get_toggle_button_style(checked=False):
        if checked:
            return AppStyles._button_style("#38D6B2", "#061210", "#4BE1C0", "#25BA99")
        return AppStyles._button_style("#1B2530", "#D5DEE6", "#25313D", "#141B23", border="#33424F")
