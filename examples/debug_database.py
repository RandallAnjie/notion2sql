#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notion2SQL 调试脚本 - 用于检查数据库获取问题
"""

import os
import sys
import json
from dotenv import load_dotenv
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from notion2sql import NotionClient

def main():
    # 加载环境变量
    load_dotenv()
    
    # 获取Notion API密钥
    notion_api_key = os.getenv("NOTION_API_KEY")
    if not notion_api_key:
        logging.error("错误: 请在.env文件中设置NOTION_API_KEY")
        return
        
    # 获取页面ID
    page_id = os.getenv("NOTION_PAGE_ID")
    if not page_id:
        logging.error("错误: 请在.env文件中设置NOTION_PAGE_ID")
        return
        
    logging.info(f"使用页面ID: {page_id}")
    
    try:
        # 初始化Notion客户端
        client = NotionClient(api_key=notion_api_key)
        
        # 连接到页面
        logging.info("连接到Notion页面...")
        page = client.connect_page(page_id=page_id)
        logging.info(f"成功连接到页面: {page_id}")
        
        # 获取页面信息
        page_info = page.page_info
        logging.info(f"页面标题: {page_info.get('properties', {}).get('title', {}).get('title', [])}")
        
        # 列出页面块
        logging.info("获取页面块内容...")
        try:
            blocks = client.client.blocks.children.list(block_id=page.page_id)
            block_results = blocks.get("results", [])
            logging.info(f"找到 {len(block_results)} 个块")
            
            for i, block in enumerate(block_results):
                block_type = block.get("type", "未知")
                block_id = block.get("id", "未知")
                logging.info(f"块 {i+1}: 类型={block_type}, ID={block_id}")
                
                # 对于数据库类型，获取更多信息
                if block_type == "child_database":
                    try:
                        db_info = client.client.databases.retrieve(database_id=block_id)
                        db_title = "未命名"
                        
                        title_array = db_info.get("title", [])
                        if title_array:
                            for title_part in title_array:
                                if "text" in title_part and "content" in title_part["text"]:
                                    db_title = title_part["text"]["content"]
                                    break
                                    
                        logging.info(f"  数据库标题: {db_title}")
                        logging.info(f"  属性数量: {len(db_info.get('properties', {}))}")
                    except Exception as db_error:
                        logging.error(f"  获取数据库详情失败: {str(db_error)}")
        except Exception as e:
            logging.error(f"获取页面块失败: {str(e)}")
        
        # 使用修改后的方法获取数据库
        logging.info("\n使用修改后的方法获取数据库...")
        databases = page.get_databases()
        logging.info(f"找到 {len(databases)} 个数据库")
        
        for i, db in enumerate(databases):
            try:
                db_info = db.get_info()
                db_title = "未命名"
                
                title_array = db_info.get("title", [])
                if title_array:
                    for title_part in title_array:
                        if "text" in title_part and "content" in title_part["text"]:
                            db_title = title_part["text"]["content"]
                            break
                            
                logging.info(f"数据库 {i+1}: 标题={db_title}, ID={db.database_id}")
                logging.info(f"属性数量: {len(db_info.get('properties', {}))}")
                
                # 查询一条记录
                logging.info("查询数据库内容...")
                results = db.query(page_size=1)
                logging.info(f"获取了 {len(results)} 条记录")
            except Exception as db_error:
                logging.error(f"处理数据库 {i+1} 时出错: {str(db_error)}")
        
    except Exception as e:
        logging.error(f"错误: {str(e)}")
        
if __name__ == "__main__":
    main() 