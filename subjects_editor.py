#!/usr/bin/env python3
"""
subjects_editor.py — Trình chỉnh sửa subjects.json
Chức năng: Thêm/Sửa/Xóa Môn học, Chương, Đề thi (link)
"""

import sys, json, os, copy
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QSplitter,
    QTreeWidget, QTreeWidgetItem, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QCheckBox, QFrame,
    QMessageBox, QFileDialog, QDialog, QDialogButtonBox,
    QAbstractItemView, QSizePolicy, QScrollArea, QGroupBox,
    QMenu, QAction, QToolBar, QStatusBar
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QFontDatabase

# ── Màu sắc & Style ──────────────────────────────────────────────────────────
STYLE = """
QMainWindow, QWidget {
    background-color: #0f1117;
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
}
QSplitter::handle {
    background: #1e2433;
    width: 2px;
}

/* Tree */
QTreeWidget {
    background-color: #141824;
    border: 1px solid #2a3146;
    border-radius: 8px;
    padding: 4px;
    color: #c8d3e8;
    outline: none;
}
QTreeWidget::item {
    padding: 6px 8px;
    border-radius: 5px;
    margin: 1px 2px;
}
QTreeWidget::item:selected {
    background-color: #2563eb;
    color: #ffffff;
}
QTreeWidget::item:hover:!selected {
    background-color: #1e2d4d;
}
QTreeWidget::branch {
    background: transparent;
}

/* Buttons */
QPushButton {
    background-color: #1e2433;
    color: #c8d3e8;
    border: 1px solid #2a3146;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #253050;
    border-color: #3b82f6;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #1d3a7a;
}
QPushButton#btn_primary {
    background-color: #2563eb;
    border-color: #2563eb;
    color: white;
    font-weight: 600;
}
QPushButton#btn_primary:hover {
    background-color: #1d4ed8;
}
QPushButton#btn_danger {
    background-color: #7f1d1d;
    border-color: #991b1b;
    color: #fca5a5;
}
QPushButton#btn_danger:hover {
    background-color: #991b1b;
    color: white;
}
QPushButton#btn_success {
    background-color: #14532d;
    border-color: #166534;
    color: #86efac;
}
QPushButton#btn_success:hover {
    background-color: #166534;
    color: white;
}

/* Input */
QLineEdit {
    background-color: #1a2035;
    border: 1px solid #2a3146;
    border-radius: 6px;
    padding: 7px 10px;
    color: #e2e8f0;
    selection-background-color: #2563eb;
}
QLineEdit:focus {
    border-color: #3b82f6;
    background-color: #1e2843;
}

/* CheckBox */
QCheckBox {
    color: #94a3b8;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px; height: 16px;
    border: 2px solid #2a3146;
    border-radius: 4px;
    background: #1a2035;
}
QCheckBox::indicator:checked {
    background: #2563eb;
    border-color: #2563eb;
}

/* GroupBox */
QGroupBox {
    border: 1px solid #2a3146;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 10px;
    color: #64748b;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

/* ScrollArea */
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical {
    background: #141824; width: 8px; border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #2a3146; border-radius: 4px; min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #3b4d70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* Frame separator */
QFrame[frameShape="4"], QFrame[frameShape="5"] {
    color: #1e2433;
}

/* Status bar */
QStatusBar {
    background: #0a0d14;
    color: #475569;
    border-top: 1px solid #1e2433;
    font-size: 11px;
}

/* Dialog */
QDialog {
    background-color: #0f1117;
}
QDialogButtonBox QPushButton {
    min-width: 80px;
}

/* Label */
QLabel#lbl_title {
    color: #f1f5f9;
    font-size: 18px;
    font-weight: 700;
}
QLabel#lbl_sub {
    color: #475569;
    font-size: 11px;
}
QLabel#lbl_tag {
    color: #3b82f6;
    background: #1e2d4d;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11px;
    font-weight: 600;
}
"""

