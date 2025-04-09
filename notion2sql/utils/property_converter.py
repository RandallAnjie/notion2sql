class PropertyConverter:
    """
    用于Notion属性与Python类型之间转换的工具类
    """
    
    @staticmethod
    def extract_plain_value(property_value):
        """
        从Notion API返回的属性值中提取常规Python值
        
        参数:
            property_value (dict): Notion API返回的属性值
            
        返回:
            混合类型: 提取的Python值
        """
        if not property_value or "type" not in property_value:
            return None
            
        prop_type = property_value["type"]
        
        if prop_type == "title":
            title_array = property_value.get("title", [])
            if not title_array:
                return ""
            return "".join(item.get("plain_text", "") for item in title_array)
            
        elif prop_type == "rich_text":
            text_array = property_value.get("rich_text", [])
            if not text_array:
                return ""
            return "".join(item.get("plain_text", "") for item in text_array)
            
        elif prop_type == "number":
            return property_value.get("number")
            
        elif prop_type == "select":
            select_obj = property_value.get("select")
            return select_obj.get("name") if select_obj else None
            
        elif prop_type == "multi_select":
            multi_select = property_value.get("multi_select", [])
            return [item.get("name") for item in multi_select]
            
        elif prop_type == "date":
            date_obj = property_value.get("date")
            if not date_obj:
                return None
                
            result = {"start": date_obj.get("start")}
            if "end" in date_obj:
                result["end"] = date_obj["end"]
            return result
            
        elif prop_type == "checkbox":
            return property_value.get("checkbox")
            
        elif prop_type == "url":
            return property_value.get("url")
            
        elif prop_type == "email":
            return property_value.get("email")
            
        elif prop_type == "phone_number":
            return property_value.get("phone_number")
            
        elif prop_type == "formula":
            formula = property_value.get("formula", {})
            formula_type = formula.get("type")
            return formula.get(formula_type)
            
        elif prop_type == "relation":
            relations = property_value.get("relation", [])
            return [rel.get("id") for rel in relations]
            
        elif prop_type == "rollup":
            return property_value.get("rollup", {}).get("array", [])
            
        elif prop_type == "created_time":
            return property_value.get("created_time")
            
        elif prop_type == "created_by":
            return property_value.get("created_by")
            
        elif prop_type == "last_edited_time":
            return property_value.get("last_edited_time")
            
        elif prop_type == "last_edited_by":
            return property_value.get("last_edited_by")
            
        elif prop_type == "unique_id":
            # 处理自增ID字段
            unique_id = property_value.get("unique_id", {})
            return unique_id.get("number") if unique_id else None
            
        elif prop_type == "status":
            status = property_value.get("status")
            return status.get("name") if status else None
            
        elif prop_type == "files":
            files = property_value.get("files", [])
            file_info = []
            for file in files:
                if file.get("type") == "external":
                    file_info.append(file.get("external", {}).get("url", ""))
                elif file.get("type") == "file":
                    file_info.append(file.get("file", {}).get("url", ""))
            return file_info
            
        elif prop_type == "people":
            people = property_value.get("people", [])
            return [person.get("id") for person in people]
            
        return None
    
    @staticmethod
    def extract_all_plain_values(page_properties):
        """
        从Notion页面属性中提取所有常规Python值
        
        参数:
            page_properties (dict): Notion页面属性
            
        返回:
            dict: 提取的Python值字典
        """
        result = {}
        
        for key, value in page_properties.items():
            result[key] = PropertyConverter.extract_plain_value(value)
            
        return result
    
    @staticmethod
    def try_parse_json_string(value):
        """
        尝试将字符串解析为JSON（用于特殊的字符串字段）
        
        参数:
            value: 要解析的值
            
        返回:
            解析后的值，如果解析失败则返回原值
        """
        import json
        
        if not isinstance(value, str):
            return value
            
        try:
            if value.startswith("[") and value.endswith("]"):
                return json.loads(value)
            elif value.startswith("{") and value.endswith("}"):
                return json.loads(value)
        except Exception:
            pass
            
        return value 