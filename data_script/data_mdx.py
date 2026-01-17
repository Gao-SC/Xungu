import json
import pymysql
from pymysql.err import IntegrityError

# -------------------------- 配置项（请根据实际情况修改） --------------------------
MDX_FILE_PATH = "../data/data.json"
MYSQL_CONFIG = {
	"host": "127.0.0.1",
	"port": 3306,
	"user": "root",
	"password": "your_root_password",
	"database": "test",
	"charset": "utf8mb4"
}
BATCH_SIZE = 100


# --------------------------------------------------------------------------------

def create_mysql_table(conn):
	"""创建指定结构的mdx_dict表（若不存在）"""
	create_sql = """
    CREATE TABLE IF NOT EXISTS mdx_dict (
	    headword VARCHAR(10) UNIQUE NOT NULL,  -- 汉字字段，限定长度+唯一约束
	    modern_reading TEXT,             -- 现代读音
	    old_chinese TEXT,                -- 上古音（JSON字符串存储嵌套结构）
	    middle_chinese TEXT,             -- 中古音（JSON字符串存储嵌套结构）
	    rhyme TEXT,                      -- 韵部信息（JSON字符串存储嵌套结构）
	    phonetic_structure TEXT,         -- 声韵结构
	    dialects TEXT,                   -- 方言信息（JSON字符串存储嵌套结构）
	    PRIMARY KEY (headword)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
  """
	try:
		with conn.cursor() as cursor:
			cursor.execute(create_sql)
		conn.commit()
		print("数据表mdx_dict创建/验证完成")
	except Exception as e:
		print(f"创建表失败：{e}")
		raise


def parse_mdx_and_insert():
	"""解析MDX文件并批量插入MySQL"""
	conn = pymysql.connect(**MYSQL_CONFIG)
	conn.autocommit(False)

	try:
		with open(MDX_FILE_PATH, "r", encoding="utf-8") as f:
			data = json.load(f)
		print(f"成功读取JSON文件，共{len(data)}条汉字数据")
	except FileNotFoundError:
		print(f"错误：JSON文件 {MDX_FILE_PATH} 不存在")
		return
	except json.JSONDecodeError as e:
		print(f"错误：JSON文件格式无效 - {e}")
		return

	try:
		# 3. 创建数据表
		create_mysql_table(conn)
		# 5. 批量读取释义并插入数据库
		batch_data = []
		for idx, word in enumerate(data, 1):
			try:
				row = (
					word["character"],
					word["modern_reading"],
					json.dumps(word["old_chinese"], ensure_ascii=False),
					json.dumps(word["middle_chinese"], ensure_ascii=False),
					json.dumps(word["rhyme"], ensure_ascii=False),
					word["phonetic_structure"],
					json.dumps(word["dialects"], ensure_ascii=False)
				)
				batch_data.append(row)
				if len(batch_data) >= BATCH_SIZE:
					insert_batch(conn, batch_data, idx, len(data))
					batch_data = []

			except Exception as e:
				print(f"处理词条【{word}】失败：{e}，跳过该词条")
				continue

		if batch_data:
			insert_batch(conn, batch_data, len(data), len(data))

		print(f"所有词条处理完成！共处理 {len(data)} 个词条")

	finally:
		# 确保数据库连接关闭
		conn.close()
		print("MySQL连接已关闭")


def insert_batch(conn, batch_data, current_idx, total_idx):
	"""批量插入数据，处理主键重复等异常"""
	insert_sql = """
		INSERT IGNORE INTO mdx_dict (
	    headword, modern_reading, old_chinese, middle_chinese,
	    rhyme, phonetic_structure, dialects
		) VALUES (%s, %s, %s, %s, %s, %s, %s)
   """
	try:
		with conn.cursor() as cursor:
			cursor.executemany(insert_sql, batch_data)
		conn.commit()
		print(f"成功插入/更新 {len(batch_data)} 条数据 | 进度：{current_idx}/{total_idx}")
	except IntegrityError as e:
		# 主键重复等完整性错误，回滚后尝试逐行插入定位问题
		conn.rollback()
		print(f"批量插入失败：{e}，尝试逐行插入排查问题")
		for single_data in batch_data:
			try:
				with conn.cursor() as cursor:
					cursor.execute(insert_sql, (
						json.dumps(single_data["character"], ensure_ascii=False),
						json.dumps(single_data["modern_reading"], ensure_ascii=False),
						json.dumps(single_data["old_chinese"], ensure_ascii=False),
						json.dumps(single_data["middle_chinese"], ensure_ascii=False),
						json.dumps(single_data["rhyme"], ensure_ascii=False),
						json.dumps(single_data["phonetic_structure"], ensure_ascii=False),
						json.dumps(single_data["dialects"], ensure_ascii=False)
					))
				conn.commit()
			except Exception as e2:
				print(f"逐行插入词条【{single_data["character"]}】失败：{e2}，跳过该词条")
	except Exception as e:
		conn.rollback()
		print(f"批量插入异常：{e}，跳过该批次数据")


if __name__ == "__main__":
	# 执行主流程
	try:
		parse_mdx_and_insert()
	except Exception as e:
		print(f"程序执行失败：{e}")