# -*- mode: python ; coding: utf-8 -*-
"""
常用信息库模块
存储常用的公司信息和代理人信息，供文书生成时调用
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import json


@dataclass
class CompanyInfo:
    """常用公司信息"""
    id: int
    name: str                           # 公司名称
    credit_code: str = ""               # 统一社会信用代码
    address: str = ""                   # 住所
    legal_rep: str = ""                 # 法定代表人
    phone: str = ""                     # 联系电话
    is_default: bool = False            # 是否设为默认
    created_at: str = ""
    updated_at: str = ""


@dataclass
class AgentInfo:
    """常用代理人信息"""
    id: int
    name: str                           # 姓名
    gender: str = ""                    # 性别
    id_card: str = ""                   # 身份证号
    phone: str = ""                     # 电话
    license_no: str = ""                # 执业证号
    law_firm: str = ""                  # 所属律所
    is_default: bool = False            # 是否设为默认
    created_at: str = ""
    updated_at: str = ""


class CommonInfoManager:
    """常用信息管理器"""
    
    def __init__(self, db_connection: sqlite3.Connection):
        self.conn = db_connection
        self.cursor = db_connection.cursor()
        self._ensure_tables()
    
    def _ensure_tables(self):
        """确保表存在"""
        # 常用公司信息表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS common_companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                credit_code TEXT DEFAULT '',
                address TEXT DEFAULT '',
                legal_rep TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 常用代理人信息表
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS common_agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                gender TEXT DEFAULT '',
                id_card TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                license_no TEXT DEFAULT '',
                law_firm TEXT DEFAULT '',
                is_default BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    # ==================== 公司信息管理 ====================
    
    def add_company(self, name: str, credit_code: str = "", address: str = "",
                    legal_rep: str = "", phone: str = "", is_default: bool = False) -> int:
        """添加常用公司"""
        now = datetime.now().isoformat()
        
        # 如果设为默认，取消其他默认
        if is_default:
            self.cursor.execute("UPDATE common_companies SET is_default = 0")
        
        self.cursor.execute("""
            INSERT INTO common_companies 
            (name, credit_code, address, legal_rep, phone, is_default, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, credit_code, address, legal_rep, phone, 1 if is_default else 0, now, now))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_company(self, company_id: int, **kwargs):
        """更新公司信息"""
        allowed_fields = ['name', 'credit_code', 'address', 'legal_rep', 'phone', 'is_default']
        
        # 如果设为默认，取消其他默认
        if kwargs.get('is_default'):
            self.cursor.execute("UPDATE common_companies SET is_default = 0")
        
        updates = []
        values = []
        for field in allowed_fields:
            if field in kwargs:
                updates.append(f"{field} = ?")
                values.append(kwargs[field] if field != 'is_default' else (1 if kwargs[field] else 0))
        
        if updates:
            updates.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(company_id)
            
            sql = f"UPDATE common_companies SET {', '.join(updates)} WHERE id = ?"
            self.cursor.execute(sql, values)
            self.conn.commit()
    
    def delete_company(self, company_id: int):
        """删除公司"""
        self.cursor.execute("DELETE FROM common_companies WHERE id = ?", (company_id,))
        self.conn.commit()
    
    def get_company_by_id(self, company_id: int) -> Optional[CompanyInfo]:
        """根据ID获取公司"""
        self.cursor.execute("SELECT * FROM common_companies WHERE id = ?", (company_id,))
        row = self.cursor.fetchone()
        return self._row_to_company(row) if row else None
    
    def get_all_companies(self) -> List[CompanyInfo]:
        """获取所有公司（默认排在最前）"""
        self.cursor.execute("""
            SELECT * FROM common_companies 
            ORDER BY is_default DESC, updated_at DESC
        """)
        rows = self.cursor.fetchall()
        return [self._row_to_company(row) for row in rows]
    
    def get_default_company(self) -> Optional[CompanyInfo]:
        """获取默认公司"""
        self.cursor.execute("SELECT * FROM common_companies WHERE is_default = 1 LIMIT 1")
        row = self.cursor.fetchone()
        return self._row_to_company(row) if row else None
    
    def _row_to_company(self, row) -> CompanyInfo:
        """转换行为对象"""
        def get_val(key, default=""):
            try:
                return row[key] if row[key] is not None else default
            except:
                return default
        
        return CompanyInfo(
            id=row['id'],
            name=row['name'],
            credit_code=get_val('credit_code'),
            address=get_val('address'),
            legal_rep=get_val('legal_rep'),
            phone=get_val('phone'),
            is_default=bool(get_val('is_default', 0)),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    # ==================== 代理人信息管理 ====================
    
    def add_agent(self, name: str, gender: str = "", id_card: str = "",
                  phone: str = "", license_no: str = "", law_firm: str = "",
                  is_default: bool = False) -> int:
        """添加常用代理人"""
        now = datetime.now().isoformat()
        
        # 如果设为默认，取消其他默认
        if is_default:
            self.cursor.execute("UPDATE common_agents SET is_default = 0")
        
        self.cursor.execute("""
            INSERT INTO common_agents 
            (name, gender, id_card, phone, license_no, law_firm, is_default, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, gender, id_card, phone, license_no, law_firm, 1 if is_default else 0, now, now))
        
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_agent(self, agent_id: int, **kwargs):
        """更新代理人信息"""
        allowed_fields = ['name', 'gender', 'id_card', 'phone', 'license_no', 'law_firm', 'is_default']
        
        # 如果设为默认，取消其他默认
        if kwargs.get('is_default'):
            self.cursor.execute("UPDATE common_agents SET is_default = 0")
        
        updates = []
        values = []
        for field in allowed_fields:
            if field in kwargs:
                updates.append(f"{field} = ?")
                values.append(kwargs[field] if field != 'is_default' else (1 if kwargs[field] else 0))
        
        if updates:
            updates.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(agent_id)
            
            sql = f"UPDATE common_agents SET {', '.join(updates)} WHERE id = ?"
            self.cursor.execute(sql, values)
            self.conn.commit()
    
    def delete_agent(self, agent_id: int):
        """删除代理人"""
        self.cursor.execute("DELETE FROM common_agents WHERE id = ?", (agent_id,))
        self.conn.commit()
    
    def get_agent_by_id(self, agent_id: int) -> Optional[AgentInfo]:
        """根据ID获取代理人"""
        self.cursor.execute("SELECT * FROM common_agents WHERE id = ?", (agent_id,))
        row = self.cursor.fetchone()
        return self._row_to_agent(row) if row else None
    
    def get_all_agents(self) -> List[AgentInfo]:
        """获取所有代理人（默认排在最前）"""
        self.cursor.execute("""
            SELECT * FROM common_agents 
            ORDER BY is_default DESC, updated_at DESC
        """)
        rows = self.cursor.fetchall()
        return [self._row_to_agent(row) for row in rows]
    
    def get_default_agent(self) -> Optional[AgentInfo]:
        """获取默认代理人"""
        self.cursor.execute("SELECT * FROM common_agents WHERE is_default = 1 LIMIT 1")
        row = self.cursor.fetchone()
        return self._row_to_agent(row) if row else None
    
    def _row_to_agent(self, row) -> AgentInfo:
        """转换行为对象"""
        def get_val(key, default=""):
            try:
                return row[key] if row[key] is not None else default
            except:
                return default
        
        return AgentInfo(
            id=row['id'],
            name=row['name'],
            gender=get_val('gender'),
            id_card=get_val('id_card'),
            phone=get_val('phone'),
            license_no=get_val('license_no'),
            law_firm=get_val('law_firm'),
            is_default=bool(get_val('is_default', 0)),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
