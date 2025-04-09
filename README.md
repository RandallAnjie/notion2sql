# Notion2SQL

一个将Notion数据库转换为SQL接口的工具，让您可以像操作传统数据库一样操作Notion页面中的数据库。

## 特性

- 将Notion数据库映射为SQL表
- 支持对Notion数据库进行CRUD操作
- 简单易用的API接口
- 支持所有Notion属性类型，包括：
  - 文本、数字、选择器、多选、日期等基本类型
  - 自增ID（unique_id类型）
  - JSON格式数据自动解析
  - 文件、人员和关系类型

## 安装

```bash
pip install notion2sql
```

## 使用方法

### 基本用法

```python
from notion2sql import NotionClient
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 初始化客户端
client = NotionClient(api_key=os.getenv("NOTION_API_KEY"))

# 连接到Notion页面
page = client.connect_page(page_id="YOUR_PAGE_ID")

# 获取页面中的所有数据库
databases = page.get_databases()

# 选择一个数据库进行操作
db = databases[0]

# 查询数据
results = db.query(filter={"property": "Name", "equals": "测试项目"})

# 添加新记录
new_item = db.add_item({
    "Name": "新项目",
    "Status": "进行中",
    "Tags": ["重要", "紧急"]
})

# 更新记录
db.update_item(item_id=new_item["id"], properties={
    "Status": "已完成"
})

# 删除记录
db.delete_item(item_id=new_item["id"])
```

### 高级功能

#### 自增ID处理

Notion支持自增ID字段（unique_id类型），Notion2SQL会自动识别并正确处理这种类型：

```python
# 查询数据，自动处理unique_id类型
results = db.query(page_size=5)

# 检查自增ID值
for item in results:
    unique_id = item["properties"]["ID"]  # 假设你的自增ID字段名为"ID"
    print(f"自增ID: {unique_id}")
```

#### JSON字符串自动解析

某些Notion字段可能存储JSON格式的数据，Notion2SQL可以自动解析这些字段：

```python
# 启用JSON解析的查询
results = db.query(parse_json_strings=True)

# 访问已解析的JSON数据
for item in results:
    json_data = item["properties"]["Config"]  # 假设"Config"字段存储了JSON数据
    # json_data 现在是Python对象，而不是字符串
```

#### SQL接口

使用SQL接口操作Notion数据库：

```python
from notion2sql import NotionClient, NotionSQLInterface

# 初始化客户端并连接到页面
client = NotionClient(api_key=os.getenv("NOTION_API_KEY"))
page = client.connect_page(page_id="YOUR_PAGE_ID")
db = page.get_databases()[0]

# 创建SQL接口
sql = NotionSQLInterface(db)

# 执行SQL查询
results = sql.execute_sql("SELECT * FROM notion_data WHERE Name LIKE '%项目%'")

# 插入数据
sql.insert({"Name": "SQL插入的项目", "Status": "计划中"})

# 更新数据
sql.update(item_id="item_id_here", values={"Status": "已完成"})

# 删除数据
sql.delete(item_id="item_id_here")

# 刷新数据（从Notion同步到SQL表）
sql.refresh()
```

## 环境变量

在项目根目录创建`.env`文件，并添加以下内容：

```
NOTION_API_KEY=your_notion_integration_token
NOTION_PAGE_ID=your_page_id_here
```

## Notion API 访问设置

1. 创建Notion集成：访问 https://www.notion.so/my-integrations
2. 获取API密钥
3. 在Notion页面中，点击右上角"共享"按钮，将您的集成添加到页面中并授予"可以编辑"权限

## 授权

该项目基于MIT许可证开源。
