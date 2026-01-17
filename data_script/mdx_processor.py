import re
import json
import os  # 新增：用于遍历目录下的txt文件


def detect_file_format(file_content):
    """
    检测文件格式
    
    Args:
        file_content (str): 文件内容
        
    Returns:
        str: 文件格式类型
    """
    # 检测dic.mdx.txt格式：包含@@@LINK=模式
    if "@@@LINK=" in file_content:
        return "dic"
    
    # 检测pron2.mdx.txt格式：包含<h1>和<ul>列表结构
    if re.search(r'<h1>.*?</h1>\s*<ul>', file_content):
        return "pron2"
    
    # 检测pron3.mdx.txt格式：包含完整的HTML表格和Modern (Beijing) reading字段
    if re.search(r'<th>Modern \(Beijing\) reading</th>', file_content):
        return "pron3"
    
    # 默认是pron1.mdx.txt格式
    return "pron1"


def extract_dic_format(input_text):
    """
    提取dic.mdx.txt格式的数据
    
    Args:
        input_text (str): 文件内容
        
    Returns:
        list: 提取的数据列表
    """
    # 匹配格式：字符\n@@@LINK=目标字符\n</>
    char_blocks = re.findall(r'([\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df])\s*@@@LINK=(.*?)\s*</>', input_text)
    
    result = []
    for char, link in char_blocks:
        char_data = {
            "character": char,
            "modern_reading": "",
            "old_chinese": {
                "preclassic": "",
                "classic": "",
                "western_han": "",
                "eastern_han": "",
                "reconstruction": ""
            },
            "middle_chinese": {
                "postclassic": {
                    "early": "",
                    "middle": "",
                    "late": ""
                },
                "reading": "",
                "fanqie": ""
            },
            "rhyme": {
                "old_rhyme": "",
                "middle_rhyme": ""
            },
            "phonetic_structure": "",
            "dialects": {}
        }
        
        result.append(char_data)
    
    return result


def extract_pron2_format(input_text):
    """
    提取pron2.mdx.txt格式的数据
    
    Args:
        input_text (str): 文件内容
        
    Returns:
        list: 提取的数据列表
    """
    # 匹配格式：字符\n<h1>字符</h1><ul><li>...</li></ul>\n</>
    char_blocks = re.findall(r'([\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df])\s*(.*?)\s*</>', input_text, re.DOTALL)
    
    result = []
    for char, html_content in char_blocks:
        char_data = {
            "character": char,
            "modern_reading": "",
            "old_chinese": {
                "preclassic": "",
                "classic": "",
                "western_han": "",
                "eastern_han": "",
                "reconstruction": ""
            },
            "middle_chinese": {
                "postclassic": {
                    "early": "",
                    "middle": "",
                    "late": ""
                },
                "reading": "",
                "fanqie": ""
            },
            "rhyme": {
                "old_rhyme": "",
                "middle_rhyme": ""
            },
            "phonetic_structure": "",
            "dialects": {}
        }
        
        # 提取现代读音（ul中的第一个li）
        modern_match = re.search(r'<ul>\s*<li>(.*?)</li>', html_content)
        if modern_match:
            char_data["modern_reading"] = modern_match.group(1).strip()
        
        # 提取上古音重构（ul中的第四个li）
        old_chinese_match = re.search(r'<ul>.*?<li>.*?</li>.*?<li>.*?</li>.*?<li>.*?</li>.*?<li>(.*?)</li>', html_content, re.DOTALL)
        if old_chinese_match:
            char_data["old_chinese"]["reconstruction"] = old_chinese_match.group(1).strip()
        
        result.append(char_data)
    
    return result


