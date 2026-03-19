#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案件工作台 - 答辩状模板管理
支持查看、复制、编辑、删除自定义模板
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit,
    QListWidget, QListWidgetItem, QDialog, QMessageBox,
    QGroupBox, QSplitter, QTabWidget, QCheckBox,
    QDialogButtonBox, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.case_workbench.models import (
    CaseWorkbenchManager, DefenseTemplate, CASE_CAUSES
)


class ParagraphEditDialog(QDialog):
    """段落编辑对话框"""
    def __init__(self, paragraph_data: dict = None, parent=None):
        super().__init__(parent)
        self.paragraph_data = paragraph_data or {}
        self.setWindowTitle("编辑段落" if paragraph_data else "添加段落")
        self.setMinimumSize(600, 400)
        self._create_ui()
        if paragraph_data:
            self._load_data()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        
        # 段落类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("段落类型："))
        
        self.type_fixed_radio = QCheckBox("固定段落")
        self.type_optional_radio = QCheckBox("可选段落")
        self.type_fixed_radio.stateChanged.connect(self._on_type_changed)
        self.type_optional_radio.stateChanged.connect(self._on_type_changed)
        type_layout.addWidget(self.type_fixed_radio)
        type_layout.addWidget(self.type_optional_radio)
        type_layout.addStretch()
        
        layout.addLayout(type_layout)
        
        # 段落标题
        form_layout = QFormLayout()
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("段落标题，如：确认劳动关系缺失")
        form_layout.addRow("段落标题*：", self.title_input)
        layout.addLayout(form_layout)
        
        # 段落内容
        layout.addWidget(QLabel("段落内容*："))
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("输入段落内容，可用占位符：{plaintiff} {defendant} {third_party} {date} ...")
        layout.addWidget(self.content_edit)
        
        # 占位符说明
        help_text = QLabel(
            "占位符说明：{plaintiff}=原告 {defendant}=被告 {court}=法院 "
            "{case_cause}=案由 {lawyer_name}=律师 {law_firm}=律所 "
            "{date}=当前日期 {third_party}=第三方公司"
        )
        help_text.setStyleSheet("color: #666666; font-size: 11px;")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        
        # 按钮
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self._save)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
    
    def _on_type_changed(self):
        """类型切换互斥"""
        sender = self.sender()
        if sender == self.type_fixed_radio and self.type_fixed_radio.isChecked():
            self.type_optional_radio.setChecked(False)
        elif sender == self.type_optional_radio and self.type_optional_radio.isChecked():
            self.type_fixed_radio.setChecked(False)
    
    def _load_data(self):
        """加载数据"""
        self.title_input.setText(self.paragraph_data.get('title', ''))
        self.content_edit.setPlainText(self.paragraph_data.get('content', ''))
        
        ptype = self.paragraph_data.get('type', 'optional')
        if ptype == 'fixed':
            self.type_fixed_radio.setChecked(True)
        else:
            self.type_optional_radio.setChecked(True)
    
    def _save(self):
        """保存"""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "提示", "请输入段落标题")
            return
        
        content = self.content_edit.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "提示", "请输入段落内容")
            return
        
        ptype = 'fixed' if self.type_fixed_radio.isChecked() else 'optional'
        
        self.result_data = {
            'type': ptype,
            'title': title,
            'content': content
        }
        
        self.accept()
    
    def get_data(self) -> dict:
        """获取数据"""
        return getattr(self, 'result_data', {})


