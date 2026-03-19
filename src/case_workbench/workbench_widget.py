#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案件工作台 - 主界面组件
包含案件卡片、编辑对话框、文书生成对话框
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit,
    QDialog, QMessageBox, QGroupBox, QScrollArea, QFrame,
    QStackedWidget, QTabWidget, QCheckBox, QDateEdit,
    QDoubleSpinBox, QSplitter, QListWidget, QListWidgetItem,
    QDialogButtonBox, QInputDialog, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

from datetime import datetime, timedelta

from .models import (
    CaseWorkbenchManager, WorkbenchCase, CASE_CAUSES, CASE_STATUSES
)
from .common_info import CommonInfoManager
from .document_generator import DocumentGenerator


class CaseCard(QWidget):
    """案件卡片组件"""
    clicked = pyqtSignal(int)  # 点击信号，传递案件ID
    document_clicked = pyqtSignal(int)  # 生成文书信号
    
    def __init__(self, case: WorkbenchCase, parent=None):
        super().__init__(parent)
        self.case = case
        self.setFixedSize(320, 200)
        self._create_ui()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # 根据紧急度设置边框颜色
        if self.case.is_urgent:
            border_color = "#f44336"  # 红色 - 紧急
            bg_color = "#ffebee"
        elif self.case.status == 'closed':
            border_color = "#9e9e9e"  # 灰色 - 已结案
            bg_color = "#f5f5f5"
        else:
            border_color = "#e0e0e0"  # 默认
            bg_color = "#ffffff"
        
        self.setStyleSheet(f"""
            CaseCard {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 8px;
            }}
            CaseCard:hover {{
                border-color: #1976d2;
                background-color: #e3f2fd;
            }}
        """)
        
        # 标题行
        title_layout = QHBoxLayout()
        
        title_label = QLabel(self.case.title)
        title_font = QFont("PingFang SC", 13)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #1976d2; border: none; background: transparent;")
        title_label.setWordWrap(True)
        title_layout.addWidget(title_label, stretch=1)
        
        # 紧急标记
        if self.case.is_urgent:
            urgent_label = QLabel("🔴")
            urgent_label.setStyleSheet("border: none; background: transparent;")
            title_layout.addWidget(urgent_label)
        
        layout.addLayout(title_layout)
        
        # 当事人信息
        parties_text = f"{self.case.plaintiff} vs {self.case.defendant}"
        parties_label = QLabel(parties_text)
        parties_label.setStyleSheet("color: #424242; border: none; background: transparent; font-size: 12px;")
        parties_label.setWordWrap(True)
        layout.addWidget(parties_label)
        
        # 案由
        if self.case.case_cause:
            cause_label = QLabel(f"案由：{self.case.case_cause}")
            cause_label.setStyleSheet("color: #666666; border: none; background: transparent; font-size: 11px;")
            layout.addWidget(cause_label)
        
        # 法院
        if self.case.court:
            court_label = QLabel(f"法院：{self.case.court}")
            court_label.setStyleSheet("color: #666666; border: none; background: transparent; font-size: 11px;")
            layout.addWidget(court_label)
        
        layout.addStretch()
        
        # 底部信息
        bottom_layout = QHBoxLayout()
        
        # 开庭日期
        if self.case.hearing_date:
            hearing = datetime.strptime(self.case.hearing_date, '%Y-%m-%d')
            days_until = (hearing.date() - datetime.now().date()).days
            
            if days_until < 0:
                date_text = f"开庭：已过期"
                date_color = "#f44336"
            elif days_until == 0:
                date_text = f"开庭：今天 {self.case.hearing_time}"
                date_color = "#f44336"
            elif days_until <= 3:
                date_text = f"开庭：{days_until}天后"
                date_color = "#ff9800"
            else:
                date_text = f"开庭：{self.case.hearing_date}"
                date_color = "#4caf50"
            
            date_label = QLabel(date_text)
            date_label.setStyleSheet(f"color: {date_color}; border: none; background: transparent; font-size: 11px;")
            bottom_layout.addWidget(date_label)
        
        # 状态
        status_text = CASE_STATUSES.get(self.case.status, self.case.status)
        status_label = QLabel(f"状态：{status_text}")
        status_label.setStyleSheet("color: #757575; border: none; background: transparent; font-size: 11px;")
        bottom_layout.addWidget(status_label)
        
        bottom_layout.addStretch()
        
        # 生成文书按钮
        doc_btn = QPushButton("📄")
        doc_btn.setFixedSize(28, 28)
        doc_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        doc_btn.setToolTip("生成文书")
        doc_btn.clicked.connect(lambda: self.document_clicked.emit(self.case.id))
        bottom_layout.addWidget(doc_btn)
        
        layout.addLayout(bottom_layout)
    
    def mousePressEvent(self, event):
        """点击事件"""
        self.clicked.emit(self.case.id)
        super().mousePressEvent(event)


