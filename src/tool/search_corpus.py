import json
import pymysql
from src.MySQLConfig import MYSQL_CONFIG
from src.tool.base import BaseTool
from src.tool.rag_search import *

class CorpusTool(BaseTool):
    REMOVE_ITEMS = ["see", "see_refs", "examples_rich", "highlights"]
    REMOVE_ITEMS_EXAMPLE = ["html", "books", "quotes", "notes", 'u_texts', 'images', 'cross_refs']

    name = "tool_search_corpus"
    description = (
        "检索文献语料库，查找异文、通假例证或相关用例。"
        "参数: {'keyword': '查询关键词'}"
    )

    def run(self, keyword: str) -> str:
        conn = None
        result = ""
        dict_obj_ = []

        try:
            conn = pymysql.connect(**MYSQL_CONFIG)
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            # 执行查询语句
            query_sql = "SELECT senses FROM dyhdc_dict WHERE headword = %s;"
            cursor.execute(query_sql, (keyword,))
            fetched_data = cursor.fetchone()
            if fetched_data:
                dict_obj = json.loads(fetched_data.get("senses"))
                for item in dict_obj:
                    if item["see"]:
                        dict_obj_.append(item)
                for item in dict_obj_:
                    for e in item['examples']:
                        for re in self.REMOVE_ITEMS_EXAMPLE:
                            e.pop(re, None)
                    for e in self.REMOVE_ITEMS:
                        item.pop(e, None)
                result += json.dumps(dict_obj_, ensure_ascii=False)

        except pymysql.MySQLError as e:
            print(f"SQL ERROR: {e}")
        finally:
            if conn:
                conn.close()

        session_id = create_session("corpus_new")
        answer = converse(session_id, f"查找{keyword}的异文、通假例证或相关用例。")
        delete_session(session_id)
        result += "\n" + answer
        return result

        """mock_evidence = [
            {
                "source": "《尔雅·释诂》",
                "content": "崇，终也。",
                "note": "直接的训诂证据。"
            },
            {
                "source": "《韩诗外传》",
                "content": "崇朝，终朝也。",
                "note": "指出在'崇朝'一词中，崇即终之意，指整个早晨。"
            }
        ]"""