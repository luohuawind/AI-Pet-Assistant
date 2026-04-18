# -*- coding: utf-8 -*-
import sys
import os
import json
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# ===================== 配置区 =====================
ZHIPU_API_KEY = os.environ.get("ZHIPU_API_KEY", "请在这里填入你的智谱API密钥")
AUTOCLAW_URL = os.environ.get("AUTOCLAW_URL", "http://localhost:8000")
# =============================================================

# AutoClaw客户端
class AutoClawClient:
    def __init__(self, base_url=AUTOCLAW_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30

    def run_task(self, prompt):
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/tasks",
                json={
                    "prompt": prompt,
                    "model": "glm-4-flash",
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                logs = result.get("logs", [])
                final_output = logs[-1]["content"] if logs else "任务执行成功！"
                return f"✅ {final_output}"
            else:
                return f"❌ 网关连接失败：{response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "❌ AutoClaw未启动！请先打开智谱澳龙客户端"
        except Exception as e:
            return f"❌ 执行异常：{str(e)[:50]}..."

# 情绪面板
class EmotionPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(120, 200)
        self.setStyleSheet("""
            background-color: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 8px;
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8,8,8,8)
        layout.setSpacing(6)
        self.bars = {}
        
        emotion_styles = {
            "生气": "#ff4444",
            "难过": "#33b5e5",
            "开心": "#ffcc00",
            "麻木": "#999999",
            "期待值": "#00cc99"
        }
        
        for name, color in emotion_styles.items():
            lab = QLabel(name)
            lab.setStyleSheet(f"color:white; font-size:12px; font-family: 'Microsoft YaHei';")
            bar = QProgressBar()
            bar.setFixedHeight(8)
            bar.setRange(0,100)
            bar.setTextVisible(False)
            bar.setStyleSheet(f"""
                QProgressBar{{background:rgba(255,255,255,0.2); border-radius:4px; border:1px solid rgba(255,255,255,0.3);}}
                QProgressBar::chunk{{background:{color}; border-radius:4px;}}
            """)
            layout.addWidget(lab)
            layout.addWidget(bar)
            self.bars[name] = bar

    def update_emotion(self, emotion_dict):
        for emo_name, value in emotion_dict.items():
            if emo_name in self.bars:
                self.bars[emo_name].setValue(max(0, min(100, value)))

# 主桌宠窗口
class SmartPetWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 650)

        self.emotion = {"生气":0, "难过":20, "开心":30, "麻木":40, "期待值":50}
        self.auto_claw = AutoClawClient()
        self.ai_messages = [{"role":"system", "content":"你是聪明的猫耳少年桌宠池年，会用AutoClaw帮用户操作电脑，说话可爱简短，20字以内。"}]

        self._init_ui()
        self.dragging = False
        self.drag_offset = QPoint()

    def _init_ui(self):
        self.emo_panel = EmotionPanel(self)
        self.emo_panel.setGeometry(10, 10, 120, 200)
        self.emo_panel.update_emotion(self.emotion)

        self.pet_label = QLabel(self)
        self.pet_label.setGeometry(140, 50, 300, 500)
        self.pet_label.setAlignment(Qt.AlignCenter)
        self.change_expression("xiyue")

    def change_expression(self, expr_name):
        expr_map = {
            "normal": "xiyue",
            "happy": "happy",
            "sad": "weiqv",
            "angry": "shengqi",
            "excited": "jingxi",
            "sleep": "shuijiao"
        }
        img_name = expr_map.get(expr_name, "xiyue") + ".png"
        try:
            pixmap = QPixmap(img_name)
            if not pixmap.isNull():
                self.pet_label.setPixmap(pixmap.scaled(300, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.pet_label.setStyleSheet("border: none;")
            else:
                self.pet_label.setStyleSheet("""
                    background-color: rgba(255,107,107,0.3);
                    border-radius: 30px;
                    color: white;
                    font-size: 24px;
                """)
                self.pet_label.setText(f"找不到{img_name}\n请检查文件名")
        except:
            self.pet_label.setStyleSheet("background-color: rgba(255,107,107,0.3); border-radius: 30px;")
            self.pet_label.setText("池年\n(AI智能助手)")

    def set_mood(self, mood):
        mood_config = {
            "normal": {"text": "池年\n（待机😐）", "happy":0, "sad":0},
            "happy": {"text": "池年\n（开心🥰）", "happy":+15, "sad":-10},
            "sad": {"text": "池年\n（难过😢）", "happy":-10, "sad":+15},
            "angry": {"text": "池年\n（生气😠）", "happy":-20, "angry":+10},
            "excited": {"text": "池年\n（期待🥳）", "happy":+20, "expect":+15}
        }
        cfg = mood_config.get(mood, mood_config["normal"])
        
        self.emotion["开心"] += cfg["happy"]
        self.emotion["难过"] += cfg.get("sad", 0)
        self.emotion["生气"] += cfg.get("angry", 0)
        self.emotion["期待值"] += cfg.get("expect", 0)
        self.emotion["麻木"] = max(0, self.emotion["麻木"] - 5)
        
        self.emo_panel.update_emotion(self.emotion)
        self.change_expression(mood)

    # ===================== 修复：对话框自动适应文字高度，避免重叠 =====================
    def show_speech_bubble(self, text):
        bubble = QLabel(text, self)
        # 先计算文字所需高度
        font_metrics = QFontMetrics(bubble.font())
        text_rect = font_metrics.boundingRect(QRect(0, 0, 280, 1000), Qt.AlignCenter | Qt.TextWordWrap, text)
        bubble_height = text_rect.height() + 24  # 加上上下padding
        
        # 动态设置气泡高度，保证文字完全显示
        bubble.setGeometry(100, 520, 300, max(60, bubble_height))
        bubble.setStyleSheet("""
            background-color: rgba(255,255,255,0.2);
            color: #ffffff;
            padding: 12px 16px;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.3);
            font-size: 14px;
            font-family: 'Microsoft YaHei';
            line-height: 1.5;
        """)
        bubble.setAlignment(Qt.AlignCenter)
        bubble.setWordWrap(True)
        bubble.show()
        QTimer.singleShot(3500, bubble.deleteLater)

    # 鼠标拖动逻辑
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_offset = e.globalPos() - self.pos()

    def mouseMoveEvent(self, e):
        if self.dragging:
            new_pos = e.globalPos() - self.drag_offset
            screen_geo = QApplication.desktop().availableGeometry()
            new_x = max(0, min(new_pos.x(), screen_geo.width() - self.width()))
            new_y = max(0, min(new_pos.y(), screen_geo.height() - self.height()))
            self.move(new_x, new_y)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = False
            if self.pet_label.geometry().contains(e.pos()):
                self.show_function_menu()

    def show_function_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(255,255,255,0.15);
                color: white;
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.3);
                font-size: 14px;
                padding: 6px;
            }
            QMenu::item {
                padding: 10px 28px;
                border-radius: 6px;
            }
            QMenu::item:selected {
                background-color: rgba(255,255,255,0.3);
            }
        """)

        menu.addAction("摸头😘", self.on_pet_head)
        menu.addAction("AI聊天💬", self.on_ai_chat)
        menu.addAction("智能操作💻", self.on_auto_claw)
        menu.addAction("睡觉💤", self.on_sleep)
        menu.addAction("重置情绪🔄", self.reset_emotion)

        menu.exec_(QCursor.pos())

    # ===== 修复版：自定义AI聊天弹窗 =====
    def on_ai_chat(self):
        dialog = QDialog(self, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        dialog.setFixedSize(320, 180)
        dialog.move(self.geometry().center().x() - 160, self.geometry().center().y() + 120)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        label = QLabel("想和我说什么？")
        label.setStyleSheet("color: white; font-size: 16px; font-family: 'Microsoft YaHei';")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        input_edit = QLineEdit()
        input_edit.setPlaceholderText("在这里输入...")
        input_edit.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255,255,255,0.1);
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        layout.addWidget(input_edit)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)

        send_btn = QPushButton("发送")
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.9);
                color: #333;
                border: none;
                border-radius: 15px;
                padding: 10px 25px;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,1);
            }
        """)

        cancel_btn = QPushButton("算了")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,0.9);
                color: #333;
                border: none;
                border-radius: 15px;
                padding: 10px 25px;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,1);
            }
        """)

        btn_layout.addWidget(send_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        dialog.setStyleSheet("""
            QDialog {
                background-color: rgba(0,0,0,0.6);
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.2);
            }
        """)

        def on_send():
            text = input_edit.text().strip()
            if text:
                self.ai_messages.append({"role":"user", "content":text})
                self.show_speech_bubble(f"你：{text[:15]}...")
                QTimer.singleShot(100, lambda: self._get_ai_reply(text))
            dialog.close()

        send_btn.clicked.connect(on_send)
        cancel_btn.clicked.connect(dialog.close)
        input_edit.returnPressed.connect(on_send)

        dialog.exec_()

    def _get_ai_reply(self, user_input):
        try:
            response = requests.post(
                "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                headers={
                    "Authorization": f"Bearer {ZHIPU_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "glm-4-flash",
                    "messages": self.ai_messages,
                    "temperature": 0.8,
                    "max_tokens": 256
                },
                timeout=10
            )
            
            if response.status_code == 200:
                reply = response.json()["choices"][0]["message"]["content"]
                self.ai_messages.append({"role":"assistant", "content":reply})
                self.show_speech_bubble(reply)
                
                if any(word in reply for word in ["开心", "喜欢", "舒服", "好耶"]):
                    self.set_mood("happy")
                elif any(word in reply for word in ["难过", "委屈", "孤单"]):
                    self.set_mood("sad")
                elif any(word in reply for word in ["生气", "讨厌", "走开"]):
                    self.set_mood("angry")
                elif any(word in reply for word in ["期待", "好耶", "太棒了"]):
                    self.set_mood("excited")
            else:
                self.show_speech_bubble("网络有点卡～等下再聊嘛😣")
        except:
            self.show_speech_bubble("连不上AI啦～抱抱我🥺")

    def on_pet_head(self):
        self.show_speech_bubble("呜～主人摸头好舒服🥰")
        self.set_mood("happy")

    def on_auto_claw(self):
        user_cmd, ok = QInputDialog.getText(self, "AI智能操作", "想让我帮你做什么？\n示例：\n1. 在桌面新建学习文件夹\n2. 打开浏览器搜智谱AI\n3. 新建文本文档写hello world", QLineEdit.Normal, "")
        if ok and user_cmd.strip():
            self.show_speech_bubble(f"正在执行：{user_cmd[:15]}...")
            self.set_mood("excited")
            QTimer.singleShot(200, lambda: self._run_auto_claw_task(user_cmd))

    def _run_auto_claw_task(self, user_cmd):
        result = self.auto_claw.run_task(user_cmd)
        self.show_speech_bubble(result)
        
        if "✅" in result:
            self.set_mood("happy")
        else:
            self.set_mood("sad")

    def on_sleep(self):
        self.show_speech_bubble("呼～我去睡觉啦💤")
        self.change_expression("sleep")
        self.emotion = {"生气":0, "难过":10, "开心":10, "麻木":80, "期待值":20}
        self.emo_panel.update_emotion(self.emotion)

    def reset_emotion(self):
        self.emotion = {"生气":0, "难过":20, "开心":30, "麻木":40, "期待值":50}
        self.emo_panel.update_emotion(self.emotion)
        self.set_mood("normal")
        self.show_speech_bubble("情绪重置啦～我又元气满满😜")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = SmartPetWindow()
    pet.show()
    sys.exit(app.exec_())