class CaseEditDialog(QDialog):
    """案件编辑对话框"""
    saved = pyqtSignal()  # 保存成功信号
    
    def __init__(self, manager: CaseWorkbenchManager, case: WorkbenchCase = None, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.case = case
        self.is_edit = case is not None
        
        self.setWindowTitle("编辑案件" if self.is_edit else "新建案件")
        self.setMinimumSize(800, 700)
        self._create_ui()
        
        if self.case:
            self._load_case_data()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)
        
        # ========== 基本信息 ==========
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        basic_layout.setSpacing(10)
        
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("案件标题")
        basic_layout.addRow("案件标题*：", self.title_input)
        
        self.status_combo = QComboBox()
        for key, value in CASE_STATUSES.items():
            self.status_combo.addItem(value, key)
        basic_layout.addRow("案件状态：", self.status_combo)
        
        self.case_cause_combo = QComboBox()
        self.case_cause_combo.addItem("请选择案由")
        self.case_cause_combo.addItems(CASE_CAUSES)
        self.case_cause_combo.currentTextChanged.connect(self._on_case_cause_changed)
        basic_layout.addRow("案由：", self.case_cause_combo)
        
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 999999999)
        self.amount_spin.setDecimals(2)
        self.amount_spin.setSuffix(" 元")
        basic_layout.addRow("诉讼标的：", self.amount_spin)
        
        form_layout.addWidget(basic_group)
        
        # ========== 当事主体 ==========
        parties_group = QGroupBox("当事主体")
        parties_layout = QFormLayout(parties_group)
        parties_layout.setSpacing(10)
        
        # 原告
        plaintiff_layout = QHBoxLayout()
        self.plaintiff_input = QLineEdit()
        self.plaintiff_input.setPlaceholderText("原告/申请人姓名或名称")
        plaintiff_layout.addWidget(self.plaintiff_input)
        
        self.plaintiff_type_combo = QComboBox()
        self.plaintiff_type_combo.addItems(["自然人", "法人"])
        plaintiff_layout.addWidget(self.plaintiff_type_combo)
        
        parties_layout.addRow("原告/申请人：", plaintiff_layout)
        
        # 被告
        defendant_layout = QHBoxLayout()
        self.defendant_input = QLineEdit()
        self.defendant_input.setPlaceholderText("被告/被申请人姓名或名称")
        defendant_layout.addWidget(self.defendant_input)
        
        self.defendant_type_combo = QComboBox()
        self.defendant_type_combo.addItems(["自然人", "法人"])
        defendant_layout.addWidget(self.defendant_type_combo)
        
        parties_layout.addRow("被告/被申请人：", defendant_layout)
        
        form_layout.addWidget(parties_group)
        
        # ========== 公司信息（被告为法人时填写）==========
        company_group = QGroupBox("公司信息（被告为法人时填写）")
        company_layout = QFormLayout(company_group)
        company_layout.setSpacing(10)
        
        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("公司全称")
        company_layout.addRow("公司名称：", self.company_name_input)
        
        self.company_credit_code_input = QLineEdit()
        self.company_credit_code_input.setPlaceholderText("统一社会信用代码")
        company_layout.addRow("信用代码：", self.company_credit_code_input)
        
        self.company_address_input = QLineEdit()
        self.company_address_input.setPlaceholderText("公司注册地址")
        company_layout.addRow("住所：", self.company_address_input)
        
        self.company_legal_rep_input = QLineEdit()
        self.company_legal_rep_input.setPlaceholderText("法定代表人姓名")
        company_layout.addRow("法定代表人：", self.company_legal_rep_input)
        
        form_layout.addWidget(company_group)
        
        # ========== 法院信息 ==========
        court_group = QGroupBox("法院信息")
        court_layout = QFormLayout(court_group)
        court_layout.setSpacing(10)
        
        self.court_input = QLineEdit()
        self.court_input.setPlaceholderText("如：北京市朝阳区人民法院")
        court_layout.addRow("管辖法院：", self.court_input)
        
        self.case_number_input = QLineEdit()
        self.case_number_input.setPlaceholderText("如：(2024)京0105民初1234号")
        court_layout.addRow("案号：", self.case_number_input)
        
        form_layout.addWidget(court_group)
        
        # ========== 日期信息 ==========
        dates_group = QGroupBox("日期信息")
        dates_layout = QFormLayout(dates_group)
        dates_layout.setSpacing(10)
        
        self.receive_date_edit = QDateEdit()
        self.receive_date_edit.setCalendarPopup(True)
        self.receive_date_edit.setDate(datetime.now())
        dates_layout.addRow("收到材料日期：", self.receive_date_edit)
        
        self.evidence_deadline_edit = QDateEdit()
        self.evidence_deadline_edit.setCalendarPopup(True)
        self.evidence_deadline_edit.setSpecialValueText("未设置")
        self.evidence_deadline_edit.setDate(datetime.now().date() + timedelta(days=15))
        dates_layout.addRow("举证期限：", self.evidence_deadline_edit)
        
        self.hearing_date_edit = QDateEdit()
        self.hearing_date_edit.setCalendarPopup(True)
        self.hearing_date_edit.setSpecialValueText("未设置")
        self.hearing_date_edit.setDate(datetime.now().date() + timedelta(days=30))
        dates_layout.addRow("开庭日期：", self.hearing_date_edit)
        
        self.hearing_time_input = QLineEdit("09:00")
        dates_layout.addRow("开庭时间：", self.hearing_time_input)
        
        form_layout.addWidget(dates_group)
        
        # ========== 代理信息 ==========
        lawyer_group = QGroupBox("代理信息")
        lawyer_layout = QFormLayout(lawyer_group)
        lawyer_layout.setSpacing(10)
        
        self.lawyer_name_input = QLineEdit()
        self.lawyer_name_input.setPlaceholderText("代理律师姓名")
        lawyer_layout.addRow("代理律师：", self.lawyer_name_input)
        
        self.lawyer_gender_combo = QComboBox()
        self.lawyer_gender_combo.addItems(["", "男", "女"])
        lawyer_layout.addRow("律师性别：", self.lawyer_gender_combo)
        
        self.lawyer_license_input = QLineEdit()
        self.lawyer_license_input.setPlaceholderText("如：11101202410XXXXXX")
        lawyer_layout.addRow("执业证号：", self.lawyer_license_input)
        
        self.law_firm_input = QLineEdit()
        self.law_firm_input.setPlaceholderText("律师事务所名称")
        lawyer_layout.addRow("律师事务所：", self.law_firm_input)
        
        self.lawyer_id_card_input = QLineEdit()
        self.lawyer_id_card_input.setPlaceholderText("律师身份证号码")
        lawyer_layout.addRow("身份证号：", self.lawyer_id_card_input)
        
        self.lawyer_phone_input = QLineEdit()
        self.lawyer_phone_input.setPlaceholderText("联系电话")
        lawyer_layout.addRow("电话：", self.lawyer_phone_input)
        
        form_layout.addWidget(lawyer_group)
        
        # ========== 案情简介 ==========
        facts_group = QGroupBox("案情简介")
        facts_layout = QVBoxLayout(facts_group)
        
        self.facts_edit = QTextEdit()
        self.facts_edit.setPlaceholderText("简要记录案情要点...")
        self.facts_edit.setMaximumHeight(120)
        facts_layout.addWidget(self.facts_edit)
        
        form_layout.addWidget(facts_group)
        
        # ========== 专题标签 ==========
        topics_group = QGroupBox("关联专题（自动匹配）")
        topics_layout = QVBoxLayout(topics_group)
        
        self.topics_label = QLabel("请选择案由以自动匹配相关专题")
        self.topics_label.setStyleSheet("color: #666666; font-size: 12px;")
        self.topics_label.setWordWrap(True)
        topics_layout.addWidget(self.topics_label)
        
        form_layout.addWidget(topics_group)
        
        form_layout.addStretch()
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # ========== 按钮 ==========
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 30px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _on_case_cause_changed(self, case_cause: str):
        """案由改变时更新专题标签"""
        if case_cause and case_cause != "请选择案由":
            topics = self.manager.auto_match_topics(case_cause)
            if topics:
                topic_names = []
                for topic_key in topics:
                    topic = self.manager.get_topic_by_key(topic_key)
                    if topic:
                        topic_names.append(topic.topic_name)
                self.topics_label.setText("已匹配专题：" + "、".join(topic_names))
                self.topics_label.setStyleSheet("color: #4caf50; font-size: 12px;")
            else:
                self.topics_label.setText("该案由暂无自动匹配专题")
                self.topics_label.setStyleSheet("color: #9e9e9e; font-size: 12px;")
        else:
            self.topics_label.setText("请选择案由以自动匹配相关专题")
            self.topics_label.setStyleSheet("color: #666666; font-size: 12px;")
    
    def _load_case_data(self):
        """加载案件数据到表单"""
        self.title_input.setText(self.case.title)
        
        index = self.status_combo.findData(self.case.status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        
        if self.case.case_cause:
            index = self.case_cause_combo.findText(self.case.case_cause)
            if index >= 0:
                self.case_cause_combo.setCurrentIndex(index)
        
        self.amount_spin.setValue(self.case.case_amount)
        self.plaintiff_input.setText(self.case.plaintiff)
        self.plaintiff_type_combo.setCurrentText(self.case.plaintiff_type)
        self.defendant_input.setText(self.case.defendant)
        self.defendant_type_combo.setCurrentText(self.case.defendant_type)
        self.court_input.setText(self.case.court)
        self.case_number_input.setText(self.case.case_number)
        
        if self.case.receive_date:
            self.receive_date_edit.setDate(
                datetime.strptime(self.case.receive_date, '%Y-%m-%d')
            )
        
        if self.case.evidence_deadline:
            self.evidence_deadline_edit.setDate(
                datetime.strptime(self.case.evidence_deadline, '%Y-%m-%d')
            )
        
        if self.case.hearing_date:
            self.hearing_date_edit.setDate(
                datetime.strptime(self.case.hearing_date, '%Y-%m-%d')
            )
        
        self.hearing_time_input.setText(self.case.hearing_time)
        
        # 公司信息
        self.company_name_input.setText(self.case.company_name)
        self.company_credit_code_input.setText(self.case.company_credit_code)
        self.company_address_input.setText(self.case.company_address)
        self.company_legal_rep_input.setText(self.case.company_legal_rep)
        
        # 代理信息
        self.lawyer_name_input.setText(self.case.lawyer_name)
        self.lawyer_gender_combo.setCurrentText(self.case.lawyer_gender)
        self.lawyer_id_card_input.setText(self.case.lawyer_id_card)
        self.lawyer_phone_input.setText(self.case.lawyer_phone)
        self.lawyer_license_input.setText(self.case.lawyer_license)
        self.law_firm_input.setText(self.case.law_firm)
        self.facts_edit.setPlainText(self.case.case_facts)
    
    def _save(self):
        """保存案件"""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "提示", "请输入案件标题")
            return
        
        case_data = {
            'title': title,
            'status': self.status_combo.currentData(),
            'case_cause': self.case_cause_combo.currentText() if self.case_cause_combo.currentIndex() > 0 else "",
            'case_amount': self.amount_spin.value(),
            'plaintiff': self.plaintiff_input.text(),
            'plaintiff_type': self.plaintiff_type_combo.currentText(),
            'defendant': self.defendant_input.text(),
            'defendant_type': self.defendant_type_combo.currentText(),
            'company_name': self.company_name_input.text(),
            'company_credit_code': self.company_credit_code_input.text(),
            'company_address': self.company_address_input.text(),
            'company_legal_rep': self.company_legal_rep_input.text(),
            'court': self.court_input.text(),
            'case_number': self.case_number_input.text(),
            'receive_date': self.receive_date_edit.date().toString("yyyy-MM-dd"),
            'evidence_deadline': self.evidence_deadline_edit.date().toString("yyyy-MM-dd") if self.evidence_deadline_edit.date() else None,
            'hearing_date': self.hearing_date_edit.date().toString("yyyy-MM-dd") if self.hearing_date_edit.date() else None,
            'hearing_time': self.hearing_time_input.text(),
            'lawyer_name': self.lawyer_name_input.text(),
            'lawyer_gender': self.lawyer_gender_combo.currentText(),
            'lawyer_id_card': self.lawyer_id_card_input.text(),
            'lawyer_phone': self.lawyer_phone_input.text(),
            'lawyer_license': self.lawyer_license_input.text(),
            'law_firm': self.law_firm_input.text(),
            'case_facts': self.facts_edit.toPlainText()
        }
        
        try:
            if self.is_edit:
                self.manager.update_case(self.case.id, **case_data)
            else:
                self.manager.add_case(**case_data)
            
            self.saved.emit()
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))