# ── Dữ liệu mẫu mặc định ──────────────────────────────────────────────────────
DEFAULT_DATA = [
  {
    "id": "ELE13101",
    "name": "Xử Lý Tín Hiệu Số",
    "shortName": "ELE13101",
    "pass": "N24DCVT133",
    "chapters": [
      {
        "title": "Chương 1",
        "exams": [
          {"label": "Luyện Tập P1", "url": "https://azota.vn/de-thi/manguz"},
          {"label": "Luyện Tập P2", "url": "https://azota.vn/de-thi/k5kuwl"},
          {"label": "Đề FULL",      "url": "https://azota.vn/de-thi/5l7rjw", "full": True}
        ]
      }
    ]
  }
]

# ─────────────────────────────────────────────────────────────────────────────
# Exam Row Widget
# ─────────────────────────────────────────────────────────────────────────────
class ExamRow(QWidget):
    removed = pyqtSignal(object)

    def __init__(self, exam_data: dict, parent=None):
        super().__init__(parent)
        self.exam_data = exam_data
        self._build()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 3, 0, 3)
        lay.setSpacing(8)

        self.edt_label = QLineEdit(self.exam_data.get("label", ""))
        self.edt_label.setPlaceholderText("Tên đề (vd: Luyện Tập P1)")
        self.edt_label.setFixedWidth(160)

        self.edt_url = QLineEdit(self.exam_data.get("url", ""))
        self.edt_url.setPlaceholderText("URL https://azota.vn/...")

        self.chk_full = QCheckBox("FULL")
        self.chk_full.setChecked(self.exam_data.get("full", False))

        btn_del = QPushButton("✕")
        btn_del.setObjectName("btn_danger")
        btn_del.setFixedSize(30, 30)
        btn_del.setToolTip("Xóa đề này")
        btn_del.clicked.connect(lambda: self.removed.emit(self))

        lay.addWidget(self.edt_label)
        lay.addWidget(self.edt_url, 1)
        lay.addWidget(self.chk_full)
        lay.addWidget(btn_del)

    def get_data(self) -> dict:
        d = {
            "label": self.edt_label.text().strip(),
            "url":   self.edt_url.text().strip(),
        }
        if self.chk_full.isChecked():
            d["full"] = True
        return d


