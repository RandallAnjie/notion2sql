from ..utils.property_converter import PropertyConverter

class NotionDatabase:
    """
    表示Notion数据库的类
    """
    
    def __init__(self, client, database_id):
        """
        初始化Notion数据库
        
        参数:
            client: Notion API客户端
            database_id (str): 数据库ID
        """
        self.client = client
        self.database_id = database_id  # 已格式化的ID
        self.database_info = self._get_database_info()
        self.properties = self._extract_properties()
        self._name = None
        self._column_count = None
        self._row_count = None
        
    @property
    def name(self):
        """
        获取数据库名称
        
        返回:
            str: 数据库名称
        """
        if self._name is None:
            title_array = self.database_info.get("title", [])
            self._name = "".join(part.get("plain_text", "") for part in title_array)
        return self._name
    
    @property
    def column_count(self):
        """
        获取数据库列数
        
        返回:
            int: 列数
        """
        if self._column_count is None:
            self._column_count = len(self.properties)
        return self._column_count
    
    @property
    def row_count(self):
        """
        获取数据库行数
        
        返回:
            int: 行数
        """
        if self._row_count is None:
            results = self.query(page_size=1)
            self._row_count = len(results)
        return self._row_count
    
    def get_columns(self):
        """
        获取数据库的所有列信息
        
        返回:
            dict: 列信息字典，格式为 {列名: 列类型}
        """
        columns = {}
        for prop_name, prop_info in self.properties.items():
            columns[prop_name] = prop_info["type"]
        return columns
    
    def get_column_names(self):
        """
        获取数据库的所有列名
        
        返回:
            list: 列名列表
        """
        return list(self.properties.keys())
    
    def get_column_types(self):
        """
        获取数据库的所有列类型
        
        返回:
            dict: 列类型字典，格式为 {列名: 列类型}
        """
        return {name: info["type"] for name, info in self.properties.items()}
    
    def get_column_info(self, column_name):
        """
        获取指定列的详细信息
        
        参数:
            column_name (str): 列名
            
        返回:
            dict: 列信息
        """
        return self.properties.get(column_name)
    
    def get_sample_data(self, limit=5):
        """
        获取数据库的样本数据
        
        参数:
            limit (int): 返回的行数限制
            
        返回:
            list: 样本数据列表
        """
        return self.query(page_size=limit)
    
    def to_sql(self):
        """
        获取SQL接口对象，用于执行SQL查询
        
        返回:
            NotionSQLInterface: SQL接口对象
        """
        from .sql_interface import NotionSQLInterface
        return NotionSQLInterface(self)
    
    def _get_database_info(self):
        """
        获取数据库信息
        
        返回:
            dict: 数据库信息
        """
        return self.client.databases.retrieve(self.database_id)
    
    def get_info(self):
        """
        获取数据库信息
        
        返回:
            dict: 数据库信息
        """
        return self.database_info
    
    def _extract_properties(self):
        """
        提取数据库属性信息
        
        返回:
            dict: 属性信息
        """
        return self.database_info.get("properties", {})
    
    def query(self, filter=None, sorts=None, page_size=100, convert_to_python=True, parse_json_strings=True):
        """
        查询数据库
        
        参数:
            filter (dict): 过滤条件
            sorts (list): 排序条件
            page_size (int): 每页大小
            convert_to_python (bool): 是否将Notion属性转换为Python类型
            parse_json_strings (bool): 是否尝试解析看起来像JSON的字符串字段
            
        返回:
            list: 查询结果
        """
        query_params = {
            "database_id": self.database_id,
            "page_size": page_size
        }
        
        if filter:
            query_params["filter"] = filter
            
        if sorts:
            query_params["sorts"] = sorts
            
        response = self.client.databases.query(**query_params)
        results = response.get("results", [])
        
        # 将属性转换为Python类型
        if convert_to_python:
            converted_results = []
            for page in results:
                page_copy = page.copy()
                properties = PropertyConverter.extract_all_plain_values(page["properties"])
                
                # 尝试解析JSON字符串
                if parse_json_strings:
                    for key, value in properties.items():
                        properties[key] = PropertyConverter.try_parse_json_string(value)
                        
                page_copy["properties"] = properties
                converted_results.append(page_copy)
            return converted_results
            
        return results
    
    def add_item(self, properties):
        """
        添加新项目到数据库
        
        参数:
            properties (dict): 项目属性
            
        返回:
            dict: 新添加的项目
        """
        # 转换属性格式以符合Notion API要求
        formatted_properties = self._format_properties_for_create(properties)
        
        # 创建页面（即添加行）
        new_page = self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=formatted_properties
        )
        
        return new_page
    
    def update_item(self, item_id, properties):
        """
        更新数据库中的项目
        
        参数:
            item_id (str): 项目ID
            properties (dict): 要更新的属性
            
        返回:
            dict: 更新后的项目
        """
        # 转换属性格式以符合Notion API要求
        formatted_properties = self._format_properties_for_update(properties)
        
        # 更新页面
        updated_page = self.client.pages.update(
            page_id=item_id,
            properties=formatted_properties
        )
        
        return updated_page
    
    def delete_item(self, item_id):
        """
        删除数据库中的项目（标记为归档）
        
        参数:
            item_id (str): 项目ID
            
        返回:
            dict: 操作结果
        """
        # Notion API实际上是将页面标记为归档，而不是真正删除
        return self.client.pages.update(
            page_id=item_id,
            archived=True
        )
    
    def _format_properties_for_create(self, properties):
        """
        将用户友好的属性格式转换为Notion API所需的格式（用于创建）
        
        参数:
            properties (dict): 用户友好的属性
            
        返回:
            dict: Notion API格式的属性
        """
        formatted = {}
        
        for key, value in properties.items():
            # 检查属性是否存在
            if key not in self.properties:
                continue
                
            prop_type = self.properties[key]["type"]
            
            if prop_type == "title" and isinstance(value, str):
                formatted[key] = {
                    "title": [{"text": {"content": value}}]
                }
            elif prop_type == "rich_text" and isinstance(value, str):
                formatted[key] = {
                    "rich_text": [{"text": {"content": value}}]
                }
            elif prop_type == "number" and (isinstance(value, int) or isinstance(value, float)):
                formatted[key] = {"number": value}
            elif prop_type == "select" and isinstance(value, str):
                formatted[key] = {"select": {"name": value}}
            elif prop_type == "multi_select" and isinstance(value, list):
                formatted[key] = {
                    "multi_select": [{"name": item} for item in value]
                }
            elif prop_type == "date" and isinstance(value, dict):
                formatted[key] = {"date": value}
            elif prop_type == "checkbox" and isinstance(value, bool):
                formatted[key] = {"checkbox": value}
            elif prop_type == "url" and isinstance(value, str):
                formatted[key] = {"url": value}
            elif prop_type == "email" and isinstance(value, str):
                formatted[key] = {"email": value}
            elif prop_type == "phone_number" and isinstance(value, str):
                formatted[key] = {"phone_number": value}
                
        return formatted
    
    def _format_properties_for_update(self, properties):
        """
        将用户友好的属性格式转换为Notion API所需的格式（用于更新）
        
        参数:
            properties (dict): 用户友好的属性
            
        返回:
            dict: Notion API格式的属性
        """
        # 更新操作的格式化与创建操作相同
        return self._format_properties_for_create(properties) 