#!/usr/bin/env python3
"""测试GUI是否能正常启动"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget

app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("测试窗口")
window.setMinimumSize(400, 300)

central = QWidget()
layout = QVBoxLayout(central)
layout.addWidget(QLabel("如果你看到这个窗口，说明PyQt6工作正常"))
btn = QPushButton("点击测试")
btn.clicked.connect(lambda: print("按钮被点击"))
layout.addWidget(btn)

window.setCentralWidget(central)
window.show()

print("窗口已显示，进入事件循环")
sys.exit(app.exec())