def extract_pron3_format(input_text):
    """
    提取pron3.mdx.txt格式的数据
    
    Args:
        input_text (str): 文件内容
        
    Returns:
        list: 提取的数据列表
    """
    # 匹配格式：字符\n<link rel="stylesheet"...><h1>字符</h1>...</table>\n</>
    char_blocks = re.findall(r'([\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df])\s*(.*?)\s*</>', input_text, re.DOTALL)
    
    result = []
    for char, html_content in char_blocks:
        char_data = {
            "character": char,
            "modern_reading": "",
            "old_chinese": {
                "preclassic": "",
                "classic": "",
                "western_han": "",
                "eastern_han": "",
                "reconstruction": ""
            },
            "middle_chinese": {
                "postclassic": {
                    "early": "",
                    "middle": "",
                    "late": ""
                },
                "reading": "",
                "fanqie": ""
            },
            "rhyme": {
                "old_rhyme": "",
                "middle_rhyme": ""
            },
            "phonetic_structure": "",
            "dialects": {}
        }
        
        # 提取现代北京读音
        modern_match = re.search(r'<th>Modern \(Beijing\) reading</th><td>(.*?)</td>', html_content)
        if modern_match:
            char_data["modern_reading"] = modern_match.group(1).strip()
        
        # 提取上古音相关字段
        preclassic_match = re.search(r'<th>Preclassic Old Chinese</th><td>(.*?)</td>', html_content)
        if preclassic_match:
            char_data["old_chinese"]["preclassic"] = preclassic_match.group(1).strip()
        
        classic_match = re.search(r'<th>Classic Old Chinese</th><td>(.*?)</td>', html_content)
        if classic_match:
            char_data["old_chinese"]["classic"] = classic_match.group(1).strip()
        
        western_han_match = re.search(r'<th>Western Han Chinese</th><td>(.*?)</td>', html_content)
        if western_han_match:
            char_data["old_chinese"]["western_han"] = western_han_match.group(1).strip()
        
        eastern_han_match = re.search(r'<th>Eastern Han Chinese</th><td>(.*?)</td>', html_content)
        if eastern_han_match:
            char_data["old_chinese"]["eastern_han"] = eastern_han_match.group(1).strip()
        
        # 提取中古音相关字段
        early_post_match = re.search(r'<th>Early Postclassic Chinese</th><td>(.*?)</td>', html_content)
        if early_post_match:
            char_data["middle_chinese"]["postclassic"]["early"] = early_post_match.group(1).strip()
        
        middle_post_match = re.search(r'<th>Middle Postclassic Chinese</th><td>(.*?)</td>', html_content)
        if middle_post_match:
            char_data["middle_chinese"]["postclassic"]["middle"] = middle_post_match.group(1).strip()
        
        late_post_match = re.search(r'<th>Late Postclassic Chinese</th><td>(.*?)</td>', html_content)
        if late_post_match:
            char_data["middle_chinese"]["postclassic"]["late"] = late_post_match.group(1).strip()
        
        middle_reading_match = re.search(r'<th>Middle Chinese</th><td>(.*?)</td>', html_content)
        if middle_reading_match:
            char_data["middle_chinese"]["reading"] = middle_reading_match.group(1).strip()
        
        fanqie_match = re.search(r'<th>Fanqie</th><td>(.*?)</td>', html_content)
        if fanqie_match:
            char_data["middle_chinese"]["fanqie"] = fanqie_match.group(1).strip()
        
        rhyme_class_match = re.search(r'<th>Rhyme class</th><td>(.*?)</td>', html_content)
        if rhyme_class_match:
            char_data["rhyme"]["middle_rhyme"] = rhyme_class_match.group(1).strip()
        
        result.append(char_data)
    
    return result