class DocumentGenerateDialog(QDialog):
    """文书生成对话框"""
    def __init__(self, manager: CaseWorkbenchManager, case: WorkbenchCase, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.case = case
        self.generator = DocumentGenerator()
        self.setWindowTitle(f"生成文书 - {case.title}")
        self.setMinimumSize(900, 700)
        self._create_ui()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        
        # 文书类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("选择文书类型："))
        
        self.doc_type_combo = QComboBox()
        self.doc_type_combo.addItems([
            "授权委托书",
            "法定代表人身份证明书",
            "答辩状"
        ])
        self.doc_type_combo.currentIndexChanged.connect(self._on_doc_type_changed)
        type_layout.addWidget(self.doc_type_combo)
        type_layout.addStretch()
        
        layout.addLayout(type_layout)
        
        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #e0e0e0;")
        layout.addWidget(line)
        
        # 内容区域
        self.content_stack = QStackedWidget()
        
        # 1. 授权委托书配置
        self.power_attorney_widget = self._create_power_attorney_widget()
        self.content_stack.addWidget(self.power_attorney_widget)
        
        # 2. 法定代表人证明配置
        self.legal_rep_widget = self._create_legal_rep_widget()
        self.content_stack.addWidget(self.legal_rep_widget)
        
        # 3. 答辩状配置
        self.defense_widget = self._create_defense_widget()
        self.content_stack.addWidget(self.defense_widget)
        
        layout.addWidget(self.content_stack)
        
        # 预览区域
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        self.preview_edit.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                font-family: "SimSun", "宋体", serif;
                font-size: 12pt;
                line-height: 1.6;
            }
        """)
        preview_layout.addWidget(self.preview_edit)
        
        layout.addWidget(preview_group)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        preview_btn = QPushButton("👁 预览")
        preview_btn.clicked.connect(self._preview)
        btn_layout.addWidget(preview_btn)
        
        export_btn = QPushButton("📄 导出Word")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        export_btn.clicked.connect(self._export)
        btn_layout.addWidget(export_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_power_attorney_widget(self) -> QWidget:
        """创建授权委托书配置面板"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        
        # 委托人类型
        self.plaintiff_type_group = QComboBox()
        self.plaintiff_type_group.addItems(["自然人", "法人"])
        if self.case.plaintiff_type:
            self.plaintiff_type_group.setCurrentText(self.case.plaintiff_type)
        layout.addRow("委托人类型：", self.plaintiff_type_group)
        
        # 委托人
        self.pa_plaintiff_input = QLineEdit(self.case.plaintiff)
        layout.addRow("委托人：", self.pa_plaintiff_input)
        
        # 对方当事人
        self.pa_defendant_input = QLineEdit(self.case.defendant)
        layout.addRow("对方当事人：", self.pa_defendant_input)
        
        # === 律师信息（从案件数据读取）===
        lawyer_info = QGroupBox("代理律师信息")
        lawyer_layout = QFormLayout(lawyer_info)
        
        self.pa_lawyer_input = QLineEdit(self.case.lawyer_name)
        lawyer_layout.addRow("律师姓名：", self.pa_lawyer_input)
        
        self.pa_lawyer_gender = QComboBox()
        self.pa_lawyer_gender.addItems(["", "男", "女"])
        self.pa_lawyer_gender.setCurrentText(self.case.lawyer_gender)
        lawyer_layout.addRow("性别：", self.pa_lawyer_gender)
        
        self.pa_lawyer_id_card = QLineEdit(self.case.lawyer_id_card)
        self.pa_lawyer_id_card.setPlaceholderText("身份证号码")
        lawyer_layout.addRow("身份证号：", self.pa_lawyer_id_card)
        
        self.pa_lawyer_phone = QLineEdit(self.case.lawyer_phone)
        self.pa_lawyer_phone.setPlaceholderText("联系电话")
        lawyer_layout.addRow("电话：", self.pa_lawyer_phone)
        
        self.pa_firm_input = QLineEdit(self.case.law_firm)
        lawyer_layout.addRow("律师事务所：", self.pa_firm_input)
        
        self.pa_license_input = QLineEdit(self.case.lawyer_license)
        lawyer_layout.addRow("执业证号：", self.pa_license_input)
        
        layout.addRow(lawyer_info)
        
        return widget
    
    def _create_legal_rep_widget(self) -> QWidget:
        """创建法定代表人证明配置面板"""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(10)
        
        # === 公司信息（从案件数据读取）===
        company_info = QGroupBox("公司信息")
        company_layout = QFormLayout(company_info)
        
        # 公司名称
        self.lr_company_name_input = QLineEdit(self.case.company_name or self.case.defendant)
        company_layout.addRow("公司名称：", self.lr_company_name_input)
        
        # 统一社会信用代码
        self.lr_credit_code_input = QLineEdit(self.case.company_credit_code)
        self.lr_credit_code_input.setPlaceholderText("统一社会信用代码")
        company_layout.addRow("信用代码：", self.lr_credit_code_input)
        
        # 住所
        self.lr_address_input = QLineEdit(self.case.company_address)
        self.lr_address_input.setPlaceholderText("公司注册地址")
        company_layout.addRow("住所：", self.lr_address_input)
        
        # 法定代表人
        self.lr_legal_rep_input = QLineEdit(self.case.company_legal_rep)
        self.lr_legal_rep_input.setPlaceholderText("法定代表人姓名")
        company_layout.addRow("法定代表人：", self.lr_legal_rep_input)
        
        layout.addRow(company_info)
        
        return widget
    
    def _create_defense_widget(self) -> QWidget:
        """创建答辩状配置面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        if not self.case.case_cause:
            layout.addWidget(QLabel("⚠️ 案件未设置案由，无法生成答辩状"))
            return widget
        
        # 获取模板
        templates = self.manager.get_templates_by_case_cause(self.case.case_cause)
        if not templates:
            layout.addWidget(QLabel(f"⚠️ 暂无{self.case.case_cause}的答辩状模板"))
            return widget
        
        # 模板选择
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("选择模板："))
        
        self.template_combo = QComboBox()
        for t in templates:
            label = f"{'[内置] ' if t.is_builtin else '[自定义] '}{t.template_name}"
            self.template_combo.addItem(label, t.id)
        template_layout.addWidget(self.template_combo)
        template_layout.addStretch()
        
        layout.addLayout(template_layout)
        
        # 自定义内容
        custom_group = QGroupBox("自定义内容（替换占位符）")
        custom_layout = QFormLayout(custom_group)
        
        self.defendant_address_input = QLineEdit()
        self.defendant_address_input.setPlaceholderText("被告住所地")
        custom_layout.addRow("被告住所地：", self.defendant_address_input)
        
        self.legal_rep_input = QLineEdit()
        self.legal_rep_input.setPlaceholderText("法定代表人姓名")
        custom_layout.addRow("法定代表人：", self.legal_rep_input)
        
        self.third_party_input = QLineEdit()
        self.third_party_input.setPlaceholderText("如：外包公司/派遣公司名称")
        custom_layout.addRow("第三方公司：", self.third_party_input)
        
        layout.addWidget(custom_group)
        
        # 段落选择
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        select_widget = QWidget()
        select_layout = QVBoxLayout(select_widget)
        
        # 获取当前模板的段落
        self.template = templates[0] if templates else None
        if self.template:
            sections = self.template.paragraph_sections
            
            # 事实段落选择
            facts_group = QGroupBox("事实部分（选择段落）")
            facts_layout = QVBoxLayout(facts_group)
            
            self.facts_checkboxes = []
            facts_options = sections.get('facts_options', [])
            for i, fact in enumerate(facts_options):
                checkbox = QCheckBox(f"{i+1}. {fact.get('title', f'段落{i+1}')}")
                checkbox.setChecked(i == 0)  # 默认选中第一个
                checkbox.setProperty('content', fact.get('content', ''))
                self.facts_checkboxes.append(checkbox)
                facts_layout.addWidget(checkbox)
            
            select_layout.addWidget(facts_group)
            
            # 抗辩要点选择
            defense_group = QGroupBox("抗辩要点（选择适用要点）")
            defense_layout = QVBoxLayout(defense_group)
            
            self.defense_checkboxes = []
            defense_options = sections.get('defense_options', [])
            for i, defense in enumerate(defense_options):
                checkbox = QCheckBox(f"{i+1}. {defense.get('title', f'要点{i+1}')}")
                checkbox.setProperty('content', defense.get('content', ''))
                self.defense_checkboxes.append(checkbox)
                defense_layout.addWidget(checkbox)
            
            select_layout.addWidget(defense_group)
            
            # 法律依据
            legal_group = QGroupBox("法律依据")
            legal_layout = QVBoxLayout(legal_group)
            
            self.legal_checkboxes = []
            legal_basis = sections.get('legal_basis', {}).get('options', self.template.legal_basis)
            for legal in legal_basis:
                checkbox = QCheckBox(legal)
                checkbox.setChecked(True)
                self.legal_checkboxes.append(checkbox)
                legal_layout.addWidget(checkbox)
            
            select_layout.addWidget(legal_group)
        
        select_layout.addStretch()
        scroll.setWidget(select_widget)
        layout.addWidget(scroll)
        
        return widget
    
    def _on_doc_type_changed(self, index: int):
        """文书类型改变"""
        self.content_stack.setCurrentIndex(index)
    
    def _preview(self):
        """预览文书"""
        doc_type = self.doc_type_combo.currentIndex()
        
        try:
            if doc_type == 0:  # 授权委托书
                case_data = {
                    'plaintiff': self.pa_plaintiff_input.text(),
                    'plaintiff_type': self.plaintiff_type_group.currentText(),
                    'defendant': self.pa_defendant_input.text(),
                    'case_cause': self.case.case_cause,
                    'company_name': self.case.company_name,
                    'company_address': self.case.company_address,
                    'company_legal_rep': self.case.company_legal_rep,
                    'lawyer_name': self.pa_lawyer_input.text(),
                    'lawyer_gender': self.pa_lawyer_gender.currentText(),
                    'lawyer_id_card': self.pa_lawyer_id_card.text(),
                    'lawyer_phone': self.pa_lawyer_phone.text(),
                    'law_firm': self.pa_firm_input.text(),
                    'lawyer_license': self.pa_license_input.text(),
                    'court': self.case.court
                }
                preview_text = self._preview_power_of_attorney(case_data)
                
            elif doc_type == 1:  # 法定代表人证明
                case_data = {
                    'company_name': self.lr_company_name_input.text(),
                    'company_credit_code': self.lr_credit_code_input.text(),
                    'company_address': self.lr_address_input.text(),
                    'company_legal_rep': self.lr_legal_rep_input.text()
                }
                preview_text = self._preview_legal_rep_cert(case_data)
                
            else:  # 答辩状
                case_data = {
                    'plaintiff': self.case.plaintiff,
                    'defendant': self.case.defendant,
                    'court': self.case.court,
                    'case_cause': self.case.case_cause
                }
                
                custom_content = {
                    'defendant_address': self.defendant_address_input.text(),
                    'legal_rep': self.legal_rep_input.text(),
                    'third_party': self.third_party_input.text()
                }
                
                selected_facts = [cb.property('content') for cb in self.facts_checkboxes if cb.isChecked()]
                selected_defenses = [cb.property('content') for cb in self.defense_checkboxes if cb.isChecked()]
                selected_legal = [cb.text() for cb in self.legal_checkboxes if cb.isChecked()]
                
                preview_text = self.generator.preview_defense_statement(
                    case_data, selected_facts, selected_defenses, selected_legal, custom_content
                )
            
            self.preview_edit.setPlainText(preview_text)
            
        except Exception as e:
            QMessageBox.warning(self, "预览失败", str(e))
    
    def _preview_power_of_attorney(self, case_data: dict) -> str:
        """预览授权委托书"""
        lines = []
        lines.append("授 权 委 托 书")
        lines.append("")
        lines.append(f"委托人：{case_data['plaintiff']}")
        
        if case_data['plaintiff_type'] == '自然人':
            lines.append("性别：______  身份证号：____________________")
            lines.append("住址：________________________________")
        else:
            lines.append(f"公司名称：{case_data.get('company_name', '')}")
            lines.append(f"住所地：{case_data.get('company_address', '')}")
            lines.append(f"法定代表人：{case_data.get('company_legal_rep', '')}")
        
        lines.append("")
        lines.append(f"受委托人：{case_data['lawyer_name']}")
        if case_data.get('lawyer_gender'):
            lines.append(f"性别：{case_data['lawyer_gender']}")
        if case_data.get('lawyer_id_card'):
            lines.append(f"身份证号：{case_data['lawyer_id_card']}")
        if case_data.get('lawyer_phone'):
            lines.append(f"联系电话：{case_data['lawyer_phone']}")
        lines.append(f"工作单位：{case_data['law_firm']}")
        lines.append(f"执业证号：{case_data['lawyer_license']}")
        lines.append("")
        lines.append(f"现委托上列受委托人在我与{case_data['defendant']}{case_data['case_cause']}一案中，作为我的诉讼代理人。")
        lines.append("")
        lines.append("代理权限如下：")
        lines.append("☑ 一般代理：代为起诉、应诉、代为陈述事实、参加辩论、代为调取证据、代为调解、代为签收法律文书等。")
        lines.append("☐ 特别授权：代为承认、放弃、变更诉讼请求，进行和解，提起反诉或上诉。")
        lines.append("")
        lines.append("委托人（签名/盖章）：______________")
        lines.append(f"日期：{datetime.now().strftime('%Y年%m月%d日')}")
        
        return '\n'.join(lines)
    
    def _preview_legal_rep_cert(self, case_data: dict) -> str:
        """预览法定代表人证明"""
        lines = []
        lines.append("法定代表人身份证明书")
        lines.append("")
        lines.append(f"{case_data['defendant']}（单位名称）的法定代表人（或主要负责人）为{case_data['legal_rep_name']}，职务：{case_data['legal_rep_position']}。")
        lines.append("")
        lines.append("特此证明。")
        lines.append("")
        lines.append("附：法定代表人/负责人身份证复印件")
        lines.append("")
        lines.append("单位（盖章）：______________")
        lines.append(f"日期：{datetime.now().strftime('%Y年%m月%d日')}")
        
        return '\n'.join(lines)
    
    def _export(self):
        """导出Word"""
        doc_type = self.doc_type_combo.currentIndex()
        
        try:
            if doc_type == 0:  # 授权委托书
                case_data = {
                    'plaintiff': self.pa_plaintiff_input.text(),
                    'plaintiff_type': self.plaintiff_type_group.currentText(),
                    'defendant': self.pa_defendant_input.text(),
                    'case_cause': self.case.case_cause,
                    'company_name': self.case.company_name,
                    'company_address': self.case.company_address,
                    'company_legal_rep': self.case.company_legal_rep,
                    'lawyer_name': self.pa_lawyer_input.text(),
                    'lawyer_gender': self.case.lawyer_gender,
                    'lawyer_id_card': self.case.lawyer_id_card,
                    'lawyer_phone': self.case.lawyer_phone,
                    'law_firm': self.pa_firm_input.text(),
                    'lawyer_license': self.pa_license_input.text(),
                    'court': self.case.court
                }
                file_path = self.generator.generate_power_of_attorney(case_data)
                
            elif doc_type == 1:  # 法定代表人证明
                case_data = {
                    'defendant': self.lr_defendant_input.text(),
                    'legal_rep_name': self.lr_rep_name_input.text(),
                    'legal_rep_position': self.lr_position_input.text()
                }
                file_path = self.generator.generate_legal_rep_cert(case_data)
                
            else:  # 答辩状
                case_data = {
                    'plaintiff': self.case.plaintiff,
                    'defendant': self.case.defendant,
                    'court': self.case.court,
                    'case_cause': self.case.case_cause
                }
                
                custom_content = {
                    'defendant_address': self.defendant_address_input.text(),
                    'legal_rep': self.legal_rep_input.text(),
                    'third_party': self.third_party_input.text()
                }
                
                selected_facts = [cb.property('content') for cb in self.facts_checkboxes if cb.isChecked()]
                selected_defenses = [cb.property('content') for cb in self.defense_checkboxes if cb.isChecked()]
                selected_legal = [cb.text() for cb in self.legal_checkboxes if cb.isChecked()]
                
                file_path = self.generator.generate_defense_statement(
                    case_data, selected_facts, selected_defenses, selected_legal, custom_content
                )
            
            # 保存文书记录
            doc_type_str = ['power_of_attorney', 'legal_rep_cert', 'defense_statement'][doc_type]
            doc_name = ['授权委托书', '法定代表人身份证明书', '答辩状'][doc_type]
            self.manager.add_document(self.case.id, doc_type_str, doc_name, 
                                     self.preview_edit.toPlainText(), file_path)
            
            QMessageBox.information(self, "导出成功", f"文书已保存至：\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", str(e))


class CaseWorkbenchWidget(QWidget):
    """案件工作台主界面 - 参考案例面板卡片样式"""
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.manager = CaseWorkbenchManager(db.conn)
        self.common_info_mgr = CommonInfoManager(db.conn)  # 常用信息管理器
        self._create_ui()
        self._load_cases()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # 标题栏
        header_layout = QHBoxLayout()
        
        title = QLabel("📋 我的案件工作台")
        title_font = QFont("PingFang SC", 13)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #1976d2;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # 新建案件按钮
        add_btn = QPushButton("➕ 新建案件")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
        """)
        add_btn.clicked.connect(self._add_case)
        header_layout.addWidget(add_btn)
        
        # 常用信息管理按钮
        common_info_btn = QPushButton("📋 常用信息")
        common_info_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        common_info_btn.clicked.connect(self._show_common_info_menu)
        header_layout.addWidget(common_info_btn)
        
        layout.addLayout(header_layout)
        
        # 筛选栏
        filter_layout = QHBoxLayout()
        
        # 状态筛选
        self.type_filter = QComboBox()
        self.type_filter.addItems(["全部案件", "待处理", "准备中", "🔴 紧急", "近期开庭"])
        self.type_filter.currentIndexChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(QLabel("筛选:"))
        filter_layout.addWidget(self.type_filter)
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索案件标题、当事人、法院...")
        self.search_input.setFixedWidth(280)
        self.search_input.returnPressed.connect(self._load_cases)
        filter_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("搜索")
        search_btn.clicked.connect(self._load_cases)
        filter_layout.addWidget(search_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # 案件列表 - 参考案例面板样式（白底卡片）
        self.case_list = QListWidget()
        self.case_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QListWidget::item {
                background-color: #fafafa;
                padding: 12px;
                margin: 4px 8px;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
                color: #212121;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-color: #1976d2;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
            }
        """)
        self.case_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.case_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.case_list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.case_list)
        
        # 统计信息
        self.stats_label = QLabel("暂无案件")
        self.stats_label.setStyleSheet("color: #757575; font-size: 11px;")
        layout.addWidget(self.stats_label)
    
    def _on_filter_changed(self, index: int):
        """筛选改变"""
        self._load_cases()
    
    def _load_cases(self):
        """加载案件列表 - 参考案例面板样式"""
        self.case_list.clear()
        
        # 获取筛选条件
        filter_index = self.type_filter.currentIndex()
        keyword = self.search_input.text().strip()
        
        if filter_index == 0:  # 全部
            cases = self.manager.get_cases(keyword=keyword if keyword else None)
        elif filter_index == 1:  # 待处理
            cases = self.manager.get_cases(status='pending', keyword=keyword if keyword else None)
        elif filter_index == 2:  # 准备中
            cases = self.manager.get_cases(status='preparing', keyword=keyword if keyword else None)
        elif filter_index == 3:  # 紧急
            cases = self.manager.get_urgent_cases()
            if keyword:
                cases = [c for c in cases if keyword in c.title or keyword in c.plaintiff 
                        or keyword in c.defendant or keyword in c.court]
        else:  # 近期开庭
            future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            cases = self.manager.get_cases(keyword=keyword if keyword else None)
            cases = [c for c in cases if c.hearing_date and c.hearing_date <= future_date and c.status not in ['closed', 'judged']]
        
        # 创建列表项
        for case in cases:
            item = QListWidgetItem()
            
            # 紧急度标记
            urgency_mark = "🔴 " if case.is_urgent else ""
            
            # 状态标记
            status_map = {
                'pending': '【待处理】',
                'preparing': '【准备中】',
                'submitted': '【已立案】',
                'hearing': '【已开庭】',
                'judged': '【已判决】',
                'closed': '【已结案】'
            }
            status_mark = status_map.get(case.status, '【待处理】')
            
            # 开庭/举证日期提醒
            date_info = ""
            if case.hearing_date:
                date_info += f" | 开庭: {case.hearing_date}"
            if case.evidence_deadline:
                date_info += f" | 举证: {case.evidence_deadline}"
            
            # 办案律师
            lawyer_info = f" | 律师: {case.lawyer_name}" if case.lawyer_name else ""
            
            # 构建显示文本
            display = f"{urgency_mark}{status_mark} {case.title}\n"
            display += f"    {case.plaintiff} vs {case.defendant}"
            if case.case_cause:
                display += f" | {case.case_cause}"
            if lawyer_info:
                display += lawyer_info
            if date_info:
                display += f"\n    {date_info}"
            
            item.setText(display)
            item.setData(Qt.ItemDataRole.UserRole, case.id)
            
            # 紧急案件高亮
            if case.is_urgent:
                item.setBackground(QColor("#ffebee"))
            
            # 提示信息
            tooltip = f"案号: {case.case_number or '未填写'}\n"
            tooltip += f"法院: {case.court or '未填写'}\n"
            tooltip += f"代理律师: {case.lawyer_name or '未填写'}"
            item.setToolTip(tooltip)
            
            self.case_list.addItem(item)
        
        # 更新统计
        total = len(cases)
        urgent_count = len([c for c in cases if c.is_urgent])
        status_text = f"共 {total} 个案件"
        if urgent_count > 0:
            status_text += f"，其中 🔴 {urgent_count} 个紧急"
        self.stats_label.setText(status_text)
    
    def _on_item_double_clicked(self, item):
        """双击编辑案件"""
        case_id = item.data(Qt.ItemDataRole.UserRole)
        self._edit_case(case_id)
    
    def _show_context_menu(self, position):
        """显示右键菜单"""
        item = self.case_list.itemAt(position)
        if not item:
            return
        
        case_id = item.data(Qt.ItemDataRole.UserRole)
        
        menu = QMenu(self)
        
        view_action = menu.addAction("查看详情")
        view_action.triggered.connect(lambda: self._edit_case(case_id))
        
        edit_action = menu.addAction("编辑案件")
        edit_action.triggered.connect(lambda: self._edit_case(case_id))
        
        menu.addSeparator()
        
        doc_action = menu.addAction("生成文书")
        doc_action.triggered.connect(lambda: self._generate_document(case_id))
        
        menu.addSeparator()
        
        delete_action = menu.addAction("删除案件")
        delete_action.triggered.connect(lambda: self._delete_case(case_id))
        
        menu.exec(self.case_list.mapToGlobal(position))
    
    def _delete_case(self, case_id: int):
        """删除案件"""
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除这个案件吗？\n此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.manager.delete_case(case_id)
            self._load_cases()
    
    def _add_case(self):
        """添加案件"""
        dialog = CaseEditDialog(self.manager, parent=self)
        dialog.saved.connect(self._load_cases)
        dialog.exec()
    
    def _edit_case(self, case_id: int):
        """编辑案件"""
        case = self.manager.get_case_by_id(case_id)
        if case:
            dialog = CaseEditDialog(self.manager, case, parent=self)
            dialog.saved.connect(self._load_cases)
            dialog.exec()
    
    def _generate_document(self, case_id: int):
        """生成文书"""
        case = self.manager.get_case_by_id(case_id)
        if case:
            dialog = DocumentGenerateDialog(self.manager, case, parent=self)
            dialog.exec()
    
    def refresh(self):
        """刷新案件列表"""
        self._load_cases()

    def _show_common_info_menu(self):
        """显示常用信息管理菜单"""
        menu = QMenu(self)
        
        company_action = menu.addAction("🏢 录入常用公司信息")
        company_action.triggered.connect(self._manage_companies)
        
        agent_action = menu.addAction("👤 录入代理人信息")
        agent_action.triggered.connect(self._manage_agents)
        
        menu.addSeparator()
        
        # 显示当前默认信息
        default_company = self.common_info_mgr.get_default_company()
        default_agent = self.common_info_mgr.get_default_agent()
        
        if default_company:
            info_action = menu.addAction(f"默认公司: {default_company.name}")
            info_action.setEnabled(False)
        
        if default_agent:
            info_action = menu.addAction(f"默认代理人: {default_agent.name}")
            info_action.setEnabled(False)
        
        # 在按钮下方显示菜单
        sender = self.sender()
        menu.exec(sender.mapToGlobal(sender.rect().bottomLeft()))
    
    def _manage_companies(self):
        """管理常用公司信息"""
        dialog = CompanyManageDialog(self.common_info_mgr, self)
        dialog.exec()
    
    def _manage_agents(self):
        """管理代理人信息"""
        dialog = AgentManageDialog(self.common_info_mgr, self)
        dialog.exec()



# ==================== 常用信息管理对话框 ====================

class CompanyManageDialog(QDialog):
    """常用公司信息管理对话框"""
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("常用公司信息管理")
        self.setMinimumSize(600, 500)
        self._create_ui()
        self._load_companies()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("🏢 常用公司信息")
        title_font = QFont("PingFang SC", 14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #1976d2;")
        layout.addWidget(title)
        
        # 说明
        desc = QLabel("录入常用的公司信息，生成文书时可直接调用")
        desc.setStyleSheet("color: #666666; font-size: 12px;")
        layout.addWidget(desc)
        
        # 公司列表
        self.company_list = QListWidget()
        self.company_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 10px;
                margin: 4px 8px;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-color: #1976d2;
            }
        """)
        self.company_list.itemDoubleClicked.connect(self._edit_company)
        layout.addWidget(self.company_list)
        
        # 按钮栏
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ 添加公司")
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
        add_btn.clicked.connect(self._add_company)
        btn_layout.addWidget(add_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_companies(self):
        """加载公司列表"""
        self.company_list.clear()
        companies = self.manager.get_all_companies()
        
        for company in companies:
            item = QListWidgetItem()
            default_mark = "【默认】" if company.is_default else ""
            display = f"{default_mark} {company.name}\n"
            display += f"    信用代码: {company.credit_code or '未填写'} | 法定代表人: {company.legal_rep or '未填写'}"
            
            item.setText(display)
            item.setData(Qt.ItemDataRole.UserRole, company.id)
            
            if company.is_default:
                item.setBackground(QColor("#fff3e0"))
            
            self.company_list.addItem(item)
    
    def _add_company(self):
        """添加公司"""
        dialog = CompanyEditDialog(self.manager, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_companies()
    
    def _edit_company(self, item):
        """编辑公司"""
        company_id = item.data(Qt.ItemDataRole.UserRole)
        dialog = CompanyEditDialog(self.manager, company_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_companies()


class CompanyEditDialog(QDialog):
    """公司信息编辑对话框"""
    def __init__(self, manager, company_id=None, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.company_id = company_id
        self.is_edit = company_id is not None
        
        self.setWindowTitle("编辑公司信息" if self.is_edit else "添加公司信息")
        self.setMinimumSize(500, 400)
        self._create_ui()
        
        if self.is_edit:
            self._load_data()
    
    def _create_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        # 公司名称
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("公司全称")
        layout.addRow("公司名称*：", self.name_input)
        
        # 信用代码
        self.credit_code_input = QLineEdit()
        self.credit_code_input.setPlaceholderText("统一社会信用代码")
        layout.addRow("信用代码：", self.credit_code_input)
        
        # 住所
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("公司注册地址")
        layout.addRow("住所：", self.address_input)
        
        # 法定代表人
        self.legal_rep_input = QLineEdit()
        self.legal_rep_input.setPlaceholderText("法定代表人姓名")
        layout.addRow("法定代表人：", self.legal_rep_input)
        
        # 联系电话
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("公司联系电话")
        layout.addRow("联系电话：", self.phone_input)
        
        # 设为默认
        self.default_check = QCheckBox("设为默认公司")
        layout.addRow("", self.default_check)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        
        layout.addRow(btn_layout)
    
    def _load_data(self):
        """加载公司数据"""
        company = self.manager.get_company_by_id(self.company_id)
        if company:
            self.name_input.setText(company.name)
            self.credit_code_input.setText(company.credit_code)
            self.address_input.setText(company.address)
            self.legal_rep_input.setText(company.legal_rep)
            self.phone_input.setText(company.phone)
            self.default_check.setChecked(company.is_default)
    
    def _save(self):
        """保存"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入公司名称")
            return
        
        data = {
            'name': name,
            'credit_code': self.credit_code_input.text(),
            'address': self.address_input.text(),
            'legal_rep': self.legal_rep_input.text(),
            'phone': self.phone_input.text(),
            'is_default': self.default_check.isChecked()
        }
        
        try:
            if self.is_edit:
                self.manager.update_company(self.company_id, **data)
            else:
                self.manager.add_company(**data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))


class AgentManageDialog(QDialog):
    """代理人信息管理对话框"""
    def __init__(self, manager, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.setWindowTitle("代理人信息管理")
        self.setMinimumSize(600, 500)
        self._create_ui()
        self._load_agents()
    
    def _create_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("👤 代理人信息")
        title_font = QFont("PingFang SC", 14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #1976d2;")
        layout.addWidget(title)
        
        # 说明
        desc = QLabel("录入常用的代理人（律师）信息，生成文书时可直接调用")
        desc.setStyleSheet("color: #666666; font-size: 12px;")
        layout.addWidget(desc)
        
        # 代理人列表
        self.agent_list = QListWidget()
        self.agent_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 10px;
                margin: 4px 8px;
                border-radius: 6px;
                border: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-color: #1976d2;
            }
        """)
        self.agent_list.itemDoubleClicked.connect(self._edit_agent)
        layout.addWidget(self.agent_list)
        
        # 按钮栏
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ 添加代理人")
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
        add_btn.clicked.connect(self._add_agent)
        btn_layout.addWidget(add_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _load_agents(self):
        """加载代理人列表"""
        self.agent_list.clear()
        agents = self.manager.get_all_agents()
        
        for agent in agents:
            item = QListWidgetItem()
            default_mark = "【默认】" if agent.is_default else ""
            gender = f"({agent.gender})" if agent.gender else ""
            display = f"{default_mark} {agent.name}{gender}\n"
            display += f"    执业证号: {agent.license_no or '未填写'} | 律所: {agent.law_firm or '未填写'}"
            
            item.setText(display)
            item.setData(Qt.ItemDataRole.UserRole, agent.id)
            
            if agent.is_default:
                item.setBackground(QColor("#fff3e0"))
            
            self.agent_list.addItem(item)
    
    def _add_agent(self):
        """添加代理人"""
        dialog = AgentEditDialog(self.manager, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_agents()
    
    def _edit_agent(self, item):
        """编辑代理人"""
        agent_id = item.data(Qt.ItemDataRole.UserRole)
        dialog = AgentEditDialog(self.manager, agent_id, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._load_agents()


class AgentEditDialog(QDialog):
    """代理人信息编辑对话框"""
    def __init__(self, manager, agent_id=None, parent=None):
        super().__init__(parent)
        self.manager = manager
        self.agent_id = agent_id
        self.is_edit = agent_id is not None
        
        self.setWindowTitle("编辑代理人信息" if self.is_edit else "添加代理人信息")
        self.setMinimumSize(500, 450)
        self._create_ui()
        
        if self.is_edit:
            self._load_data()
    
    def _create_ui(self):
        layout = QFormLayout(self)
        layout.setSpacing(15)
        
        # 姓名
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("代理人姓名")
        layout.addRow("姓名*：", self.name_input)
        
        # 性别
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["", "男", "女"])
        layout.addRow("性别：", self.gender_combo)
        
        # 身份证号
        self.id_card_input = QLineEdit()
        self.id_card_input.setPlaceholderText("身份证号码")
        layout.addRow("身份证号：", self.id_card_input)
        
        # 电话
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("联系电话")
        layout.addRow("电话：", self.phone_input)
        
        # 执业证号
        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("律师执业证号")
        layout.addRow("执业证号：", self.license_input)
        
        # 律所
        self.law_firm_input = QLineEdit()
        self.law_firm_input.setPlaceholderText("所属律师事务所")
        layout.addRow("律师事务所：", self.law_firm_input)
        
        # 设为默认
        self.default_check = QCheckBox("设为默认代理人")
        layout.addRow("", self.default_check)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        save_btn.clicked.connect(self._save)
        btn_layout.addWidget(save_btn)
        
        layout.addRow(btn_layout)
    
    def _load_data(self):
        """加载代理人数据"""
        agent = self.manager.get_agent_by_id(self.agent_id)
        if agent:
            self.name_input.setText(agent.name)
            self.gender_combo.setCurrentText(agent.gender)
            self.id_card_input.setText(agent.id_card)
            self.phone_input.setText(agent.phone)
            self.license_input.setText(agent.license_no)
            self.law_firm_input.setText(agent.law_firm)
            self.default_check.setChecked(agent.is_default)
    
    def _save(self):
        """保存"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "提示", "请输入姓名")
            return
        
        data = {
            'name': name,
            'gender': self.gender_combo.currentText(),
            'id_card': self.id_card_input.text(),
            'phone': self.phone_input.text(),
            'license_no': self.license_input.text(),
            'law_firm': self.law_firm_input.text(),
            'is_default': self.default_check.isChecked()
        }
        
        try:
            if self.is_edit:
                self.manager.update_agent(self.agent_id, **data)
            else:
                self.manager.add_agent(**data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "保存失败", str(e))
