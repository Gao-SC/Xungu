"""import json
import pymysql

# -------------------------- 配置项（与之前保持一致） --------------------------
MYSQL_CONFIG = {
	"host": "127.0.0.1",
	"port": 3306,
	"user": "root",
	"password": "your_root_password",
	"database": "test",
	"charset": "utf8mb4"
}

REMOVE_ITEMS = ["see", "see_refs", "examples_rich", "highlights"]
REMOVE_ITEMS_EXAMPLE = ["html", "books", "quotes", "notes", 'u_texts', 'images', 'cross_refs']

def query_headword_chong():
	# 建立数据库连接
	conn = None
	try:
		conn = pymysql.connect(**MYSQL_CONFIG)
		cursor = conn.cursor(pymysql.cursors.DictCursor)  # 使用字典游标，结果以字典形式返回

		# 执行查询语句
		query_sql = "SELECT senses FROM dyhdc_dict WHERE headword = %s;"
		cursor.execute(query_sql, ("年",))  # 使用参数化查询，避免SQL注入

		# 获取查询结果
		result = cursor.fetchone()["senses"]  # 因为headword是主键，只会有一条结果，用fetchone()
		dict_obj = json.loads(result)
		dict_obj_ = []
		for item in dict_obj:
			if item['see']:
				dict_obj_.append(item)
		for item in dict_obj_:
			for e in item['examples']:
				for re in REMOVE_ITEMS_EXAMPLE:
					e.pop(re, None)
			for e in REMOVE_ITEMS:
					item.pop(e, None)
			print(item)

	except pymysql.MySQLError as e:
		print(f"数据库查询出错：{e}")
	finally:
		if conn:
			conn.close()  # 关闭数据库连接


if __name__ == "__main__":
	query_headword_chong()"""