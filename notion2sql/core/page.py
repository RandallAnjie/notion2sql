from .database import NotionDatabase

class NotionPage:
    """
    表示Notion页面的类
    """
    
    def __init__(self, client, page_id):
        """
        初始化Notion页面
        
        参数:
            client: Notion API客户端
            page_id (str): 页面ID
        """
        self.client = client
        self.page_id = page_id
        self.page_info = self._get_page_info()
        
    def _get_page_info(self):
        """
        获取页面信息
        
        返回:
            dict: 页面信息
        """
        return self.client.pages.retrieve(self.page_id)
    
    def get_databases(self):
        """
        获取页面中的所有数据库
        
        返回:
            list: 数据库对象列表
        """
        # 使用两种方法获取数据库
        page_databases = []
        
        # 方法1: 获取页面中的块，查找数据库类型的块
        try:
            blocks = self.client.blocks.children.list(block_id=self.page_id)
            for block in blocks.get("results", []):
                if block.get("type") == "child_database":
                    page_databases.append(NotionDatabase(self.client, block["id"]))
        except Exception as e:
            print(f"通过块获取数据库失败: {str(e)}")
        
        # 方法2: 使用搜索API查找属于当前页面的数据库
        if not page_databases:
            try:
                results = self.client.search(
                    query="",
                    filter={
                        "property": "object",
                        "value": "database"
                    },
                    page_size=100
                ).get("results", [])
                
                for db in results:
                    parent = db.get("parent", {})
                    if parent.get("type") == "page_id" and parent.get("page_id") == self.page_id:
                        page_databases.append(NotionDatabase(self.client, db["id"]))
            except Exception as e:
                print(f"通过搜索获取数据库失败: {str(e)}")
        
        return page_databases
    
    def get_database_by_name(self, name):
        """
        根据名称获取数据库
        
        参数:
            name (str): 数据库名称
            
        返回:
            NotionDatabase: 数据库对象，如果未找到则返回None
        """
        databases = self.get_databases()
        
        for db in databases:
            db_info = db.get_info()
            db_title = ""
            
            # 提取数据库标题
            title_array = db_info.get("title", [])
            if title_array:
                for title_part in title_array:
                    if "text" in title_part and "content" in title_part["text"]:
                        db_title += title_part["text"]["content"]
            
            if db_title == name:
                return db
                
        return None 