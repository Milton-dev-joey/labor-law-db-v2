#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案件工作台 - 数据模型和数据库管理
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import json


# ==================== 案由枚举 ====================

CASE_CAUSES = [
    "确认劳动关系纠纷",
    "追索劳动报酬纠纷", 
    "经济补偿金纠纷",
    "违法解除劳动合同赔偿金纠纷",
    "工伤保险待遇纠纷",
    "竞业限制纠纷"
]

# ==================== 案件状态枚举 ====================

CASE_STATUSES = {
    'pending': '待处理',
    'preparing': '准备中',
    'submitted': '已立案/应诉',
    'hearing': '已开庭',
    'judged': '已判决',
    'closed': '已结案'
}


# ==================== 数据模型 ====================

@dataclass
class WorkbenchCase:
    """案件工作台案件模型"""
    id: int
    title: str
    # 当事主体
    plaintiff: str = ""                    # 原告/申请人
    plaintiff_type: str = "自然人"          # 原告类型
    defendant: str = ""                    # 被告/被申请人
    defendant_type: str = "法人"            # 被告类型
    
    # 公司信息（被告为法人时）⭐
    company_name: str = ""                 # 公司名称
    company_credit_code: str = ""          # 统一社会信用代码
    company_address: str = ""              # 公司住所
    company_legal_rep: str = ""            # 法定代表人姓名
    
    # 法院信息
    court: str = ""                        # 管辖法院
    case_number: str = ""                  # 案号
    
    # 日期
    receive_date: Optional[str] = None     # 收到材料日期
    evidence_deadline: Optional[str] = None # 举证期限
    hearing_date: Optional[str] = None     # 开庭日期
    hearing_time: str = "09:00"            # 开庭时间
    
    # 代理信息
    lawyer_name: str = ""                  # 代理律师
    lawyer_gender: str = ""                # 律师性别 ⭐
    lawyer_id_card: str = ""               # 律师身份证号 ⭐
    lawyer_phone: str = ""                 # 律师电话 ⭐
    lawyer_license: str = ""               # 执业证号
    law_firm: str = ""                     # 律师事务所
    
    # 案件信息
    case_cause: str = ""                   # 案由
    case_amount: float = 0.0               # 诉讼标的金额
    case_facts: str = ""                   # 案情简介
    
    # 专题关联
    topic_tags: List[str] = field(default_factory=list)  # 关联专题标签
    
    # 状态和紧急度
    status: str = "pending"                # 案件状态
    is_urgent: bool = False                # 是否紧急
    
    # 时间戳
    created_at: str = ""
    updated_at: str = ""


@dataclass
class DefenseTemplate:
    """答辩状模板"""
    id: int
    case_cause: str                        # 案由
    template_name: str                     # 模板名称
    template_content: str                  # 模板内容
    paragraph_sections: Dict[str, Any] = field(default_factory=dict)  # 段落结构JSON
    common_defenses: List[str] = field(default_factory=list)          # 常见抗辩要点
    legal_basis: List[str] = field(default_factory=list)              # 关联法律依据
    is_builtin: bool = True                # 是否内置模板
    created_at: str = ""
    updated_at: str = ""


@dataclass
class CaseTopic:
    """案件专题"""
    id: int
    topic_name: str                        # 专题名称
    topic_key: str                         # 专题标识
    case_causes: List[str] = field(default_factory=list)              # 关联案由
    common_claims: List[str] = field(default_factory=list)            # 常见诉请
    defense_strategies: Dict[str, Any] = field(default_factory=dict)  # 抗辩策略
    legal_articles: List[str] = field(default_factory=list)           # 关联法条
    typical_cases: List[str] = field(default_factory=list)            # 典型案例
    created_at: str = ""


@dataclass
class CaseDocument:
    """案件文书"""
    id: int
    case_id: int                           # 关联案件ID
    doc_type: str                          # 文书类型
    doc_name: str                          # 文书名称
    doc_content: str = ""                  # 文书内容
    file_path: str = ""                    # 生成文件路径
    created_at: str = ""


# ==================== 数据库管理器 ====================

