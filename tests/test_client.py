#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notion2SQL 客户端测试
"""

import unittest
import os
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# 加载环境变量用于测试
load_dotenv()

# 导入被测试的模块
from notion2sql import NotionClient, NotionPage, NotionDatabase

class TestNotionClient(unittest.TestCase):
    """测试Notion客户端类"""
    
    def setUp(self):
        """设置测试环境"""
        self.api_key = os.getenv("NOTION_API_KEY", "test_api_key")
        self.page_id = os.getenv("NOTION_PAGE_ID", "test_page_id")
        
    @patch('notion2sql.core.client.NotionApiClient')
    def test_client_initialization(self, mock_notion_api):
        """测试客户端初始化"""
        # 创建客户端
        client = NotionClient(api_key=self.api_key)
        
        # 验证是否调用了正确的API
        mock_notion_api.assert_called_once_with(auth=self.api_key)
        
        # 验证客户端属性
        self.assertEqual(client.api_key, self.api_key)
        self.assertIsNotNone(client.client)
        
    @patch('notion2sql.core.client.NotionApiClient')
    def test_connect_page_with_valid_id(self, mock_notion_api):
        """测试连接到有效页面"""
        # 创建模拟客户端和页面
        mock_client = MagicMock()
        mock_notion_api.return_value = mock_client
        
        # 设置模拟响应
        mock_client.pages.retrieve.return_value = {"id": self.page_id}
        
        # 创建客户端并连接页面
        client = NotionClient(api_key=self.api_key)
        page = client.connect_page(page_id=self.page_id)
        
        # 验证是否调用了正确的API
        mock_client.pages.retrieve.assert_called_once()
        
        # 验证返回对象
        self.assertIsInstance(page, NotionPage)
        self.assertEqual(page.page_id, self.page_id.replace("-", ""))
        
    @patch('notion2sql.core.client.NotionApiClient')
    def test_connect_page_with_invalid_id(self, mock_notion_api):
        """测试连接到无效页面"""
        # 创建模拟客户端
        mock_client = MagicMock()
        mock_notion_api.return_value = mock_client
        
        # 设置模拟响应（抛出异常）
        mock_client.pages.retrieve.side_effect = Exception("Page not found")
        
        # 创建客户端
        client = NotionClient(api_key=self.api_key)
        
        # 验证是否抛出异常
        with self.assertRaises(ConnectionError):
            client.connect_page(page_id=self.page_id)
            
    def test_connect_page_with_empty_id(self):
        """测试连接到空页面ID"""
        # 创建客户端
        client = NotionClient(api_key=self.api_key)
        
        # 验证是否抛出异常
        with self.assertRaises(ValueError):
            client.connect_page(page_id="")
            
    def test_initialization_with_empty_api_key(self):
        """测试使用空API密钥初始化客户端"""
        # 验证是否抛出异常
        with self.assertRaises(ValueError):
            NotionClient(api_key="")

if __name__ == '__main__':
    unittest.main() 