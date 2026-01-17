import json
import pymysql
from src.MySQLConfig import MYSQL_CONFIG
from src.tool.base import BaseTool

class PhonologyTool(BaseTool):
    name = "tool_check_phonology"
    description = (
        "查询两个字的上古音韵关系（声母、韵部），判断是否音近。"
        "参数: {'char_a': '字A', 'char_b': '字B'}"
    )

    def run(self, char_a: str, char_b: str) -> str:
        conn = None
        result = {}
        try:
            conn = pymysql.connect(**MYSQL_CONFIG)
            cursor = conn.cursor(pymysql.cursors.DictCursor)

            # 执行查询语句
            query_sql = "SELECT * FROM mdx_dict WHERE headword = %s;"
            cursor.execute(query_sql, (char_a,))
            fetched_data1 = json.dumps(cursor.fetchone(), ensure_ascii=False)
            cursor.execute(query_sql, (char_b,))
            fetched_data2 = json.dumps(cursor.fetchone(), ensure_ascii=False)
            print(fetched_data1)
            print(fetched_data2)

            result = {
                "char_a": fetched_data1,
                "char_b": fetched_data2,
            }
        except pymysql.MySQLError as e:
            print(f"SQL ERROR: {e}")
        finally:
            if conn:
                conn.close()

        return json.dumps(result, ensure_ascii=False)