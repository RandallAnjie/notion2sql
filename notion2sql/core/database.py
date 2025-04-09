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