def extract_pron1_format(input_text):
    """
    提取pron1.mdx.txt格式的数据
    
    Args:
        input_text (str): 文件内容
        
    Returns:
        list: 提取的数据列表
    """
    # 匹配格式：汉字 + HTML内容 + </>
    char_blocks = re.findall(r'([\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df])\s*(.*?)\s*</>', input_text, re.DOTALL)

    result = []
    for char, html_content in char_blocks:
        # 初始化当前汉字的结构化数据
        char_data = {
            "character": char,
            "modern_reading": "",
            "old_chinese": {
                "preclassic": "",
                "classic": "",
                "western_han": "",
                "eastern_han": "",
                "reconstruction": ""
            },
            "middle_chinese": {
                "postclassic": {
                    "early": "",
                    "middle": "",
                    "late": ""
                },
                "reading": "",
                "fanqie": ""
            },
            "rhyme": {
                "old_rhyme": "",
                "middle_rhyme": ""
            },
            "phonetic_structure": "",
            "dialects": {}
        }

        # 提取核心字段
        # 上古韻部
        old_rhyme_match = re.search(r'<th>上古韻部</th><td>(.*?)</td>', html_content)
        if old_rhyme_match:
            char_data["rhyme"]["old_rhyme"] = old_rhyme_match.group(1).strip()

        # 上古音
        old_chinese_match = re.search(r'<th>上古音</th><td>(.*?)</td>', html_content)
        if old_chinese_match:
            char_data["old_chinese"]["reconstruction"] = old_chinese_match.group(1).strip()
        else:
            # 尝试匹配直接的上古音（不在<th><td>结构中）
            old_chinese_match = re.search(r'<u>(.*?)</u>', html_content)
            if old_chinese_match:
                char_data["old_chinese"]["reconstruction"] = old_chinese_match.group(1).strip()

        # 提取中古音韻地位表格中的信息
        middle_chinese_table = re.search(r'<table><caption>中古音韻地位</caption>(.*?)</table>', html_content, re.DOTALL)
        if middle_chinese_table:
            table_content = middle_chinese_table.group(1)
            
            # 反切
            fanqie_match = re.search(r'<th>反切</th><td>(.*?)</td>', table_content)
            if fanqie_match:
                char_data["middle_chinese"]["fanqie"] = fanqie_match.group(1).strip()
            
            # 聲母
            shengmu_match = re.search(r'<th>聲母</th><td>(.*?)</td>', table_content)
            if shengmu_match:
                char_data["middle_chinese"]["shengmu"] = shengmu_match.group(1).strip()
            
            # 韻
            yun_match = re.search(r'<th>韻</th><td>(.*?)</td>', table_content)
            if yun_match:
                char_data["middle_chinese"]["yun"] = yun_match.group(1).strip()
            
            # 開合
            kaihe_match = re.search(r'<th>開合</th><td>(.*?)</td>', table_content)
            if kaihe_match:
                char_data["middle_chinese"]["kaihe"] = kaihe_match.group(1).strip()
            
            # 等
            deng_match = re.search(r'<th>等</th><td>(.*?)</td>', table_content)
            if deng_match:
                char_data["middle_chinese"]["deng"] = deng_match.group(1).strip()
            
            # 聲調
            shengdiao_match = re.search(r'<th>聲調</th><td>(.*?)</td>', table_content)
            if shengdiao_match:
                char_data["middle_chinese"]["shengdiao"] = shengdiao_match.group(1).strip()

        result.append(char_data)

    return result


def extract_chinese_char_data(input_text):
    """
    从输入的文本中提取每个汉字的语音信息并结构化（根据文件格式自动选择提取方法）

    Args:
        input_text (str): 包含汉字语音信息的文本

    Returns:
        list: 包含每个汉字结构化数据的列表
    """
    # 检测文件格式
    file_format = detect_file_format(input_text)
    
    # 根据不同格式调用不同的提取函数
    if file_format == "dic":
        return extract_dic_format(input_text)
    elif file_format == "pron2":
        return extract_pron2_format(input_text)
    elif file_format == "pron3":
        return extract_pron3_format(input_text)
    elif file_format == "pron1":
        return extract_pron1_format(input_text)
    else:
        return []


