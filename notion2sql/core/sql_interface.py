from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Float, Boolean, Text, text
from sqlalchemy.engine import Engine
from sqlalchemy.sql import select, insert, update, delete
import json

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
        
        # 创建内存数据库引擎
        self.engine = create_engine('sqlite:///:memory:')
        self.metadata = MetaData()
        
        # 创建映射表
        self.table = self._create_table()
        self.metadata.create_all(self.engine)
        
        # 填充数据
        self._sync_data()
        
    def _create_table(self):
        """
        基于Notion数据库属性创建SQLAlchemy表对象
        
        返回:
            Table: SQLAlchemy表对象
        """
        columns = [
            Column('id', String, primary_key=True)
        ]
        
        for prop_name, prop_info in self.properties.items():
            prop_type = prop_info["type"]
            
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
                row_data = {'id': item['id']}
                
                for prop_name, prop_value in item['properties'].items():
                    if isinstance(prop_value, list):
                        row_data[prop_name] = json.dumps(prop_value)
                    elif isinstance(prop_value, dict):
                        row_data[prop_name] = json.dumps(prop_value)
                    else:
                        row_data[prop_name] = prop_value
                        
                conn.execute(self.table.insert().values(**row_data))
    
    def execute_sql(self, sql_query):
        """
        执行SQL查询
        
        参数:
            sql_query (str): SQL查询字符串
            
        返回:
            list: 查询结果
        """
        with self.engine.connect() as conn:
            result = conn.execute(sql_query)
            return [dict(row) for row in result]
    
    def select(self, columns=None, where=None):
        """
        构建并执行SELECT查询
        
        参数:
            columns (list): 要选择的列
            where (str): WHERE子句
            
        返回:
            list: 查询结果
        """
        query = select([self.table])
        
        if columns:
            query = select([self.table.c[col] for col in columns])
            
        if where:
            query = query.where(text(where))
            
        with self.engine.connect() as conn:
            result = conn.execute(query)
            return [dict(row) for row in result]
    
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
                
                if prop_type == "multi_select" and isinstance(value, str):
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
                
                if prop_type == "multi_select" and isinstance(value, str):
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