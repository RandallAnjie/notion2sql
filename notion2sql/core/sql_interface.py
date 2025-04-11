from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Float, Boolean, Text, text
from sqlalchemy.engine import Engine
from sqlalchemy.sql import select, insert, update, delete
import json
import requests
from datetime import datetime

from .database import NotionDatabase

class NotionSQLInterface:
    """
    Notion数据库的SQL接口，允许使用SQL语法来操作Notion数据库
    """
    
    def __init__(self, notion_database):
        """
        初始化SQL接口
        
        参数:
            notion_database (NotionDatabase): Notion数据库对象
        """
        if not isinstance(notion_database, NotionDatabase):
            raise TypeError("notion_database必须是NotionDatabase类型")
            
        self.notion_db = notion_database
        self.properties = notion_database.properties
        self.client = notion_database.client
        
        # 创建内存数据库引擎
        self.engine = create_engine('sqlite:///:memory:')
        self.metadata = MetaData()
        
        # 创建映射表
        self.table = self._create_table()
        self.metadata.create_all(self.engine)
        
        # 填充数据
        self._sync_data()
    
    def get_files(self, item_id, property_name):
        """
        获取指定项目的文件列表
        
        参数:
            item_id (str): 项目ID
            property_name (str): 属性名称
            
        返回:
            list: 文件列表，每个文件包含name和url
        """
        if self.properties.get(property_name, {}).get("type") != "files":
            raise ValueError(f"属性 {property_name} 不是文件类型")
            
        # 获取项目信息
        page = self.client.pages.retrieve(item_id)
        files = page["properties"][property_name].get("files", [])
        
        return [{"name": f["name"], "url": f["file"]["url"]} for f in files]
    
    def download_file(self, file_url, save_path):
        """
        下载文件
        
        参数:
            file_url (str): 文件URL
            save_path (str): 保存路径
            
        返回:
            str: 保存的文件路径
        """
        response = requests.get(file_url, stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return save_path
    
    def upload_file(self, item_id, property_name, file_path):
        """
        上传文件到指定项目
        
        参数:
            item_id (str): 项目ID
            property_name (str): 属性名称
            file_path (str): 文件路径
            
        返回:
            dict: 上传结果
        """
        if self.properties.get(property_name, {}).get("type") != "files":
            raise ValueError(f"属性 {property_name} 不是文件类型")
            
        # 上传文件
        with open(file_path, 'rb') as f:
            file_data = f.read()
            
        # 更新项目属性
        return self.client.pages.update(
            page_id=item_id,
            properties={
                property_name: {
                    "files": [{"name": file_path.split('/')[-1], "file": {"url": "file://" + file_path}}]
                }
            }
        )
    
    def get_people(self, item_id, property_name):
        """
        获取指定项目的人员列表
        
        参数:
            item_id (str): 项目ID
            property_name (str): 属性名称
            
        返回:
            list: 人员列表，每个人员包含id和name
        """
        if self.properties.get(property_name, {}).get("type") != "people":
            raise ValueError(f"属性 {property_name} 不是人员类型")
            
        # 获取项目信息
        page = self.client.pages.retrieve(item_id)
        people = page["properties"][property_name].get("people", [])
        
        return [{"id": p["id"], "name": p["name"]} for p in people]
    
    def add_person(self, item_id, property_name, person_id):
        """
        添加人员到指定项目
        
        参数:
            item_id (str): 项目ID
            property_name (str): 属性名称
            person_id (str): 人员ID
            
        返回:
            dict: 更新结果
        """
        if self.properties.get(property_name, {}).get("type") != "people":
            raise ValueError(f"属性 {property_name} 不是人员类型")
            
        # 获取当前人员列表
        current_people = self.get_people(item_id, property_name)
        current_people_ids = [p["id"] for p in current_people]
        
        # 如果人员已存在，直接返回
        if person_id in current_people_ids:
            return {"status": "already_exists"}
            
        # 添加新人员
        current_people.append({"id": person_id})
        
        # 更新项目属性
        return self.client.pages.update(
            page_id=item_id,
            properties={
                property_name: {
                    "people": current_people
                }
            }
        )
    
    def remove_person(self, item_id, property_name, person_id):
        """
        从指定项目移除人员
        
        参数:
            item_id (str): 项目ID
            property_name (str): 属性名称
            person_id (str): 人员ID
            
        返回:
            dict: 更新结果
        """
        if self.properties.get(property_name, {}).get("type") != "people":
            raise ValueError(f"属性 {property_name} 不是人员类型")
            
        # 获取当前人员列表
        current_people = self.get_people(item_id, property_name)
        
        # 过滤掉要移除的人员
        updated_people = [p for p in current_people if p["id"] != person_id]
        
        # 更新项目属性
        return self.client.pages.update(
            page_id=item_id,
            properties={
                property_name: {
                    "people": updated_people
                }
            }
        )
    
    def _create_table(self):
        """
        基于Notion数据库属性创建SQLAlchemy表对象
        
        返回:
            Table: SQLAlchemy表对象
        """
        columns = [
            Column('id', String, primary_key=True)  # 始终保留id字段
        ]
        
        for prop_name, prop_info in self.properties.items():
            prop_type = prop_info["type"]
            
            # 跳过特殊类型的列
            if prop_type in ["button", "people", "last_edited_time", "created_time"]:
                continue
                
            # 处理列名冲突
            if prop_name.lower() == 'id':
                prop_name = 'notion_id'  # 重命名以避免冲突
                
            if prop_type == "title" or prop_type == "rich_text":
                columns.append(Column(prop_name, Text))
            elif prop_type == "number":
                columns.append(Column(prop_name, Float))
            elif prop_type == "select":
                columns.append(Column(prop_name, String))
            elif prop_type == "multi_select":
                columns.append(Column(prop_name, String))  # 将作为JSON字符串存储
            elif prop_type == "date":
                columns.append(Column(prop_name, String))  # 将作为JSON字符串存储
            elif prop_type == "checkbox":
                columns.append(Column(prop_name, Boolean))
            elif prop_type == "url" or prop_type == "email" or prop_type == "phone_number":
                columns.append(Column(prop_name, String))
            elif prop_type == "relation":
                columns.append(Column(prop_name, String))  # 将作为JSON字符串存储
            elif prop_type == "files":
                columns.append(Column(prop_name, String))  # 将作为JSON字符串存储
            elif prop_type == "unique_id":
                columns.append(Column(prop_name, String))  # 将作为JSON字符串存储
        
        return Table('notion_data', self.metadata, *columns)
    
    def _sync_data(self):
        """
        同步Notion数据库数据到SQL表
        """
        # 获取所有数据
        results = self.notion_db.query(convert_to_python=True)
        
        # 清空表
        with self.engine.connect() as conn:
            conn.execute(self.table.delete())
            
            # 插入数据
            for item in results:
                row_data = {'id': item['id']}  # 始终保留id字段
                
                for prop_name, prop_value in item['properties'].items():
                    prop_type = self.properties[prop_name]["type"]
                    
                    # 跳过特殊类型的列
                    if prop_type in ["button", "people", "last_edited_time", "created_time"]:
                        continue
                        
                    # 处理列名冲突
                    if prop_name.lower() == 'id':
                        prop_name = 'notion_id'
                        
                    if prop_type == "relation":
                        # 将关系类型转换为JSON格式
                        relation_info = {
                            "type": "relation",
                            "database_id": self.properties[prop_name].get("relation", {}).get("database_id"),
                            "values": prop_value
                        }
                        row_data[prop_name] = json.dumps(relation_info)
                    elif prop_type == "files":
                        # 将文件类型转换为JSON格式
                        files_info = {
                            "type": "files",
                            "files": prop_value
                        }
                        row_data[prop_name] = json.dumps(files_info)
                    elif prop_type == "unique_id":
                        # 将unique_id类型转换为JSON格式
                        unique_id_info = {
                            "type": "unique_id",
                            "value": prop_value
                        }
                        row_data[prop_name] = json.dumps(unique_id_info)
                    elif isinstance(prop_value, list):
                        row_data[prop_name] = json.dumps(prop_value)
                    elif isinstance(prop_value, dict):
                        row_data[prop_name] = json.dumps(prop_value)
                    else:
                        row_data[prop_name] = prop_value
                
                # 打印调试信息
                print(f"正在插入数据: {row_data}")
                conn.execute(self.table.insert().values(**row_data))
            
            # 提交事务
            conn.commit()
    
    def execute_sql(self, sql_query):
        """
        执行SQL查询
        
        参数:
            sql_query (str): SQL查询字符串
            
        返回:
            list: 查询结果
        """
        with self.engine.connect() as conn:
            result = conn.execute(text(sql_query))
            # 使用 _asdict() 方法来正确转换结果行为字典
            return [row._asdict() for row in result]
    
    def select(self, columns=None, where=None):
        """
        构建并执行SELECT查询
        
        参数:
            columns (list): 要选择的列
            where (str): WHERE子句
            
        返回:
            list: 查询结果
        """
        # 过滤掉特殊类型的列
        if columns:
            columns = [col for col in columns if self.properties.get(col, {}).get("type") not in 
                      ["button", "people", "last_edited_time", "created_time"]]
            
            # 处理列名冲突
            columns = ['notion_id' if col.lower() == 'id' else col for col in columns]
        
        # 构建查询
        if columns:
            # 如果指定了列，只选择这些列
            selected_columns = [self.table.c[col] for col in columns]
            query = select(*selected_columns)
        else:
            # 如果没有指定列，选择所有列
            query = select(self.table)
            
        if where:
            query = query.where(text(where))
            
        with self.engine.connect() as conn:
            result = conn.execute(query)
            # 使用 _asdict() 方法来正确转换结果行为字典
            return [row._asdict() for row in result]
    
    def insert(self, values):
        """
        插入新记录
        
        参数:
            values (dict): 列值对
            
        返回:
            dict: 插入后的记录
        """
        # 转换数据
        notion_properties = {}
        
        for key, value in values.items():
            if key == 'id':
                continue
                
            if key in self.properties:
                prop_type = self.properties[key]["type"]
                
                # 跳过特殊类型的列
                if prop_type in ["button", "people", "last_edited_time", "created_time"]:
                    continue
                    
                if prop_type == "relation":
                    # 处理关系类型
                    try:
                        relation_data = json.loads(value)
                        if isinstance(relation_data, dict) and "values" in relation_data:
                            notion_properties[key] = relation_data["values"]
                    except:
                        notion_properties[key] = value
                elif prop_type == "multi_select" and isinstance(value, str):
                    # 尝试从JSON字符串解析
                    try:
                        notion_properties[key] = json.loads(value)
                    except:
                        notion_properties[key] = value
                else:
                    notion_properties[key] = value
        
        # 调用Notion API添加项目
        return self.notion_db.add_item(notion_properties)
    
    def update(self, item_id, values):
        """
        更新记录
        
        参数:
            item_id (str): 记录ID
            values (dict): 列值对
            
        返回:
            dict: 更新后的记录
        """
        # 转换数据
        notion_properties = {}
        
        for key, value in values.items():
            if key == 'id':
                continue
                
            if key in self.properties:
                prop_type = self.properties[key]["type"]
                
                # 跳过特殊类型的列
                if prop_type in ["button", "people", "last_edited_time", "created_time"]:
                    continue
                    
                if prop_type == "relation":
                    # 处理关系类型
                    try:
                        relation_data = json.loads(value)
                        if isinstance(relation_data, dict) and "values" in relation_data:
                            notion_properties[key] = relation_data["values"]
                    except:
                        notion_properties[key] = value
                elif prop_type == "multi_select" and isinstance(value, str):
                    # 尝试从JSON字符串解析
                    try:
                        notion_properties[key] = json.loads(value)
                    except:
                        notion_properties[key] = value
                else:
                    notion_properties[key] = value
        
        # 调用Notion API更新项目
        return self.notion_db.update_item(item_id, notion_properties)
    
    def delete(self, item_id):
        """
        删除记录
        
        参数:
            item_id (str): 记录ID
            
        返回:
            dict: 操作结果
        """
        return self.notion_db.delete_item(item_id)
    
    def refresh(self):
        """
        刷新SQL表数据
        """
        self._sync_data() 