def save_to_json(data, output_file="data.json"):
    """
    将结构化数据保存为JSON文件（固定输出为1.json）

    Args:
        data (list): 结构化的汉字语音数据
        output_file (str): 输出JSON文件名，默认1.json
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        # indent=4 格式化输出，ensure_ascii=False 保留中文
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"所有数据已汇总保存到 {output_file}")


# ------------------- 主程序执行 -------------------
if __name__ == "__main__":
    # 初始化汇总数据的列表
    all_char_data = []

    # 1. 获取当前目录下所有.txt文件
    current_dir = os.getcwd()  # 获取当前工作目录
    txt_files = [f for f in os.listdir(current_dir) if f.endswith('.txt')]

    if not txt_files:
        print("警告：当前目录下未找到任何.txt文件！")
    else:
        print(f"找到 {len(txt_files)} 个txt文件，开始处理...")

        # 2. 遍历每个txt文件，读取内容并提取数据
        for txt_file in txt_files:
            file_path = os.path.join(current_dir, txt_file)
            try:
                # 读取txt文件内容（指定utf-8编码避免乱码）
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()

                # 检测文件格式
                file_format = detect_file_format(file_content)
                print(f"🔍 正在处理：{txt_file}（格式：{file_format}）")

                # 根据文件格式选择提取函数
                if file_format == "dic":
                    char_data = extract_dic_format(file_content)
                elif file_format == "pron2":
                    char_data = extract_pron2_format(file_content)
                elif file_format == "pron3":
                    char_data = extract_pron3_format(file_content)
                elif file_format == "pron1":
                    char_data = extract_pron1_format(file_content)
                else:
                    char_data = []

                # 将当前文件的数据添加到汇总列表
                all_char_data.extend(char_data)
                print(f"✅ 处理完成：{txt_file}（提取到 {len(char_data)} 个汉字）")

            except Exception as e:
                print(f"❌ 处理失败：{txt_file}，错误信息：{str(e)}")

    # 3. 合并相同汉字的数据（智能合并，保留所有有效字段）
    merged_char_dict = {}
    
    for item in all_char_data:
        char = item['character']
        
        if char in merged_char_dict:
            # 合并已有数据和新数据，保留所有有效字段
            existing = merged_char_dict[char]
            
            # 合并现代读音
            if item['modern_reading'] and not existing['modern_reading']:
                existing['modern_reading'] = item['modern_reading']
            
            # 合并上古音相关字段
            for field in ['preclassic', 'classic', 'western_han', 'eastern_han', 'reconstruction']:
                if item['old_chinese'][field] and not existing['old_chinese'][field]:
                    existing['old_chinese'][field] = item['old_chinese'][field]
            
            # 合并中古音相关字段
            # postclassic
            for period in ['early', 'middle', 'late']:
                if item['middle_chinese']['postclassic'][period] and not existing['middle_chinese']['postclassic'][period]:
                    existing['middle_chinese']['postclassic'][period] = item['middle_chinese']['postclassic'][period]
            
            # other middle chinese fields
            for field in ['reading', 'fanqie', 'shengmu', 'yun', 'kaihe', 'deng', 'shengdiao']:
                if item['middle_chinese'].get(field, '') and not existing['middle_chinese'].get(field, ''):
                    existing['middle_chinese'][field] = item['middle_chinese'][field]
            
            # 合并韵部
            for field in ['old_rhyme', 'middle_rhyme']:
                if item['rhyme'][field] and not existing['rhyme'][field]:
                    existing['rhyme'][field] = item['rhyme'][field]
        else:
            # 添加新数据
            merged_char_dict[char] = item
    
    merged_char_data = list(merged_char_dict.values())
    
    # 4. 过滤掉没有有效数据的记录（至少需要有一个字段有值）
    filtered_char_data = []
    for item in merged_char_data:
        # 检查是否有任何字段有值
        has_data = False
        
        # 检查现代读音
        if item['modern_reading']:
            has_data = True
        
        # 检查上古音相关字段
        if any(item['old_chinese'].values()):
            has_data = True
        
        # 检查上古韻部
        if any(item['rhyme'].values()):
            has_data = True
        
        # 检查中古音相关字段
        if any([
            item['middle_chinese']['fanqie'],
            item.get('middle_chinese', {}).get('shengmu', ''),
            item.get('middle_chinese', {}).get('yun', ''),
            item.get('middle_chinese', {}).get('kaihe', ''),
            item.get('middle_chinese', {}).get('deng', ''),
            item.get('middle_chinese', {}).get('shengdiao', ''),
            any(item['middle_chinese']['postclassic'].values())
        ]):
            has_data = True
        
        if has_data:
            filtered_char_data.append(item)
    
    # 5. 保存汇总后的数据到1.json
    if filtered_char_data:
        save_to_json(filtered_char_data)
        print(f"\n最终汇总：共提取到 {len(all_char_data)} 个汉字")
        print(f"去重后：共保留 {len(merged_char_data)} 个不重复的汉字")
        print(f"过滤后：共保留 {len(filtered_char_data)} 个有有效数据的汉字")
        print(f"📊 数据完整性：")
        print(f"   - 现代读音：{sum(1 for item in filtered_char_data if item['modern_reading'])} 个")
        print(f"   - 上古音重构：{sum(1 for item in filtered_char_data if item['old_chinese']['reconstruction'])} 个")
        print(f"   - 反切：{sum(1 for item in filtered_char_data if item['middle_chinese']['fanqie'])} 个")
        print(f"   - 上古韻部：{sum(1 for item in filtered_char_data if item['rhyme']['old_rhyme'])} 个")
    else:
        print("\n未提取到任何有效汉字数据，未生成1.json")