#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notion2SQL 高级用法示例
"""

import os
import sys
import json
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from notion2sql import NotionClient

def format_value(value):
    """格式化值，使其易读"""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)

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
        
    try:
        # 初始化Notion客户端
        client = NotionClient(api_key=notion_api_key)
        
        # 连接到页面
        print("连接到Notion页面...")
        page = client.connect_page(page_id=page_id)
        print("成功连接到页面")
        
        # 获取页面中的数据库
        print("\n获取页面中的数据库...")
        databases = page.get_databases()
        print(f"找到 {len(databases)} 个数据库")
        
        if not databases:
            print("没有找到数据库，请确保页面ID正确")
            return
            
        # 打印数据库信息
        print("\n数据库列表:")
        for i, db in enumerate(databases):
            db_info = db.get_info()
            db_title = "未命名"
            
            # 提取数据库标题
            title_array = db_info.get("title", [])
            if title_array:
                for title_part in title_array:
                    if "text" in title_part and "content" in title_part["text"]:
                        db_title = title_part["text"]["content"]
            
            print(f"{i+1}. {db_title} (ID: {db.database_id})")
            
        # 选择第一个数据库进行演示
        db = databases[0]
        
        # 获取数据库属性信息
        print("\n获取数据库结构...")
        properties = db.properties
        print("属性列表:")
        for prop_name, prop_info in properties.items():
            prop_type = prop_info["type"]
            print(f"- {prop_name} ({prop_type})")
            
        # 查询数据
        print("\n查询数据库内容...")
        results = db.query(page_size=5)
        print(f"获取了 {len(results)} 条记录")
        
        if results:
            # 打印第一条记录的所有字段
            print("\n第一条记录详情:")
            for key, value in results[0]["properties"].items():
                formatted_value = format_value(value)
                print(f"{key}: {formatted_value}")
                
            # 检查ID字段
            record_id = results[0]["id"]
            print(f"\n记录ID: {record_id}")
            
            # 检查自增ID字段
            for key, value in results[0]["properties"].items():
                prop_type = properties.get(key, {}).get("type")
                if prop_type == "unique_id" or key.lower() == "id":
                    print(f"自增ID字段 ({key}): {value}")
                    
            # 检查JSON格式的字段
            for key, value in results[0]["properties"].items():
                if isinstance(value, (list, dict)) and key not in ["LastLoginTime", "CreatedAt", "UpdatedAt"]:
                    print(f"\nJSON格式字段 ({key}): {format_value(value)}")
            
            # 添加新记录示例
            print("\n准备添加新记录...")
            # 创建样例属性
            sample_properties = {}
            
            # 查找标题字段
            title_field = None
            for key, prop in properties.items():
                if prop["type"] == "title":
                    title_field = key
                    break
                    
            if title_field:
                sample_properties[title_field] = "通过高级示例添加的记录"
                
                # 添加其他字段
                for key, prop in properties.items():
                    if key == title_field:
                        continue
                        
                    prop_type = prop["type"]
                    
                    if prop_type == "rich_text":
                        sample_properties[key] = "示例文本内容"
                    elif prop_type == "number":
                        sample_properties[key] = 42
                    elif prop_type == "select":
                        options = prop.get("select", {}).get("options", [])
                        if options:
                            sample_properties[key] = options[0]["name"]
                    elif prop_type == "multi_select":
                        options = prop.get("multi_select", {}).get("options", [])
                        if options and len(options) >= 2:
                            sample_properties[key] = [options[0]["name"], options[1]["name"]]
                    elif prop_type == "checkbox":
                        sample_properties[key] = True
                    elif prop_type == "email":
                        sample_properties[key] = "example@example.com"
                    elif prop_type == "url":
                        sample_properties[key] = "https://example.com"
                        
                print("准备添加的属性:")
                for key, value in sample_properties.items():
                    formatted_value = format_value(value)
                    print(f"- {key}: {formatted_value}")
                
                # 添加记录
                new_item = db.add_item(sample_properties)
                new_item_id = new_item["id"]
                print(f"\n添加成功! ID: {new_item_id}")
                
                # 查询新添加的记录
                print("\n查询新添加的记录...")
                filter_params = {
                    "property": title_field,
                    "title": {
                        "equals": "通过高级示例添加的记录"
                    }
                }
                
                new_results = db.query(filter=filter_params)
                if new_results:
                    print("成功查询到新记录:")
                    for key, value in new_results[0]["properties"].items():
                        formatted_value = format_value(value)
                        print(f"{key}: {formatted_value}")
                    
                    # 清理：删除测试记录
                    print("\n删除测试记录...")
                    db.delete_item(new_item_id)
                    print("删除成功!")
                else:
                    print("未能查询到新添加的记录")
            else:
                print("未找到标题字段，无法添加记录")
                
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()
        
if __name__ == "__main__":
    main() 