import json
from typing import List
import pymysql
from src.MySQLConfig import MYSQL_CONFIG
from src.tool.base import BaseTool

class DictionaryTool(BaseTool):
    REMOVE_ITEMS = ["see", "see_refs", "examples_rich", "highlights"]
    REMOVE_ITEMS_EXAMPLE = ["html", "books", "quotes", "notes", 'u_texts', 'images', 'cross_refs']

    name = "tool_search_dictionary"
    description = (
        "查询字词的本义、引申义。支持批量查询。"
        "参数: {'words': ['查询词1', '查询词2']}"
    )

    def run(self, words: List[str]) -> str:
        conn = None
        result = {}
        try:
            conn = pymysql.connect(**MYSQL_CONFIG)
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            for word in words:
                # 执行查询语句
                query_sql = "SELECT senses FROM dyhdc_dict WHERE headword = %s;"
                cursor.execute(query_sql, (word,))
                fetched_data = cursor.fetchone()["senses"]
                dict_obj = json.loads(fetched_data)
                for item in dict_obj:
                    for e in item['examples']:
                        for re in self.REMOVE_ITEMS_EXAMPLE:
                            e.pop(re, None)
                    for e in self.REMOVE_ITEMS:
                        item.pop(e, None)
                result[word] = fetched_data

        except pymysql.MySQLError as e:
            print(f"SQL ERROR: {e}")
        finally:
            if conn:
                conn.close()

        return json.dumps(result, ensure_ascii=False)
        # 模拟数据：针对 "崇" 和 "终"
        data = {
            "崇": {
                "definitions": [
                    "高大 (lofty/high)",
                    "尊崇 (worship/honor)",
                    "充满 (full)"
                ],
                "explanation": "本义为山大而高。"
            },
            "终": {
                "definitions": [
                    "了结，结束 (end/finish)",
                    "死 (death)",
                    "极点 (limit)"
                ],
                "explanation": "本义为丝线绕完了。"
            }
        }

        results = {}
        for word in words:
            results[word] = mock_data.get(word, "未收录该字")

        return json.dumps(results, ensure_ascii=False)