class TemplateEditDialog(QDialog):
    """模板编辑对话框"""
    saved = pyqtSignal()
    
    def __init__(self, manager: CaseWorkbenchManager, template: DefenseTemplate = None, 
                 base_template: DefenseTemplate = None, parent=None):
        """
        模板编辑对话框
        
        Args:
            manager: 案件管理器
            template: 编辑的模板（None表示新建）
            base_template: 基于哪个模板复制（用于复制内置模板）
            parent: 父窗口
        """
        super().__init__(parent)
        self.manager = manager
        self.template = template
        self.base_template = base_template
        self.is_edit = template is not None
        
        title = "编辑模板" if self.is_edit else ("复制模板" if base_template else "新建模板")
        self.setWindowTitle(title)
        self.setMinimumSize(900, 700)
        
        self.paragraphs = {
            'header': None,
            'facts_options': [],
            'defense_options': [],
            'legal_basis': {'type': 'selectable', 'title': '法律依据', 'options': []},
            'footer': None
        }
        
        self._create_ui()
        self._load_data()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        
        # 基本信息
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("模板名称")
        basic_layout.addRow("模板名称*：", self.name_input)
        
        self.case_cause_combo = QComboBox()
        self.case_cause_combo.addItems(CASE_CAUSES)
        basic_layout.addRow("适用案由*：", self.case_cause_combo)
        
        layout.addWidget(basic_group)
        
        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：段落列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        left_layout.addWidget(QLabel("段落结构："))
        
        self.paragraph_list = QListWidget()
        self.paragraph_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        self.paragraph_list.itemDoubleClicked.connect(self._edit_paragraph)
        left_layout.addWidget(self.paragraph_list)
        
        # 段落操作按钮
        btn_layout = QHBoxLayout()
        
        add_fact_btn = QPushButton("+ 事实段落")
        add_fact_btn.clicked.connect(lambda: self._add_paragraph('facts'))
        btn_layout.addWidget(add_fact_btn)
        
        add_defense_btn = QPushButton("+ 抗辩段落")
        add_defense_btn.clicked.connect(lambda: self._add_paragraph('defense'))
        btn_layout.addWidget(add_defense_btn)
        
        add_legal_btn = QPushButton("+ 法律依据")
        add_legal_btn.clicked.connect(self._add_legal_basis)
        btn_layout.addWidget(add_legal_btn)
        
        left_layout.addLayout(btn_layout)
        
        move_layout = QHBoxLayout()
        
        up_btn = QPushButton("↑ 上移")
        up_btn.clicked.connect(self._move_up)
        move_layout.addWidget(up_btn)
        
        down_btn = QPushButton("↓ 下移")
        down_btn.clicked.connect(self._move_down)
        move_layout.addWidget(down_btn)
        
        delete_btn = QPushButton("🗑 删除")
        delete_btn.setStyleSheet("color: #f44336;")
        delete_btn.clicked.connect(self._delete_paragraph)
        move_layout.addWidget(delete_btn)
        
        left_layout.addLayout(move_layout)
        
        splitter.addWidget(left_widget)
        
        # 右侧：预览
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        right_layout.addWidget(QLabel("段落预览："))
        
        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                font-family: "SimSun", "宋体", serif;
            }
        """)
        right_layout.addWidget(self.preview_edit)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 500])
        
        layout.addWidget(splitter)
        
        # 按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存模板")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        save_btn.clicked.connect(self._save)
        bottom_layout.addWidget(save_btn)
        
        layout.addLayout(bottom_layout)
    
    def _load_data(self):
        """加载模板数据"""
        source = self.template or self.base_template
        
        if source:
            self.name_input.setText(source.template_name)
            
            index = self.case_cause_combo.findText(source.case_cause)
            if index >= 0:
                self.case_cause_combo.setCurrentIndex(index)
            
            # 加载段落
            sections = source.paragraph_sections
            self.paragraphs['header'] = sections.get('header')
            self.paragraphs['facts_options'] = sections.get('facts_options', [])
            self.paragraphs['defense_options'] = sections.get('defense_options', [])
            self.paragraphs['legal_basis'] = sections.get('legal_basis', {'type': 'selectable', 'title': '法律依据', 'options': []})
            self.paragraphs['footer'] = sections.get('footer')
            
            self._refresh_paragraph_list()
    
    def _refresh_paragraph_list(self):
        """刷新段落列表"""
        self.paragraph_list.clear()
        
        # 头部
        if self.paragraphs['header']:
            item = QListWidgetItem(f"📄 头部（固定）：{self.paragraphs['header'].get('title', '无标题')}")
            item.setData(Qt.ItemDataRole.UserRole, ('header', 0))
            self.paragraph_list.addItem(item)
        
        # 事实段落
        for i, fact in enumerate(self.paragraphs['facts_options']):
            item = QListWidgetItem(f"📋 事实段落{i+1}：{fact.get('title', '无标题')}")
            item.setData(Qt.ItemDataRole.UserRole, ('facts', i))
            self.paragraph_list.addItem(item)
        
        # 抗辩段落
        for i, defense in enumerate(self.paragraphs['defense_options']):
            item = QListWidgetItem(f"⚖️ 抗辩段落{i+1}：{defense.get('title', '无标题')}")
            item.setData(Qt.ItemDataRole.UserRole, ('defense', i))
            self.paragraph_list.addItem(item)
        
        # 法律依据
        legal = self.paragraphs['legal_basis']
        if legal and legal.get('options'):
            item = QListWidgetItem(f"📚 法律依据（{len(legal['options'])}条）")
            item.setData(Qt.ItemDataRole.UserRole, ('legal', 0))
            self.paragraph_list.addItem(item)
        
        # 尾部
        if self.paragraphs['footer']:
            item = QListWidgetItem(f"📄 尾部（固定）：{self.paragraphs['footer'].get('title', '无标题')}")
            item.setData(Qt.ItemDataRole.UserRole, ('footer', 0))
            self.paragraph_list.addItem(item)
    
    def _add_paragraph(self, ptype: str):
        """添加段落"""
        dialog = ParagraphEditDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if ptype == 'facts':
                self.paragraphs['facts_options'].append(data)
            else:
                self.paragraphs['defense_options'].append(data)
            self._refresh_paragraph_list()
    
    def _add_legal_basis(self):
        """添加法律依据"""
        text, ok = QInputDialog.getText(
            self, "添加法律依据", 
            "输入法律条文，如：《劳动合同法》第47条"
        )
        if ok and text.strip():
            if 'options' not in self.paragraphs['legal_basis']:
                self.paragraphs['legal_basis']['options'] = []
            self.paragraphs['legal_basis']['options'].append(text.strip())
            self._refresh_paragraph_list()
    
    def _edit_paragraph(self, item: QListWidgetItem):
        """编辑段落"""
        ptype, index = item.data(Qt.ItemDataRole.UserRole)
        
        if ptype == 'header':
            dialog = ParagraphEditDialog(self.paragraphs['header'], self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.paragraphs['header'] = dialog.get_data()
                self._refresh_paragraph_list()
                
        elif ptype == 'facts':
            dialog = ParagraphEditDialog(self.paragraphs['facts_options'][index], self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.paragraphs['facts_options'][index] = dialog.get_data()
                self._refresh_paragraph_list()
                
        elif ptype == 'defense':
            dialog = ParagraphEditDialog(self.paragraphs['defense_options'][index], self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.paragraphs['defense_options'][index] = dialog.get_data()
                self._refresh_paragraph_list()
    
    def _move_up(self):
        """上移段落"""
        current = self.paragraph_list.currentRow()
        if current <= 0:
            return
        
        item = self.paragraph_list.item(current)
        ptype, index = item.data(Qt.ItemDataRole.UserRole)
        
        if ptype == 'facts' and index > 0:
            self.paragraphs['facts_options'][index], self.paragraphs['facts_options'][index-1] = \
                self.paragraphs['facts_options'][index-1], self.paragraphs['facts_options'][index]
            self._refresh_paragraph_list()
            self.paragraph_list.setCurrentRow(current - 1)
            
        elif ptype == 'defense' and index > 0:
            self.paragraphs['defense_options'][index], self.paragraphs['defense_options'][index-1] = \
                self.paragraphs['defense_options'][index-1], self.paragraphs['defense_options'][index]
            self._refresh_paragraph_list()
            self.paragraph_list.setCurrentRow(current - 1)
    
    def _move_down(self):
        """下移段落"""
        current = self.paragraph_list.currentRow()
        if current < 0 or current >= self.paragraph_list.count() - 1:
            return
        
        item = self.paragraph_list.item(current)
        ptype, index = item.data(Qt.ItemDataRole.UserRole)
        
        if ptype == 'facts' and index < len(self.paragraphs['facts_options']) - 1:
            self.paragraphs['facts_options'][index], self.paragraphs['facts_options'][index+1] = \
                self.paragraphs['facts_options'][index+1], self.paragraphs['facts_options'][index]
            self._refresh_paragraph_list()
            self.paragraph_list.setCurrentRow(current + 1)
            
        elif ptype == 'defense' and index < len(self.paragraphs['defense_options']) - 1:
            self.paragraphs['defense_options'][index], self.paragraphs['defense_options'][index+1] = \
                self.paragraphs['defense_options'][index+1], self.paragraphs['defense_options'][index]
            self._refresh_paragraph_list()
            self.paragraph_list.setCurrentRow(current + 1)
    
    def _delete_paragraph(self):
        """删除段落"""
        current = self.paragraph_list.currentRow()
        if current < 0:
            return
        
        item = self.paragraph_list.item(current)
        ptype, index = item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self, "确认删除", "确定要删除这个段落吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        if ptype == 'facts':
            del self.paragraphs['facts_options'][index]
        elif ptype == 'defense':
            del self.paragraphs['defense_options'][index]
        elif ptype == 'legal':
            self.paragraphs['legal_basis']['options'] = []
        
        self._refresh_paragraph_list()
    
    def _save(self):
        """保存模板"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入模板名称")
            return
        
        case_cause = self.case_cause_combo.currentText()
        
        # 收集段落
        paragraph_sections = {
            'header': self.paragraphs['header'],
            'facts_options': self.paragraphs['facts_options'],
            'defense_options': self.paragraphs['defense_options'],
            'legal_basis': self.paragraphs['legal_basis'],
            'footer': self.paragraphs['footer']
        }
        
        # 收集常见抗辩要点和法律依据
        common_defenses = [p.get('title', '') for p in self.paragraphs['defense_options']]
        legal_basis = self.paragraphs['legal_basis'].get('options', [])
        
        try:
            if self.is_edit:
                self.manager.update_template(
                    self.template.id,
                    template_name=name,
                    paragraph_sections=paragraph_sections,
                    common_defenses=common_defenses,
                    legal_basis=legal_basis
                )
            else:
                self.manager.add_template(
                    case_cause=case_cause,
                    template_name=name,
                    paragraph_sections=paragraph_sections,
                    common_defenses=common_defenses,
                    legal_basis=legal_basis,
                    is_builtin=False
                )
            
            self.saved.emit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))


