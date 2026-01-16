import json
import pymysql
from pymysql.err import IntegrityError

# -------------------------- 配置项 --------------------------
JSONL_FILE_PATH = "./data/data.jsonl"  # 你的JSONL文件路径
MYSQL_CONFIG = {
	"host": "127.0.0.1",
	"port": 3306,
	"user": "root",  # 替换为你的MySQL用户名
	"password": "your_root_password",  # 替换为你的MySQL密码
	"database": "test",  # 替换为你的数据库名（需提前创建）
	"charset": "utf8mb4"
}
BATCH_SIZE = 100  # 批量插入大小，可根据服务器性能调整
# -------------------------------------------------------------

def create_table(conn):
	"""创建数据表（若不存在）"""
	create_sql = """
    CREATE TABLE IF NOT EXISTS dyhdc_dict (
        headword VARCHAR(255) NOT NULL COMMENT '原始词头（主键）',
        hw VARCHAR(255) COMMENT '展示用词头',
        simp VARCHAR(255) COMMENT '简体词头',
        pron VARCHAR(255) COMMENT '读音文本',
        yinyun JSON COMMENT '音韵信息数组',
        senses JSON COMMENT '义项数组',
        images JSON COMMENT '图片src数组',
        cross_refs JSON COMMENT '交叉引用链接数组',
        redirect_to VARCHAR(255) COMMENT '重定向目标词头',
        variant_of JSON COMMENT '相关词头数组',
        source_class VARCHAR(50) COMMENT '根容器class',
        alts JSON COMMENT '别名/附加内容数组',
        html_clean TEXT COMMENT '清理后的原始HTML',
        PRIMARY KEY (headword)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='汉语大词典数据';
    """
	with conn.cursor() as cursor:
		cursor.execute(create_sql)
	conn.commit()


def process_jsonl_and_insert():
	"""读取JSONL并插入MySQL"""
	# 建立MySQL连接
	conn = pymysql.connect(**MYSQL_CONFIG)
	try:
		# 1. 创建表
		create_table(conn)

		# 2. 逐行读取JSONL，批量插入
		batch_data = []
		with open(JSONL_FILE_PATH, "r", encoding="utf-8") as f:
			for line_num, line in enumerate(f, 1):
				line = line.strip()
				if not line:  # 跳过空行
					continue

				try:
					obj = json.loads(line)
				except json.JSONDecodeError as e:
					print(f"第{line_num}行JSON解析失败：{e}，跳过该行")
					continue

				# 过滤元信息行（headword以#开头）
				headword = obj.get("headword", "")
				if isinstance(headword, str) and headword.startswith("#"):
					continue

				# 提取字段（None转为MySQL的NULL）
				row = (
					headword,
					obj.get("hw"),
					obj.get("simp"),
					obj.get("pron"),
					json.dumps(obj.get("yinyun", []), ensure_ascii=False) if obj.get("yinyun") else None,
					json.dumps(obj.get("senses", []), ensure_ascii=False) if obj.get("senses") else None,
					json.dumps(obj.get("images", []), ensure_ascii=False) if obj.get("images") else None,
					json.dumps(obj.get("cross_refs", []), ensure_ascii=False) if obj.get("cross_refs") else None,
					obj.get("redirect_to"),
					json.dumps(obj.get("variant_of", []), ensure_ascii=False) if obj.get("variant_of") else None,
					obj.get("source_class"),
					json.dumps(obj.get("alts", []), ensure_ascii=False) if obj.get("alts") else None,
					obj.get("html_clean")
				)
				batch_data.append(row)

				# 批量插入
				if len(batch_data) >= BATCH_SIZE:
					insert_batch(conn, batch_data, line_num)
					batch_data = []

			# 插入剩余数据
			if batch_data:
				insert_batch(conn, batch_data, line_num)

		print("数据导入完成！")

	finally:
		conn.close()


def insert_batch(conn, batch_data, current_line):
	"""批量插入数据，处理主键重复等异常"""
	insert_sql = """
    INSERT INTO dyhdc_dict (
        headword, hw, simp, pron, yinyun, senses, images,
        cross_refs, redirect_to, variant_of, source_class, alts, html_clean
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE  -- 主键重复时更新字段（可选，根据需求调整）
        hw = VALUES(hw),
        simp = VALUES(simp),
        pron = VALUES(pron),
        yinyun = VALUES(yinyun),
        senses = VALUES(senses)
    """
	try:
		with conn.cursor() as cursor:
			cursor.executemany(insert_sql, batch_data)
		conn.commit()
		print(f"成功插入/更新 {len(batch_data)} 条数据（处理至第{current_line}行）")
	except IntegrityError as e:
		print(f"批量插入失败（第{current_line}行附近）：{e}，尝试逐行插入排查")
		# 逐行插入定位错误
		for idx, row in enumerate(batch_data):
			try:
				with conn.cursor() as cursor:
					cursor.execute(insert_sql, row)
				conn.commit()
			except Exception as e2:
				print(f"第{current_line - len(batch_data) + idx + 1}行插入失败：{e2}，跳过该行")
	except Exception as e:
		conn.rollback()
		print(f"批量插入异常：{e}，跳过该批次")


if __name__ == "__main__":
	# 安装依赖：pip install pymysql
	process_jsonl_and_insert()