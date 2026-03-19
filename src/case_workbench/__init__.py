#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
案件工作台模块
劳动法数据库 - 我的案件工作台功能
"""

from .models import (
    CaseWorkbenchManager,
    WorkbenchCase,
    DefenseTemplate,
    CaseTopic,
    CaseDocument,
    CASE_CAUSES,
    CASE_STATUSES
)

from .common_info import (
    CommonInfoManager,
    CompanyInfo,
    AgentInfo
)

from .document_generator import DocumentGenerator

from .workbench_widget import (
    CaseWorkbenchWidget,
    CaseCard,
    CaseEditDialog,
    DocumentGenerateDialog
)

from .template_manager import (
    TemplateManagerWidget,
    TemplateEditDialog,
    ParagraphEditDialog
)

__all__ = [
    # 模型
    'CaseWorkbenchManager',
    'WorkbenchCase',
    'DefenseTemplate',
    'CaseTopic',
    'CaseDocument',
    'CASE_CAUSES',
    'CASE_STATUSES',
    
    # 常用信息
    'CommonInfoManager',
    'CompanyInfo',
    'AgentInfo',
    
    # 文书生成
    'DocumentGenerator',
    
    # 工作台界面
    'CaseWorkbenchWidget',
    'CaseCard',
    'CaseEditDialog',
    'DocumentGenerateDialog',
    
    # 模板管理
    'TemplateManagerWidget',
    'TemplateEditDialog',
    'ParagraphEditDialog',
]