class TemplateManagerWidget(QWidget):
    """模板管理主界面"""
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.manager = CaseWorkbenchManager(db.conn)
        self._create_ui()
        self._load_templates()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 标题栏
        header_layout = QHBoxLayout()
        
        title = QLabel("📝 答辩状模板管理")
        title_font = QFont("PingFang SC", 16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #1976d2;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # 筛选
        self.case_cause_filter = QComboBox()
        self.case_cause_filter.addItem("全部案由")
        self.case_cause_filter.addItems(CASE_CAUSES)
        self.case_cause_filter.currentTextChanged.connect(self._load_templates)
        header_layout.addWidget(QLabel("案由筛选："))
        header_layout.addWidget(self.case_cause_filter)
        
        # 新建按钮
        add_btn = QPushButton("➕ 新建模板")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_btn.clicked.connect(self._add_template)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # 模板列表
        self.template_list = QListWidget()
        self.template_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background-color: #fafafa;
            }
            QListWidget::item {
                background-color: white;
                margin: 6px 10px;
                padding: 12px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
                border-color: #1976d2;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-color: #1976d2;
            }
        """)
        self.template_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.template_list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.template_list)
        
        # 说明
        help_label = QLabel(
            "💡 提示：内置模板不可直接修改，但可复制后创建自定义模板。"
            "自定义模板支持段落增删改、排序调整。"
        )
        help_label.setStyleSheet("color: #666666; font-size: 11px;")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
    
    def _load_templates(self):
        """加载模板列表"""
        self.template_list.clear()
        
        case_cause = self.case_cause_filter.currentText()
        if case_cause == "全部案由":
            # 获取所有案由的模板
            templates = []
            for cause in CASE_CAUSES:
                templates.extend(self.manager.get_templates_by_case_cause(cause))
        else:
            templates = self.manager.get_templates_by_case_cause(case_cause)
        
        for template in templates:
            item = QListWidgetItem()
            
            # 类型标记
            type_mark = "[内置]" if template.is_builtin else "[自定义]"
            
            # 段落数量
            sections = template.paragraph_sections
            facts_count = len(sections.get('facts_options', []))
            defense_count = len(sections.get('defense_options', []))
            
            display = f"{type_mark} {template.template_name}\n"
            display += f"    案由：{template.case_cause}\n"
            display += f"    段落：{facts_count}个事实段落 + {defense_count}个抗辩段落"
            
            item.setText(display)
            item.setData(Qt.ItemDataRole.UserRole, template.id)
            
            # 自定义模板用不同颜色
            if not template.is_builtin:
                item.setForeground(QColor("#1976d2"))
            
            self.template_list.addItem(item)
    
    def _show_context_menu(self, position):
        """显示右键菜单"""
        item = self.template_list.itemAt(position)
        if not item:
            return
        
        template_id = item.data(Qt.ItemDataRole.UserRole)
        template = self.manager.get_template_by_id(template_id)
        if not template:
            return
        
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        
        # 查看
        view_action = menu.addAction("👁 查看详情")
        view_action.triggered.connect(lambda: self._view_template(template_id))
        
        menu.addSeparator()
        
        # 复制
        copy_action = menu.addAction("📋 复制模板")
        copy_action.triggered.connect(lambda: self._copy_template(template_id))
        
        # 编辑（仅自定义模板）
        if not template.is_builtin:
            edit_action = menu.addAction("✏️ 编辑模板")
            edit_action.triggered.connect(lambda: self._edit_template(template_id))
            
            menu.addSeparator()
            
            delete_action = menu.addAction("🗑 删除模板")
            delete_action.triggered.connect(lambda: self._delete_template(template_id))
        
        menu.exec(self.template_list.mapToGlobal(position))
    
    def _view_template(self, template_id: int):
        """查看模板详情"""
        template = self.manager.get_template_by_id(template_id)
        if not template:
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"模板详情 - {template.template_name}")
        dialog.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # 基本信息
        info_text = f"""
        <b>模板名称：</b>{template.template_name}<br>
        <b>适用案由：</b>{template.case_cause}<br>
        <b>模板类型：</b>{'内置模板' if template.is_builtin else '自定义模板'}<br>
        <b>创建时间：</b>{template.created_at}<br>
        <hr>
        """
        
        info_label = QLabel(info_text)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info_label)
        
        # 段落列表
        sections = template.paragraph_sections
        
        content_edit = QTextEdit()
        content_edit.setReadOnly(True)
        
        content = []
        
        if sections.get('header'):
            content.append(f"【头部】{sections['header'].get('title', '')}")
            content.append(sections['header'].get('content', '')[:200] + "...")
            content.append("")
        
        for i, fact in enumerate(sections.get('facts_options', []), 1):
            content.append(f"【事实段落{i}】{fact.get('title', '')}")
            content.append(fact.get('content', '')[:200] + "...")
            content.append("")
        
        for i, defense in enumerate(sections.get('defense_options', []), 1):
            content.append(f"【抗辩段落{i}】{defense.get('title', '')}")
            content.append(defense.get('content', '')[:200] + "...")
            content.append("")
        
        legal_options = sections.get('legal_basis', {}).get('options', [])
        if legal_options:
            content.append("【法律依据】")
            for legal in legal_options:
                content.append(f"  • {legal}")
        
        content_edit.setPlainText('\n'.join(content))
        layout.addWidget(content_edit)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def _add_template(self):
        """添加新模板"""
        dialog = TemplateEditDialog(self.manager, parent=self)
        dialog.saved.connect(self._load_templates)
        dialog.exec()
    
    def _edit_template(self, template_id: int):
        """编辑模板"""
        template = self.manager.get_template_by_id(template_id)
        if not template:
            return
        
        dialog = TemplateEditDialog(self.manager, template, parent=self)
        dialog.saved.connect(self._load_templates)
        dialog.exec()
    
    def _copy_template(self, template_id: int):
        """复制模板"""
        template = self.manager.get_template_by_id(template_id)
        if not template:
            return
        
        new_name, ok = QInputDialog.getText(
            self, "复制模板",
            "请输入新模板名称：",
            text=f"{template.template_name}（复制）"
        )
        
        if ok and new_name.strip():
            try:
                self.manager.duplicate_template(template_id, new_name.strip())
                self._load_templates()
                QMessageBox.information(self, "成功", "模板已复制")
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))
    
    def _delete_template(self, template_id: int):
        """删除模板"""
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除这个自定义模板吗？\n此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.manager.delete_template(template_id)
                self._load_templates()
            except Exception as e:
                QMessageBox.critical(self, "删除失败", str(e))
    
    def refresh(self):
        """刷新模板列表"""
        self._load_templates()