class CaseWorkbenchManager:
    """案件工作台管理器"""
    
    # 案由与专题的自动匹配映射
    TOPIC_MAPPING = {
        "确认劳动关系纠纷": ["outsourcing_labor", "double_relationship"],
        "追索劳动报酬纠纷": ["wage_claim", "overtime_pay"],
        "经济补偿金纠纷": ["severance_calc", "severance_dispute"],
        "违法解除劳动合同赔偿金纠纷": ["illegal_termination", "termination_evidence"],
        "工伤保险待遇纠纷": ["work_injury", "injury_compensation"],
        "竞业限制纠纷": ["non_compete", "competition_restrictions"]
    }
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.cursor = db_connection.cursor()
        self._ensure_tables()
        self._init_default_data()
    
    def _ensure_tables(self):
        """确保所有必要的表存在"""
        
        # 1. 扩展 cases 表（添加新字段）
        new_columns = [
            ("plaintiff", "TEXT", "''"),
            ("plaintiff_type", "TEXT", "'自然人'"),
            ("defendant", "TEXT", "''"),
            ("defendant_type", "TEXT", "'法人'"),
            ("company_name", "TEXT", "''"),
            ("company_credit_code", "TEXT", "''"),
            ("company_address", "TEXT", "''"),
            ("company_legal_rep", "TEXT", "''"),
            ("court", "TEXT", "''"),
            ("case_number", "TEXT", "''"),
            ("receive_date", "DATE", "NULL"),
            ("evidence_deadline", "DATE", "NULL"),
            ("hearing_date", "DATE", "NULL"),
            ("hearing_time", "TEXT", "'09:00'"),
            ("lawyer_name", "TEXT", "''"),
            ("lawyer_gender", "TEXT", "''"),
            ("lawyer_id_card", "TEXT", "''"),
            ("lawyer_phone", "TEXT", "''"),
            ("lawyer_license", "TEXT", "''"),
            ("law_firm", "TEXT", "''"),
            ("case_cause", "TEXT", "''"),
            ("case_amount", "DECIMAL", "0"),
            ("case_facts", "TEXT", "''"),
            ("topic_tags", "TEXT", "'[]'"),
            ("is_urgent", "BOOLEAN", "0"),
            ("status", "TEXT", "'pending'")
        ]
        
        for col_name, col_type, default in new_columns:
            try:
                self.cursor.execute(f"ALTER TABLE cases ADD COLUMN {col_name} {col_type} DEFAULT {default}")
            except sqlite3.OperationalError:
                # 列已存在，忽略错误
                pass
        
        # 2. 创建 defense_templates 表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS defense_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_cause TEXT NOT NULL,
                template_name TEXT NOT NULL,
                template_content TEXT NOT NULL,
                paragraph_sections TEXT DEFAULT '{}',
                common_defenses TEXT DEFAULT '[]',
                legal_basis TEXT DEFAULT '[]',
                is_builtin BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 3. 创建 case_topics 表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS case_topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_name TEXT NOT NULL,
                topic_key TEXT UNIQUE NOT NULL,
                case_causes TEXT DEFAULT '[]',
                common_claims TEXT DEFAULT '[]',
                defense_strategies TEXT DEFAULT '{}',
                legal_articles TEXT DEFAULT '[]',
                typical_cases TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 4. 创建 case_documents 表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS case_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                doc_type TEXT NOT NULL,
                doc_name TEXT NOT NULL,
                doc_content TEXT DEFAULT '',
                file_path TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
            )
        """)
        
        # 创建索引
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_cases_hearing_date ON cases(hearing_date)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_cases_case_cause ON cases(case_cause)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_defense_templates_case_cause ON defense_templates(case_cause)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_case_documents_case_id ON case_documents(case_id)")
        
        self.conn.commit()
    
    def _init_default_data(self):
        """初始化默认数据"""
        # 检查是否已有专题数据
        self.cursor.execute("SELECT COUNT(*) FROM case_topics")
        if self.cursor.fetchone()[0] == 0:
            self._init_default_topics()
        
        # 检查是否已有答辩状模板
        self.cursor.execute("SELECT COUNT(*) FROM defense_templates")
        if self.cursor.fetchone()[0] == 0:
            self._init_default_templates()
    
    def _init_default_topics(self):
        """初始化默认专题数据"""
        topics = [
            {
                "topic_name": "外包员工劳动关系认定",
                "topic_key": "outsourcing_labor",
                "case_causes": ["确认劳动关系纠纷"],
                "common_claims": ["确认存在劳动关系", "支付未签劳动合同二倍工资差额"],
                "defense_strategies": {
                    "key_points": ["从属性缺失", "报酬支付主体", "管理控制主体"],
                    "evidence_focus": ["外包合同", "工资发放记录", "社保缴纳记录"]
                },
                "legal_articles": ["《劳动合同法》第7条", "《关于确立劳动关系有关事项的通知》第1条"],
                "typical_cases": []
            },
            {
                "topic_name": "双重劳动关系认定",
                "topic_key": "double_relationship",
                "case_causes": ["确认劳动关系纠纷"],
                "common_claims": ["确认存在劳动关系", "经济补偿金"],
                "defense_strategies": {
                    "key_points": ["后单位明知", "原单位未解除劳动合同", "社保关系"],
                    "evidence_focus": ["原单位劳动合同", "社保缴纳记录", "入职登记表"]
                },
                "legal_articles": ["《劳动合同法》第39条", "《关于审理劳动争议案件适用法律问题的解释（一）》第32条"],
                "typical_cases": []
            },
            {
                "topic_name": "经济补偿金计算争议",
                "topic_key": "severance_calc",
                "case_causes": ["经济补偿金纠纷"],
                "common_claims": ["支付经济补偿金", "补足经济补偿金差额"],
                "defense_strategies": {
                    "key_points": ["工作年限计算", "月工资标准", "12个月封顶"],
                    "evidence_focus": ["劳动合同", "工资流水", "社保缴费基数"]
                },
                "legal_articles": ["《劳动合同法》第47条", "《劳动合同法实施条例》第27条"],
                "typical_cases": []
            },
            {
                "topic_name": "违法解除抗辩",
                "topic_key": "illegal_termination",
                "case_causes": ["违法解除劳动合同赔偿金纠纷"],
                "common_claims": ["支付违法解除劳动合同赔偿金"],
                "defense_strategies": {
                    "key_points": ["严重违纪", "严重失职", "客观情况变化", "试用期不符合录用条件"],
                    "evidence_focus": ["员工手册", "违纪证据", "绩效考核记录"]
                },
                "legal_articles": ["《劳动合同法》第39条", "《劳动合同法》第40条", "《劳动合同法》第87条"],
                "typical_cases": []
            },
            {
                "topic_name": "工伤待遇争议",
                "topic_key": "work_injury",
                "case_causes": ["工伤保险待遇纠纷"],
                "common_claims": ["支付工伤医疗费", "支付一次性伤残补助金", "支付伤残津贴"],
                "defense_strategies": {
                    "key_points": ["工伤认定", "伤残等级", "本人工资标准", "是否参保"],
                    "evidence_focus": ["工伤认定书", "劳动能力鉴定结论", "工伤保险缴费记录"]
                },
                "legal_articles": ["《工伤保险条例》第33-37条", "《社会保险法》第38-39条"],
                "typical_cases": []
            },
            {
                "topic_name": "竞业限制争议",
                "topic_key": "non_compete",
                "case_causes": ["竞业限制纠纷"],
                "common_claims": ["支付竞业限制补偿金", "继续履行竞业限制义务", "支付违约金"],
                "defense_strategies": {
                    "key_points": ["竞业限制主体资格", "竞业限制范围", "补偿金标准", "违约金合理性"],
                    "evidence_focus": ["竞业限制协议", "新单位工商信息", "补偿金支付记录"]
                },
                "legal_articles": ["《劳动合同法》第23-24条", "《最高人民法院关于审理劳动争议案件适用法律问题的解释（一）》第36-40条"],
                "typical_cases": []
            }
        ]
        
        for topic in topics:
            self.cursor.execute("""
                INSERT INTO case_topics 
                (topic_name, topic_key, case_causes, common_claims, defense_strategies, legal_articles, typical_cases)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                topic["topic_name"],
                topic["topic_key"],
                json.dumps(topic["case_causes"], ensure_ascii=False),
                json.dumps(topic["common_claims"], ensure_ascii=False),
                json.dumps(topic["defense_strategies"], ensure_ascii=False),
                json.dumps(topic["legal_articles"], ensure_ascii=False),
                json.dumps(topic["typical_cases"], ensure_ascii=False)
            ))
        
        self.conn.commit()
    
    def _init_default_templates(self):
        """初始化默认答辩状模板"""
        templates = [
            {
                "case_cause": "确认劳动关系纠纷",
                "template_name": "标准答辩状-确认劳动关系",
                "template_content": "",  # 由段落组合生成
                "paragraph_sections": json.dumps({
                    "header": {
                        "type": "fixed",
                        "title": "文书头部",
                        "content": "民 事 答 辩 状\n\n答辩人：{defendant}\n住所地：{defendant_address}\n法定代表人/负责人：{legal_rep}\n\n被答辩人（原告）：{plaintiff}\n\n答辩人因与被答辩人{case_cause}一案，现提出答辩如下："
                    },
                    "facts_options": [
                        {
                            "type": "optional",
                            "title": "不存在劳动关系-外包模式",
                            "content": "被告与原告之间不存在劳动关系。原告系与{third_party}签订劳动合同，其工资由{third_party}发放，社会保险由{third_party}缴纳，日常工作接受{third_party}的管理和安排。\n\n被告与{third_party}之间签订有合法有效的外包服务合同，原告在被告处工作是基于外包服务合同的约定，并非与被告建立劳动关系。"
                        },
                        {
                            "type": "optional",
                            "title": "不存在劳动关系-劳务派遣",
                            "content": "被告与原告之间不存在劳动关系。原告系由{dispatch_company}派遣至被告处工作，其用人单位为{dispatch_company}，与被告仅为用工单位与派遣员工的关系。\n\n原告的工资由{dispatch_company}发放，社会保险由{dispatch_company}缴纳，劳动合同亦与{dispatch_company}签订。"
                        },
                        {
                            "type": "optional",
                            "title": "存在劳务关系而非劳动关系",
                            "content": "被告与原告之间仅存在劳务关系，而非劳动关系。原告为被告提供的是临时性、项目性的劳务服务，双方之间不存在管理与被管理的人身依附关系。\n\n原告的工作时间、工作方式均由其自行安排，不受被告规章制度的约束，报酬按项目或按工作量结算，不具有工资的稳定性和周期性特征。"
                        }
                    ],
                    "defense_options": [
                        {
                            "type": "optional",
                            "title": "从属性缺失抗辩",
                            "content": "一、从属性缺失，不符合劳动关系特征\n\n根据《关于确立劳动关系有关事项的通知》第1条规定，劳动关系的成立需同时具备以下情形：(1)用人单位和劳动者符合法律、法规规定的主体资格；(2)用人单位依法制定的各项劳动规章制度适用于劳动者，劳动者受用人单位的劳动管理，从事用人单位安排的有报酬的劳动；(3)劳动者提供的劳动是用人单位业务的组成部分。\n\n本案中，原告不受被告劳动规章制度的约束，日常工作不受被告的考勤、考核管理，双方之间不存在人身依附关系，不符合劳动关系的从属性特征。"
                        },
                        {
                            "type": "optional",
                            "title": "报酬支付主体抗辩",
                            "content": "二、报酬支付主体非被告\n\n原告的劳动报酬并非由被告支付，而是由{third_party}支付。根据银行流水记录，原告每月收到的款项均由{third_party}账户转出，被告从未向原告支付过任何劳动报酬。"
                        },
                        {
                            "type": "optional",
                            "title": "社保缴纳主体抗辩",
                            "content": "三、社会保险由第三方缴纳\n\n原告的社会保险一直由{third_party}依法缴纳，被告并非原告的社保缴纳主体。社会保险的缴纳是认定劳动关系的重要参考因素，原告的社保缴纳情况足以证明其与被告之间不存在劳动关系。"
                        }
                    ],
                    "legal_basis": {
                        "type": "selectable",
                        "title": "法律依据",
                        "options": [
                            "《中华人民共和国劳动合同法》第七条",
                            "《关于确立劳动关系有关事项的通知》第一条",
                            "《关于确立劳动关系有关事项的通知》第二条"
                        ]
                    },
                    "footer": {
                        "type": "fixed",
                        "title": "文书尾部",
                        "content": "\n综上所述，被告与原告之间不存在劳动关系，原告的诉讼请求缺乏事实和法律依据，恳请贵院依法驳回原告的全部诉讼请求。\n\n此致\n\n{court}\n\n\n\n答辩人：{defendant}（盖章）\n\n日期：{date}"
                    }
                }, ensure_ascii=False),
                "common_defenses": json.dumps([
                    "从属性缺失：原告不受被告劳动规章制度约束",
                    "报酬支付：原告报酬由第三方支付，非被告支付",
                    "工作管理：原告日常工作由第三方安排管理",
                    "社保缴纳：原告社会保险由第三方缴纳"
                ], ensure_ascii=False),
                "legal_basis": json.dumps([
                    "《劳动合同法》第7条",
                    "《关于确立劳动关系有关事项的通知》第1条",
                    "《关于确立劳动关系有关事项的通知》第2条"
                ], ensure_ascii=False),
                "is_builtin": 1
            }
        ]
        
        for template in templates:
            self.cursor.execute("""
                INSERT INTO defense_templates 
                (case_cause, template_name, template_content, paragraph_sections, common_defenses, legal_basis, is_builtin)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                template["case_cause"],
                template["template_name"],
                template["template_content"],
                template["paragraph_sections"],
                template["common_defenses"],
                template["legal_basis"],
                template["is_builtin"]
            ))
        
        self.conn.commit()
    
    # ==================== 案件 CRUD ====================
    
    def add_case(self, **kwargs) -> int:
        """添加案件"""
        now = datetime.now().isoformat()
        
        # 自动匹配专题
        if 'case_cause' in kwargs and kwargs['case_cause']:
            kwargs['topic_tags'] = self.auto_match_topics(kwargs['case_cause'])
        else:
            kwargs['topic_tags'] = []
        
        # 检查紧急度
        kwargs['is_urgent'] = self._check_urgent(
            kwargs.get('hearing_date'),
            kwargs.get('evidence_deadline')
        )
        
        fields = [
            'title', 'plaintiff', 'plaintiff_type', 'defendant', 'defendant_type',
            'company_name', 'company_credit_code', 'company_address', 'company_legal_rep',
            'court', 'case_number', 'receive_date', 'evidence_deadline',
            'hearing_date', 'hearing_time', 'lawyer_name', 'lawyer_gender',
            'lawyer_id_card', 'lawyer_phone', 'lawyer_license',
            'law_firm', 'case_cause', 'case_amount', 'case_facts', 'topic_tags',
            'is_urgent', 'status'
        ]
        
        values = []
        for field in fields:
            value = kwargs.get(field)
            if field == 'topic_tags' and isinstance(value, list):
                value = json.dumps(value, ensure_ascii=False)
            elif field == 'case_amount':
                value = float(value) if value else 0.0
            elif field == 'is_urgent':
                value = 1 if value else 0
            values.append(value)
        
        values.extend([now, now])  # created_at, updated_at
        
        placeholders = ', '.join(['?' for _ in range(len(fields) + 2)])
        fields_str = ', '.join(fields + ['created_at', 'updated_at'])
        
        sql = f"INSERT INTO cases ({fields_str}) VALUES ({placeholders})"
        self.cursor.execute(sql, values)
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_case(self, case_id: int, **kwargs):
        """更新案件"""
        allowed_fields = [
            'title', 'plaintiff', 'plaintiff_type', 'defendant', 'defendant_type',
            'company_name', 'company_credit_code', 'company_address', 'company_legal_rep',
            'court', 'case_number', 'receive_date', 'evidence_deadline',
            'hearing_date', 'hearing_time', 'lawyer_name', 'lawyer_gender',
            'lawyer_id_card', 'lawyer_phone', 'lawyer_license',
            'law_firm', 'case_cause', 'case_amount', 'case_facts', 'topic_tags',
            'is_urgent', 'status'
        ]
        
        updates = []
        params = []
        
        # 如果案由改变，自动更新专题匹配
        if 'case_cause' in kwargs:
            kwargs['topic_tags'] = self.auto_match_topics(kwargs['case_cause'])
        
        # 检查紧急度
        if 'hearing_date' in kwargs or 'evidence_deadline' in kwargs:
            # 获取现有日期
            self.cursor.execute("SELECT hearing_date, evidence_deadline FROM cases WHERE id = ?", (case_id,))
            row = self.cursor.fetchone()
            hearing_date = kwargs.get('hearing_date', row['hearing_date'] if row else None)
            evidence_deadline = kwargs.get('evidence_deadline', row['evidence_deadline'] if row else None)
            kwargs['is_urgent'] = self._check_urgent(hearing_date, evidence_deadline)
        
        for field in allowed_fields:
            if field in kwargs:
                updates.append(f"{field} = ?")
                value = kwargs[field]
                if field == 'topic_tags' and isinstance(value, list):
                    value = json.dumps(value, ensure_ascii=False)
                elif field == 'case_amount':
                    value = float(value) if value else 0.0
                elif field == 'is_urgent':
                    value = 1 if value else 0
                params.append(value)
        
        if not updates:
            return
        
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(case_id)
        
        sql = f"UPDATE cases SET {', '.join(updates)} WHERE id = ?"
        self.cursor.execute(sql, params)
        self.conn.commit()
    
    def get_case_by_id(self, case_id: int) -> Optional[WorkbenchCase]:
        """根据ID获取案件"""
        self.cursor.execute("SELECT * FROM cases WHERE id = ?", (case_id,))
        row = self.cursor.fetchone()
        return self._row_to_workbench_case(row) if row else None
    
    def get_cases(self, status: str = None, is_urgent: bool = None, 
                  case_cause: str = None, keyword: str = None) -> List[WorkbenchCase]:
        """获取案件列表，支持筛选"""
        conditions = []
        params = []
        
        if status:
            conditions.append("status = ?")
            params.append(status)
        
        if is_urgent is not None:
            conditions.append("is_urgent = ?")
            params.append(1 if is_urgent else 0)
        
        if case_cause:
            conditions.append("case_cause = ?")
            params.append(case_cause)
        
        if keyword:
            keyword_pattern = f"%{keyword}%"
            conditions.append("(title LIKE ? OR plaintiff LIKE ? OR defendant LIKE ? OR court LIKE ?)")
            params.extend([keyword_pattern, keyword_pattern, keyword_pattern, keyword_pattern])
        
        if conditions:
            sql = f"SELECT * FROM cases WHERE {' AND '.join(conditions)} ORDER BY is_urgent DESC, hearing_date ASC NULLS LAST, created_at DESC"
        else:
            sql = "SELECT * FROM cases ORDER BY is_urgent DESC, hearing_date ASC NULLS LAST, created_at DESC"
        
        self.cursor.execute(sql, params)
        rows = self.cursor.fetchall()
        return [self._row_to_workbench_case(row) for row in rows]
    
    def get_urgent_cases(self) -> List[WorkbenchCase]:
        """获取紧急案件（开庭<7天或举证<3天）"""
        sql = """
            SELECT *, 
                CASE 
                    WHEN hearing_date <= date('now', '+7 days') THEN 1
                    WHEN evidence_deadline <= date('now', '+3 days') THEN 1
                    ELSE 0
                END as is_urgent_calc
            FROM cases
            WHERE status != 'closed'
                AND (hearing_date <= date('now', '+7 days') 
                     OR evidence_deadline <= date('now', '+3 days'))
            ORDER BY hearing_date ASC, evidence_deadline ASC
        """
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        return [self._row_to_workbench_case(row) for row in rows]
    
    def delete_case(self, case_id: int):
        """删除案件"""
        self.cursor.execute("DELETE FROM cases WHERE id = ?", (case_id,))
        self.conn.commit()
    
    def _check_urgent(self, hearing_date: Optional[str], evidence_deadline: Optional[str]) -> bool:
        """检查是否紧急"""
        today = datetime.now().date()
        
        if hearing_date:
            try:
                hearing = datetime.strptime(hearing_date, '%Y-%m-%d').date()
                if (hearing - today).days <= 7:
                    return True
            except:
                pass
        
        if evidence_deadline:
            try:
                evidence = datetime.strptime(evidence_deadline, '%Y-%m-%d').date()
                if (evidence - today).days <= 3:
                    return True
            except:
                pass
        
        return False
    
    # ==================== 专题管理 ====================
    
    def auto_match_topics(self, case_cause: str) -> List[str]:
        """根据案由自动匹配专题"""
        return self.TOPIC_MAPPING.get(case_cause, [])
    
    def get_all_topics(self) -> List[CaseTopic]:
        """获取所有专题"""
        self.cursor.execute("SELECT * FROM case_topics ORDER BY topic_name")
        rows = self.cursor.fetchall()
        return [self._row_to_case_topic(row) for row in rows]
    
    def get_topics_by_case_cause(self, case_cause: str) -> List[CaseTopic]:
        """根据案由获取相关专题"""
        sql = "SELECT * FROM case_topics WHERE case_causes LIKE ? ORDER BY topic_name"
        self.cursor.execute(sql, (f'%"{case_cause}"%',))
        rows = self.cursor.fetchall()
        return [self._row_to_case_topic(row) for row in rows]
    
    def get_topic_by_key(self, topic_key: str) -> Optional[CaseTopic]:
        """根据key获取专题"""
        self.cursor.execute("SELECT * FROM case_topics WHERE topic_key = ?", (topic_key,))
        row = self.cursor.fetchone()
        return self._row_to_case_topic(row) if row else None
    
    # ==================== 答辩状模板管理 ====================
    
    def get_templates_by_case_cause(self, case_cause: str) -> List[DefenseTemplate]:
        """根据案由获取答辩状模板"""
        self.cursor.execute(
            "SELECT * FROM defense_templates WHERE case_cause = ? ORDER BY is_builtin DESC, created_at DESC",
            (case_cause,)
        )
        rows = self.cursor.fetchall()
        return [self._row_to_defense_template(row) for row in rows]
    
    def get_template_by_id(self, template_id: int) -> Optional[DefenseTemplate]:
        """根据ID获取模板"""
        self.cursor.execute("SELECT * FROM defense_templates WHERE id = ?", (template_id,))
        row = self.cursor.fetchone()
        return self._row_to_defense_template(row) if row else None
    
    def add_template(self, case_cause: str, template_name: str, 
                     paragraph_sections: Dict, common_defenses: List[str],
                     legal_basis: List[str], is_builtin: bool = False) -> int:
        """添加自定义模板"""
        now = datetime.now().isoformat()
        sql = """
            INSERT INTO defense_templates 
            (case_cause, template_name, template_content, paragraph_sections, 
             common_defenses, legal_basis, is_builtin, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(sql, (
            case_cause, template_name, "",
            json.dumps(paragraph_sections, ensure_ascii=False),
            json.dumps(common_defenses, ensure_ascii=False),
            json.dumps(legal_basis, ensure_ascii=False),
            1 if is_builtin else 0,
            now, now
        ))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_template(self, template_id: int, **kwargs):
        """更新模板（仅自定义模板可修改）"""
        # 检查是否为内置模板
        self.cursor.execute("SELECT is_builtin FROM defense_templates WHERE id = ?", (template_id,))
        row = self.cursor.fetchone()
        if row and row['is_builtin']:
            raise ValueError("内置模板不可修改，请复制后修改")
        
        allowed_fields = ['template_name', 'paragraph_sections', 'common_defenses', 'legal_basis']
        
        updates = []
        params = []
        
        for field in allowed_fields:
            if field in kwargs:
                updates.append(f"{field} = ?")
                value = kwargs[field]
                if isinstance(value, (list, dict)):
                    value = json.dumps(value, ensure_ascii=False)
                params.append(value)
        
        if not updates:
            return
        
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(template_id)
        
        sql = f"UPDATE defense_templates SET {', '.join(updates)} WHERE id = ?"
        self.cursor.execute(sql, params)
        self.conn.commit()
    
    def delete_template(self, template_id: int):
        """删除模板（仅自定义模板可删除）"""
        self.cursor.execute("SELECT is_builtin FROM defense_templates WHERE id = ?", (template_id,))
        row = self.cursor.fetchone()
        if row and row['is_builtin']:
            raise ValueError("内置模板不可删除")
        
        self.cursor.execute("DELETE FROM defense_templates WHERE id = ?", (template_id,))
        self.conn.commit()
    
    def duplicate_template(self, template_id: int, new_name: str) -> int:
        """复制模板（用于基于内置模板创建自定义模板）"""
        template = self.get_template_by_id(template_id)
        if not template:
            raise ValueError("模板不存在")
        
        return self.add_template(
            case_cause=template.case_cause,
            template_name=new_name,
            paragraph_sections=template.paragraph_sections,
            common_defenses=template.common_defenses,
            legal_basis=template.legal_basis,
            is_builtin=False
        )
    
    # ==================== 文书历史 ====================
    
    def add_document(self, case_id: int, doc_type: str, doc_name: str,
                     doc_content: str = "", file_path: str = "") -> int:
        """添加文书记录"""
        sql = """
            INSERT INTO case_documents (case_id, doc_type, doc_name, doc_content, file_path)
            VALUES (?, ?, ?, ?, ?)
        """
        self.cursor.execute(sql, (case_id, doc_type, doc_name, doc_content, file_path))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_documents_by_case(self, case_id: int) -> List[CaseDocument]:
        """获取案件的所有文书"""
        self.cursor.execute(
            "SELECT * FROM case_documents WHERE case_id = ? ORDER BY created_at DESC",
            (case_id,)
        )
        rows = self.cursor.fetchall()
        return [self._row_to_case_document(row) for row in rows]
    
    def delete_document(self, doc_id: int):
        """删除文书记录"""
        self.cursor.execute("DELETE FROM case_documents WHERE id = ?", (doc_id,))
        self.conn.commit()
    
    # ==================== 辅助方法 ====================
    
    def _row_to_workbench_case(self, row) -> WorkbenchCase:
        """将数据库行转换为 WorkbenchCase 对象"""
        def get_value(key, default=None):
            try:
                return row[key] if row[key] is not None else default
            except (KeyError, IndexError):
                return default
        
        return WorkbenchCase(
            id=row['id'],
            title=row['title'],
            plaintiff=get_value('plaintiff', ''),
            plaintiff_type=get_value('plaintiff_type', '自然人'),
            defendant=get_value('defendant', ''),
            defendant_type=get_value('defendant_type', '法人'),
            company_name=get_value('company_name', ''),
            company_credit_code=get_value('company_credit_code', ''),
            company_address=get_value('company_address', ''),
            company_legal_rep=get_value('company_legal_rep', ''),
            court=get_value('court', ''),
            case_number=get_value('case_number', ''),
            receive_date=get_value('receive_date'),
            evidence_deadline=get_value('evidence_deadline'),
            hearing_date=get_value('hearing_date'),
            hearing_time=get_value('hearing_time', '09:00'),
            lawyer_name=get_value('lawyer_name', ''),
            lawyer_gender=get_value('lawyer_gender', ''),
            lawyer_id_card=get_value('lawyer_id_card', ''),
            lawyer_phone=get_value('lawyer_phone', ''),
            lawyer_license=get_value('lawyer_license', ''),
            law_firm=get_value('law_firm', ''),
            case_cause=get_value('case_cause', ''),
            case_amount=get_value('case_amount', 0.0) or 0.0,
            case_facts=get_value('case_facts', ''),
            topic_tags=json.loads(get_value('topic_tags', '[]') or '[]'),
            status=get_value('status', 'pending'),
            is_urgent=bool(get_value('is_urgent', 0)),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def _row_to_defense_template(self, row) -> DefenseTemplate:
        def get_value(key, default=None):
            try:
                return row[key] if row[key] is not None else default
            except (KeyError, IndexError):
                return default
        
        return DefenseTemplate(
            id=row['id'],
            case_cause=row['case_cause'],
            template_name=row['template_name'],
            template_content=row['template_content'],
            paragraph_sections=json.loads(get_value('paragraph_sections', '{}') or '{}'),
            common_defenses=json.loads(get_value('common_defenses', '[]') or '[]'),
            legal_basis=json.loads(get_value('legal_basis', '[]') or '[]'),
            is_builtin=bool(get_value('is_builtin', 1)),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def _row_to_case_topic(self, row) -> CaseTopic:
        def get_value(key, default=None):
            try:
                return row[key] if row[key] is not None else default
            except (KeyError, IndexError):
                return default
        
        return CaseTopic(
            id=row['id'],
            topic_name=row['topic_name'],
            topic_key=row['topic_key'],
            case_causes=json.loads(get_value('case_causes', '[]') or '[]'),
            common_claims=json.loads(get_value('common_claims', '[]') or '[]'),
            defense_strategies=json.loads(get_value('defense_strategies', '{}') or '{}'),
            legal_articles=json.loads(get_value('legal_articles', '[]') or '[]'),
            typical_cases=json.loads(get_value('typical_cases', '[]') or '[]'),
            created_at=row['created_at']
        )
    
    def _row_to_case_document(self, row) -> CaseDocument:
        def get_value(key, default=None):
            try:
                return row[key] if row[key] is not None else default
            except (KeyError, IndexError):
                return default
        
        return CaseDocument(
            id=row['id'],
            case_id=row['case_id'],
            doc_type=row['doc_type'],
            doc_name=row['doc_name'],
            doc_content=get_value('doc_content', ''),
            file_path=get_value('file_path', ''),
            created_at=row['created_at']
        )
