#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Notion2SQL SQL接口使用示例
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from notion2sql import NotionClient, NotionSQLInterface

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
        page = client.connect_page(page_id=page_id)
        print("成功连接到Notion页面")
        
        # 获取数据库
        databases = page.get_databases()
        if not databases:
            print("没有找到数据库。请确保页面ID正确，并且页面中包含数据库。")
            return
            
        # 使用第一个数据库进行演示
        db = databases[0]
        
        # 创建SQL接口
        sql = NotionSQLInterface(db)
        print("成功创建SQL接口")
        
        # 执行SQL查询
        print("\n执行SQL查询...")
        results = sql.execute_sql("SELECT * FROM notion_data LIMIT 5")
        
        # 显示结果
        print(f"查询结果 ({len(results)} 行):")
        for i, row in enumerate(results):
            print(f"\n行 {i+1}:")
            for col, val in row.items():
                print(f"  {col}: {val}")
                
        # 使用SQL接口插入数据
        if results:
            print("\n使用SQL接口插入数据...")
            
            # 从第一行推断表结构
            sample_data = {}
            first_row = results[0]
            
            for key, value in first_row.items():
                if key == 'id':
                    continue
                    
                if isinstance(value, str) and db.properties.get(key, {}).get("type") == "title":
                    sample_data[key] = "通过SQL接口插入的记录"
                elif isinstance(value, bool):
                    sample_data[key] = not value  # 取反值
                elif isinstance(value, (int, float)):
                    sample_data[key] = value + 10
                elif value is None:
                    pass  # 跳过空值
                else:
                    sample_data[key] = value
            
            # 确保至少有一个标题字段
            has_title = False
            for key, prop in db.properties.items():
                if prop["type"] == "title":
                    has_title = True
                    if key not in sample_data:
                        sample_data[key] = "通过SQL接口插入的记录"
                    break
                    
            if has_title and sample_data:
                # 插入数据
                new_item = sql.insert(sample_data)
                print(f"成功插入记录，ID: {new_item['id']}")
                
                # 刷新数据
                sql.refresh()
                
                # 再次查询以验证
                print("\n验证插入的数据...")
                verify_results = sql.execute_sql(f"SELECT * FROM notion_data WHERE id = '{new_item['id']}'")
                
                if verify_results:
                    print("成功找到插入的记录:")
                    for col, val in verify_results[0].items():
                        print(f"  {col}: {val}")
                        
                    # 测试更新
                    print("\n更新记录...")
                    update_data = {}
                    
                    # 查找一个可以更新的字段
                    for key, prop in db.properties.items():
                        if prop["type"] == "checkbox":
                            update_data[key] = not verify_results[0].get(key, False)
                            break
                            
                    if update_data:
                        sql.update(new_item['id'], update_data)
                        print("记录已更新")
                        
                        # 最后删除测试记录
                        print("\n删除记录...")
                        sql.delete(new_item['id'])
                        print("记录已删除")
                            
    except Exception as e:
        print(f"错误: {str(e)}")
        
if __name__ == "__main__":
    main() 