from notion_client import Client as NotionApiClient
from .page import NotionPage

class NotionClient:
    """
    Notion客户端类，用于与Notion API进行交互
    """
    
    def __init__(self, api_key):
        """
        初始化Notion客户端
        
        参数:
            api_key (str): Notion API密钥
        """
        if not api_key:
            raise ValueError("必须提供Notion API密钥")
            
        self.api_key = api_key
        self.client = NotionApiClient(auth=api_key)
    
    def _format_page_id(self, page_id):
        """
        格式化页面ID，确保使用正确的格式
        
        参数:
            page_id (str): 页面ID
            
        返回:
            str: 格式化后的页面ID
        """
        # 移除所有连字符
        clean_id = page_id.replace('-', '')
        
        # 如果ID长度符合标准，重新添加连字符
        if len(clean_id) == 32:
            formatted_id = f"{clean_id[:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:]}"
            return formatted_id
        return clean_id
        
    def connect_page(self, page_id):
        """
        连接到指定的Notion页面
        
        参数:
            page_id (str): Notion页面ID
            
        返回:
            NotionPage: 表示连接的Notion页面的对象
        """
        # 验证页面ID
        if not page_id:
            raise ValueError("必须提供页面ID")
            
        # 格式化页面ID
        formatted_page_id = self._format_page_id(page_id)
        
        try:
            # 验证页面是否存在
            self.client.pages.retrieve(formatted_page_id)
            return NotionPage(self.client, formatted_page_id)
        except Exception as e:
            raise ConnectionError(f"无法连接到页面: {str(e)}")
    
    def get_database(self, database_id):
        """
        直接获取数据库对象
        
        参数:
            database_id (str): 数据库ID
            
        返回:
            NotionDatabase: 数据库对象
        """
        from .database import NotionDatabase
        
        if not database_id:
            raise ValueError("必须提供数据库ID")
            
        # 格式化数据库ID
        formatted_database_id = self._format_page_id(database_id)
        
        try:
            # 验证数据库是否存在
            self.client.databases.retrieve(formatted_database_id)
            return NotionDatabase(self.client, formatted_database_id)
        except Exception as e:
            raise ConnectionError(f"无法连接到数据库: {str(e)}") 