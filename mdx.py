import os
import pymysql
from pymysql.err import IntegrityError

# -------------------------- 配置项（请根据实际情况修改） --------------------------
MDX_FILE_PATH = "./data/dic.mdx"
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
        word VARCHAR(512) NOT NULL COMMENT '词典词条（主键）',
        definition LONGTEXT COMMENT '词条释义（HTML格式）',
        word_length INT COMMENT '词条长度（可选，用于查询优化）',
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '入库时间',
        update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
        PRIMARY KEY (word),
        INDEX idx_word_length (word_length)  -- 可选索引，优化按长度查询
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='MDX字典数据';
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
	# 1. 验证MDX文件是否存在
	if not os.path.exists(MDX_FILE_PATH):
		raise FileNotFoundError(f"MDX文件不存在：{MDX_FILE_PATH}")

	# 2. 建立MySQL连接（设置自动提交为False，便于事务控制）
	conn = pymysql.connect(**MYSQL_CONFIG)
	conn.autocommit(False)

	try:
		# 3. 创建数据表
		create_mysql_table(conn)

		# 4. 初始化MDX解析器
		print(f"开始解析MDX文件：{MDX_FILE_PATH}")
		mdx = MDict(MDX_FILE_PATH)
		# 获取所有词条（返回有序列表，包含所有word）
		all_words = mdx.keys()
		total_words = len(all_words)
		print(f"MDX文件解析完成，共发现 {total_words} 个词条")

		# 5. 批量读取释义并插入数据库
		batch_data = []
		for idx, word in enumerate(all_words, 1):
			try:
				# 读取词条对应的HTML释义（mdict_utils会自动处理编码）
				definition = mdx.get(word)
				# 计算词条长度（按字符数，不是字节数）
				word_length = len(word)

				# 组装插入数据（None值会自动转为MySQL的NULL）
				batch_data.append((
					word,
					definition,
					word_length
				))

				# 达到批量大小则执行插入
				if len(batch_data) >= BATCH_SIZE:
					insert_batch(conn, batch_data, idx, total_words)
					batch_data = []

			except Exception as e:
				print(f"处理词条【{word}】失败：{e}，跳过该词条")
				continue

		# 插入剩余的未批量数据
		if batch_data:
			insert_batch(conn, batch_data, total_words, total_words)

		print(f"所有词条处理完成！共处理 {total_words} 个词条")

	finally:
		# 确保数据库连接关闭
		conn.close()
		print("MySQL连接已关闭")


def insert_batch(conn, batch_data, current_idx, total_idx):
	"""批量插入数据，处理主键重复等异常"""
	insert_sql = """
    INSERT INTO mdx_dict (word, definition, word_length)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE  -- 主键（word）重复时更新释义和长度
        definition = VALUES(definition),
        word_length = VALUES(word_length)
    """
	try:
		with conn.cursor() as cursor:
			# executemany批量插入，效率远高于单条插入
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
					cursor.execute(insert_sql, single_data)
				conn.commit()
			except Exception as e2:
				print(f"逐行插入词条【{single_data[0]}】失败：{e2}，跳过该词条")
	except Exception as e:
		conn.rollback()
		print(f"批量插入异常：{e}，跳过该批次数据")


if __name__ == "__main__":
	# 执行主流程
	try:
		parse_mdx_and_insert()
	except Exception as e:
		print(f"程序执行失败：{e}")