# ─────────────────────────────────────────────────────────────────────────────
# Chapter Panel
# ─────────────────────────────────────────────────────────────────────────────
class ChapterPanel(QWidget):
    removed = pyqtSignal(object)
    moved_up   = pyqtSignal(object)
    moved_down = pyqtSignal(object)

    def __init__(self, chapter_data: dict, parent=None):
        super().__init__(parent)
        self.chapter_data = chapter_data
        self.exam_rows: list[ExamRow] = []
        self._build()

    def _build(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        # Header bar
        header = QWidget()
        header.setStyleSheet("background:#141824; border-radius:7px;")
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(10, 6, 6, 6)
        hlay.setSpacing(8)

        self.edt_title = QLineEdit(self.chapter_data.get("title", ""))
        self.edt_title.setPlaceholderText("Tên chương")
        self.edt_title.setStyleSheet(
            "border:none; background:transparent; font-weight:600; font-size:14px; color:#e2e8f0;"
        )

        btn_up   = QPushButton("↑"); btn_up.setFixedSize(26,26); btn_up.setToolTip("Di chuyển lên")
        btn_down = QPushButton("↓"); btn_down.setFixedSize(26,26); btn_down.setToolTip("Di chuyển xuống")
        btn_del  = QPushButton("✕ Chương"); btn_del.setObjectName("btn_danger"); btn_del.setToolTip("Xóa chương")

        btn_up.clicked.connect(lambda: self.moved_up.emit(self))
        btn_down.clicked.connect(lambda: self.moved_down.emit(self))
        btn_del.clicked.connect(lambda: self.removed.emit(self))

        hlay.addWidget(QLabel("📚"), 0)
        hlay.addWidget(self.edt_title, 1)
        hlay.addWidget(btn_up)
        hlay.addWidget(btn_down)
        hlay.addWidget(btn_del)

        # Exam area
        self.exams_widget = QWidget()
        self.exams_layout = QVBoxLayout(self.exams_widget)
        self.exams_layout.setContentsMargins(14, 6, 6, 6)
        self.exams_layout.setSpacing(2)

        # Column header
        col_hdr = QWidget()
        col_lay = QHBoxLayout(col_hdr)
        col_lay.setContentsMargins(0,0,0,0)
        col_lay.setSpacing(8)
        l1 = QLabel("Tên Đề"); l1.setFixedWidth(160); l1.setStyleSheet("color:#475569;font-size:11px;")
        l2 = QLabel("URL Link"); l2.setStyleSheet("color:#475569;font-size:11px;")
        l3 = QLabel("Full"); l3.setFixedWidth(40); l3.setStyleSheet("color:#475569;font-size:11px;")
        l4 = QLabel(""); l4.setFixedWidth(30)
        col_lay.addWidget(l1); col_lay.addWidget(l2,1); col_lay.addWidget(l3); col_lay.addWidget(l4)
        self.exams_layout.addWidget(col_hdr)

        for exam in self.chapter_data.get("exams", []):
            self._add_exam_row(exam)

        # Add exam button
        btn_add_exam = QPushButton("+ Thêm Đề")
        btn_add_exam.setObjectName("btn_success")
        btn_add_exam.clicked.connect(lambda: self._add_exam_row({"label":"","url":""}))
        add_bar = QHBoxLayout()
        add_bar.setContentsMargins(14,4,6,6)
        add_bar.addWidget(btn_add_exam)
        add_bar.addStretch()

        # Separator
        sep = QFrame(); sep.setFrameShape(QFrame.HLine); sep.setStyleSheet("color:#1e2433;")

        main.addWidget(header)
        main.addWidget(self.exams_widget)
        add_lay = QWidget()
        add_lay.setLayout(add_bar)
        main.addWidget(add_lay)
        main.addWidget(sep)

    def _add_exam_row(self, exam_data: dict):
        row = ExamRow(exam_data)
        row.removed.connect(self._remove_exam_row)
        self.exam_rows.append(row)
        self.exams_layout.addWidget(row)

    def _remove_exam_row(self, row: ExamRow):
        self.exam_rows.remove(row)
        self.exams_layout.removeWidget(row)
        row.deleteLater()

    def get_data(self) -> dict:
        return {
            "title": self.edt_title.text().strip(),
            "exams": [r.get_data() for r in self.exam_rows]
        }


# ─────────────────────────────────────────────────────────────────────────────
# Subject Editor Panel (right side)
# ─────────────────────────────────────────────────────────────────────────────
class SubjectEditorPanel(QWidget):
    data_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._subject_data: dict | None = None
        self.chapter_panels: list[ChapterPanel] = []
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(0)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.content = QWidget()
        self.content_lay = QVBoxLayout(self.content)
        self.content_lay.setContentsMargins(20, 20, 20, 30)
        self.content_lay.setSpacing(16)

        scroll.setWidget(self.content)
        root.addWidget(scroll)

        self._show_placeholder()

    def _clear_content(self):
        while self.content_lay.count():
            item = self.content_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.chapter_panels.clear()

    def _show_placeholder(self):
        self._clear_content()
        lbl = QLabel("← Chọn một môn học để chỉnh sửa")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("color:#2a3146; font-size:16px; padding:60px;")
        self.content_lay.addWidget(lbl)
        self.content_lay.addStretch()

    def load_subject(self, subject_data: dict):
        self._subject_data = subject_data
        self._clear_content()

        # ── Header info ────────────────────────────────────────────────
        grp_info = QGroupBox("THÔNG TIN MÔN HỌC")
        form = QFormLayout(grp_info)
        form.setSpacing(10)
        form.setContentsMargins(14,16,14,14)

        self.edt_id        = QLineEdit(subject_data.get("id",""))
        self.edt_name      = QLineEdit(subject_data.get("name",""))
        self.edt_shortname = QLineEdit(subject_data.get("shortName",""))
        self.edt_pass      = QLineEdit(subject_data.get("pass",""))

        for w in [self.edt_id, self.edt_name, self.edt_shortname, self.edt_pass]:
            w.setMinimumWidth(300)

        form.addRow("Mã Môn (ID):",    self.edt_id)
        form.addRow("Tên Môn:",        self.edt_name)
        form.addRow("Tên Viết Tắt:",   self.edt_shortname)
        form.addRow("Mật Khẩu (pass):", self.edt_pass)

        self.content_lay.addWidget(grp_info)

        # ── Chapters ───────────────────────────────────────────────────
        grp_chap = QGroupBox("DANH SÁCH CHƯƠNG")
        grp_lay = QVBoxLayout(grp_chap)
        grp_lay.setContentsMargins(10,16,10,10)
        grp_lay.setSpacing(6)

        self.chapters_container = QVBoxLayout()
        self.chapters_container.setSpacing(4)
        grp_lay.addLayout(self.chapters_container)

        for ch in subject_data.get("chapters", []):
            self._add_chapter_panel(ch)

        btn_add_ch = QPushButton("+ Thêm Chương Mới")
        btn_add_ch.setObjectName("btn_primary")
        add_bar = QHBoxLayout()
        add_bar.addWidget(btn_add_ch)
        add_bar.addStretch()
        grp_lay.addLayout(add_bar)
        btn_add_ch.clicked.connect(lambda: self._add_chapter_panel({"title":"Chương mới","exams":[]}))

        self.content_lay.addWidget(grp_chap)
        self.content_lay.addStretch()

    def _add_chapter_panel(self, chapter_data: dict):
        panel = ChapterPanel(chapter_data)
        panel.removed.connect(self._remove_chapter)
        panel.moved_up.connect(self._move_chapter_up)
        panel.moved_down.connect(self._move_chapter_down)
        self.chapter_panels.append(panel)
        self.chapters_container.addWidget(panel)

    def _remove_chapter(self, panel: ChapterPanel):
        if QMessageBox.question(self, "Xác nhận", f"Xóa chương '{panel.edt_title.text()}'?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.chapter_panels.remove(panel)
            self.chapters_container.removeWidget(panel)
            panel.deleteLater()

    def _move_chapter_up(self, panel: ChapterPanel):
        idx = self.chapter_panels.index(panel)
        if idx == 0: return
        self.chapter_panels[idx], self.chapter_panels[idx-1] = self.chapter_panels[idx-1], self.chapter_panels[idx]
        self.chapters_container.removeWidget(panel)
        self.chapters_container.insertWidget(idx-1, panel)

    def _move_chapter_down(self, panel: ChapterPanel):
        idx = self.chapter_panels.index(panel)
        if idx >= len(self.chapter_panels)-1: return
        self.chapter_panels[idx], self.chapter_panels[idx+1] = self.chapter_panels[idx+1], self.chapter_panels[idx]
        self.chapters_container.removeWidget(panel)
        self.chapters_container.insertWidget(idx+1, panel)

    def get_current_data(self) -> dict | None:
        if self._subject_data is None:
            return None
        return {
            "id":        self.edt_id.text().strip(),
            "name":      self.edt_name.text().strip(),
            "shortName": self.edt_shortname.text().strip(),
            "pass":      self.edt_pass.text().strip(),
            "chapters":  [p.get_data() for p in self.chapter_panels]
        }


# ─────────────────────────────────────────────────────────────────────────────
# Main Window
# ─────────────────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("subjects.json — Trình Chỉnh Sửa")
        self.resize(1200, 780)
        self.subjects: list[dict] = []
        self.current_index: int = -1
        self.filepath: str = ""
        self._build_ui()
        self._load_initial()

    def _build_ui(self):
        # ── Toolbar ────────────────────────────────────────────────────
        tb = QToolBar("Main")
        tb.setMovable(False)
        tb.setIconSize(QSize(16,16))
        tb.setStyleSheet("QToolBar{background:#0a0d14;border-bottom:1px solid #1e2433;padding:4px 8px;spacing:6px;}")
        self.addToolBar(tb)

        # App name label
        lbl_app = QLabel("  📋  subjects.json")
        lbl_app.setStyleSheet("color:#3b82f6; font-weight:700; font-size:14px;")
        tb.addWidget(lbl_app)

        spacer = QWidget(); spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        tb.addWidget(spacer)

        btn_open = QPushButton("📂 Mở File")
        btn_open.clicked.connect(self.open_file)
        btn_save = QPushButton("💾 Lưu")
        btn_save.setObjectName("btn_primary")
        btn_save.clicked.connect(self.save_file)
        btn_saveas = QPushButton("💾 Lưu As...")
        btn_saveas.clicked.connect(self.save_file_as)

        for b in [btn_open, btn_save, btn_saveas]:
            tb.addWidget(b)

        # ── Central ────────────────────────────────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)
        main_lay.setContentsMargins(0,0,0,0)
        main_lay.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)

        # Left: subject list
        left = QWidget()
        left.setFixedWidth(260)
        left.setStyleSheet("background:#0a0d14; border-right:1px solid #1e2433;")
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(12,14,12,12)
        left_lay.setSpacing(10)

        lbl_list = QLabel("Danh Sách Môn")
        lbl_list.setStyleSheet("color:#64748b; font-size:11px; font-weight:600; letter-spacing:1px;")
        left_lay.addWidget(lbl_list)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setRootIsDecorated(False)
        self.tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tree.itemClicked.connect(self._on_subject_clicked)
        left_lay.addWidget(self.tree)

        # Buttons below list
        btn_add_subj = QPushButton("+ Thêm Môn")
        btn_add_subj.setObjectName("btn_primary")
        btn_add_subj.clicked.connect(self._add_subject)

        btn_del_subj = QPushButton("✕ Xóa Môn")
        btn_del_subj.setObjectName("btn_danger")
        btn_del_subj.clicked.connect(self._delete_subject)

        btn_dup = QPushButton("⧉ Nhân Bản")
        btn_dup.clicked.connect(self._duplicate_subject)

        for b in [btn_add_subj, btn_del_subj, btn_dup]:
            left_lay.addWidget(b)

        # Right: editor
        self.editor = SubjectEditorPanel()

        splitter.addWidget(left)
        splitter.addWidget(self.editor)
        splitter.setStretchFactor(1, 1)

        main_lay.addWidget(splitter)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.lbl_filepath = QLabel("Chưa mở file")
        self.lbl_filepath.setStyleSheet("color:#475569;")
        self.status.addWidget(self.lbl_filepath)
        self.lbl_count = QLabel()
        self.status.addPermanentWidget(self.lbl_count)

    # ── File operations ────────────────────────────────────────────────
    def _load_initial(self):
        # Try loading subjects.json from current dir
        if os.path.exists("subjects.json"):
            self._load_file("subjects.json")
        else:
            self.subjects = copy.deepcopy(DEFAULT_DATA)
            self._refresh_tree()
            self.lbl_filepath.setText("(Dữ liệu mẫu — chưa mở file)")

    def open_file(self):
        self._save_current_edits()
        path, _ = QFileDialog.getOpenFileName(self, "Mở subjects.json", "", "JSON files (*.json);;All (*)")
        if path:
            self._load_file(path)

    def _load_file(self, path: str):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                raise ValueError("File phải là JSON array")
            self.subjects = data
            self.filepath = path
            self.lbl_filepath.setText(f"  {path}")
            self.current_index = -1
            self.editor._show_placeholder()
            self._refresh_tree()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể đọc file:\n{e}")

    def save_file(self):
        self._save_current_edits()
        if not self.filepath:
            self.save_file_as()
            return
        self._write_file(self.filepath)

    def save_file_as(self):
        self._save_current_edits()
        path, _ = QFileDialog.getSaveFileName(self, "Lưu subjects.json", "subjects.json",
                                               "JSON files (*.json);;All (*)")
        if path:
            self.filepath = path
            self.lbl_filepath.setText(f"  {path}")
            self._write_file(path)

    def _write_file(self, path: str):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.subjects, f, ensure_ascii=False, indent=2)
            self.status.showMessage(f"✓ Đã lưu: {path}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể ghi file:\n{e}")

    # ── Tree management ────────────────────────────────────────────────
    def _refresh_tree(self):
        self.tree.clear()
        for i, subj in enumerate(self.subjects):
            name  = subj.get("name", f"Môn {i+1}")
            sid   = subj.get("id", "")
            item  = QTreeWidgetItem([f"  {name}"])
            item.setData(0, Qt.UserRole, i)
            item.setToolTip(0, f"ID: {sid}\nChương: {len(subj.get('chapters',[]))}")
            self.tree.addTopLevelItem(item)
        self.lbl_count.setText(f"{len(self.subjects)} môn học  ")

    def _on_subject_clicked(self, item: QTreeWidgetItem):
        self._save_current_edits()
        idx = item.data(0, Qt.UserRole)
        self.current_index = idx
        self.editor.load_subject(self.subjects[idx])

    def _save_current_edits(self):
        if self.current_index < 0:
            return
        data = self.editor.get_current_data()
        if data:
            self.subjects[self.current_index] = data
            # Update tree label
            item = self.tree.topLevelItem(self.current_index)
            if item:
                item.setText(0, f"  {data.get('name', '?')}")

    def _add_subject(self):
        self._save_current_edits()
        new_subj = {
            "id": f"NEW{len(self.subjects)+1:03d}",
            "name": "Môn Học Mới",
            "shortName": "NEW",
            "pass": "",
            "chapters": []
        }
        self.subjects.append(new_subj)
        self._refresh_tree()
        # Select new item
        last = self.tree.topLevelItem(len(self.subjects)-1)
        self.tree.setCurrentItem(last)
        self.current_index = len(self.subjects)-1
        self.editor.load_subject(new_subj)

    def _delete_subject(self):
        if self.current_index < 0:
            QMessageBox.information(self, "Thông báo", "Vui lòng chọn một môn để xóa.")
            return
        name = self.subjects[self.current_index].get("name", "?")
        if QMessageBox.question(self, "Xác nhận xóa",
                                f"Bạn có chắc muốn xóa môn:\n\n'{name}'?\n\nHành động này không thể hoàn tác.",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.subjects.pop(self.current_index)
            self.current_index = -1
            self.editor._show_placeholder()
            self._refresh_tree()

    def _duplicate_subject(self):
        if self.current_index < 0:
            QMessageBox.information(self, "Thông báo", "Vui lòng chọn một môn để nhân bản.")
            return
        self._save_current_edits()
        dup = copy.deepcopy(self.subjects[self.current_index])
        dup["name"] = dup["name"] + " (copy)"
        dup["id"]   = dup["id"]  + "_copy"
        self.subjects.append(dup)
        self._refresh_tree()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, "Thoát", "Bạn có muốn lưu trước khi thoát không?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )
        if reply == QMessageBox.Save:
            self.save_file()
            event.accept()
        elif reply == QMessageBox.Discard:
            event.accept()
        else:
            event.ignore()


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette base
    pal = QPalette()
    pal.setColor(QPalette.Window,          QColor("#0f1117"))
    pal.setColor(QPalette.WindowText,      QColor("#e2e8f0"))
    pal.setColor(QPalette.Base,            QColor("#141824"))
    pal.setColor(QPalette.AlternateBase,   QColor("#1a2035"))
    pal.setColor(QPalette.ToolTipBase,     QColor("#1e2433"))
    pal.setColor(QPalette.ToolTipText,     QColor("#e2e8f0"))
    pal.setColor(QPalette.Text,            QColor("#e2e8f0"))
    pal.setColor(QPalette.Button,          QColor("#1e2433"))
    pal.setColor(QPalette.ButtonText,      QColor("#c8d3e8"))
    pal.setColor(QPalette.Highlight,       QColor("#2563eb"))
    pal.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(pal)
    app.setStyleSheet(STYLE)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
