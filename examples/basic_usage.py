#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notion2SQL 基本用法示例
"""

import os
import sys
from dotenv import load_dotenv
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from notion2sql import NotionClient

def main():
    # 加载环境变量
    load_dotenv()
    
    # 获取Notion API密钥
    notion_api_key = os.getenv("NOTION_API_KEY")
    if not notion_api_key:
        print("错误: 请在.env文件中设置NOTION_API_KEY")
        return
        
    # 获取页面ID
    page_id = os.getenv("NOTION_PAGE_ID")
    if not page_id:
        print("错误: 请在.env文件中设置NOTION_PAGE_ID")
        return
        
    print("连接到Notion...")
    
    try:
        # 初始化Notion客户端
        client = NotionClient(api_key=notion_api_key)
        
        # 连接到页面
        page = client.connect_page(page_id=page_id)
        print("成功连接到页面！")
        
        # 获取页面上的所有数据库
        print("\n获取页面中的数据库...")
        databases = page.get_databases()
        print(f"找到 {len(databases)} 个数据库")
        
        if not databases:
            print("没有找到数据库。请确保页面ID正确，并且页面中包含数据库。")
            return
            
        # 使用第一个数据库进行演示
        db = databases[0]
        db_info = db.get_info()
        db_title = "未命名数据库"
        
        if "title" in db_info and db_info["title"]:
            for title_part in db_info["title"]:
                if "text" in title_part and "content" in title_part["text"]:
                    db_title = title_part["text"]["content"]
                    break
                    
        print(f"\n使用数据库: {db_title}")
        
        # 查询数据库
        print("\n查询数据库内容...")
        results = db.query(page_size=5)
        print(f"获取了 {len(results)} 条记录")
        
        # 打印每条记录的简要信息
        for i, item in enumerate(results):
            print(f"\n记录 {i+1}:")
            print(json.dumps(item["properties"], indent=2, ensure_ascii=False))
            
        # 如果有记录，尝试添加、更新和删除操作
        if results:
            print("\n添加一条新记录...")
            # 获取数据库模式
            properties = db.properties
            sample_properties = {}
            
            # 为每种属性类型创建样例数据
            for prop_name, prop_info in properties.items():
                prop_type = prop_info["type"]
                
                if prop_type == "title":
                    sample_properties[prop_name] = "示例标题"
                elif prop_type == "rich_text":
                    sample_properties[prop_name] = "示例文本内容"
                elif prop_type == "number":
                    sample_properties[prop_name] = 42
                elif prop_type == "select":
                    options = prop_info.get("select", {}).get("options", [])
                    if options:
                        sample_properties[prop_name] = options[0]["name"]
                elif prop_type == "multi_select":
                    options = prop_info.get("multi_select", {}).get("options", [])
                    if options and len(options) >= 2:
                        sample_properties[prop_name] = [options[0]["name"], options[1]["name"]]
                elif prop_type == "checkbox":
                    sample_properties[prop_name] = True
                    
            # 添加记录
            if "title" in sample_properties:
                new_item = db.add_item(sample_properties)
                new_item_id = new_item["id"]
                print(f"添加成功! ID: {new_item_id}")
                
                # 更新记录
                print("\n更新记录...")
                update_properties = {}
                for prop_name, prop_info in properties.items():
                    if prop_info["type"] == "checkbox":
                        update_properties[prop_name] = False
                        
                if update_properties:
                    updated_item = db.update_item(new_item_id, update_properties)
                    print("更新成功!")
                    
                # 删除记录
                print("\n删除记录...")
                db.delete_item(new_item_id)
                print("删除成功!")
            
    except Exception as e:
        print(f"错误: {str(e)}")
        
if __name__ == "__main__":
    main() 