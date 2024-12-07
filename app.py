# -*- coding: utf-8 -*-
"""
日本人信息生成器
用于生成包含地址、姓名、个人信息等在内的完整日本人信息
包含日文、罗马字和中文的多语言支持
"""

import random
import string
import uuid
from datetime import datetime, timedelta
import json
from faker import Faker
import pykakasi
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from logging.handlers import RotatingFileHandler

# 创建 Flask 应用实例
app = Flask(__name__)
# 生产环境应该限制 CORS
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv('ALLOWED_ORIGINS', '*').split(',')  # 默认允许所有来源
    }
})

# 添加请求限制
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[
        f"{os.getenv('RATE_LIMIT_PER_MINUTE', '10')} per minute",
        "200 per day"
    ]
)

# 创建日本语言的 Faker 实例
fake_jp = Faker(['ja_JP'])
fake_en = Faker(['en_US'])

# 在文件开头添加转换器���例
kks = pykakasi.Kakasi()

# 定义日本地区数据
JAPAN_REGIONS = {
    "東京都": {
        "code": "13",
        "cities": {
            "新宿区": {
                "zip_codes": ["160-0001", "160-0002", "160-0003", "160-0004", "160-0005"],
                "phone_area_code": "03",
                "areas": ["新宿", "歌舞伎町", "四谷", "西新宿", "大久保", "神楽坂", "市谷", "早稲田"],
                "en_name": "Shinjuku-ku",
                "cn_name": "新宿区"
            },
            "渋谷区": {
                "zip_codes": ["150-0001", "150-0002", "150-0003", "150-0004"],
                "phone_area_code": "03",
                "areas": ["神宮前", "渋谷", "代々木", "原宿", "恵比寿", "広尾", "表参道"],
                "en_name": "Shibuya-ku",
                "cn_name": "涩谷"
            },
            "港区": {
                "zip_codes": ["105-0001", "105-0002", "105-0003", "105-0004"],
                "phone_area_code": "03",
                "areas": ["虎ノ門", "新橋", "赤坂", "六本木", "芝公園", "台場"],
                "en_name": "Minato-ku",
                "cn_name": "港区"
            }
        }
    },
    "大阪府": {
        "code": "27",
        "cities": {
            "大阪市西淀川区": {
                "zip_codes": ["555-0001", "555-0002", "555-0011", "555-0012"],
                "phone_area_code": "06",
                "areas": ["御幣島", "竹島", "高須町", "中島", "佃", "野里", "姫島"],
                "en_name": "Nishiyodogawa-ku",
                "cn_name": "西淀川区"
            },
            "大阪市北区": {
                "zip_codes": ["530-0001", "530-0002", "530-0003", "530-0004"],
                "phone_area_code": "06",
                "areas": ["梅田", "曽根崎", "角田", "堂", "中之島", "天神橋"],
                "en_name": "Kita-ku",
                "cn_name": "北区"
            },
            "大阪市中央区": {
                "zip_codes": ["540-0001", "540-0002", "540-0003", "540-0004"],
                "phone_area_code": "06",
                "areas": ["心斎橋", "道頓堀", "難波", "天満橋", "本町"],
                "en_name": "Chuo-ku",
                "cn_name": "中央区"
            }
        }
    },
    "神奈川県": {
        "code": "14",
        "cities": {
            "横浜市中区": {
                "zip_codes": ["231-0001", "231-0002", "231-0003", "231-0004"],
                "phone_area_code": "045",
                "areas": ["山手町", "海岸通", "日本大通", "元町", "山下町", "中華街"],
                "en_name": "Naka-ku",
                "cn_name": "中区"
            },
            "横浜市西区": {
                "zip_codes": ["220-0001", "220-0002", "220-0003"],
                "phone_area_code": "045",
                "areas": ["みなとみらい", "北幸", "南幸", "戸部", "高島"],
                "en_name": "Nishi-ku",
                "cn_name": "西区"
            }
        }
    },
    "北海道": {
        "code": "01",
        "cities": {
            "札幌市中央区": {
                "zip_codes": ["060-0001", "060-0002", "060-0003", "060-0004"],
                "phone_area_code": "011",
                "areas": ["北一条西", "大通西", "北三条西", "南一条西", "すすきの"],
                "en_name": "Chuo-ku",
                "cn_name": "中央区"
            },
            "札幌市北区": {
                "zip_codes": ["001-0001", "001-0002", "001-0003"],
                "phone_area_code": "011",
                "areas": ["北一条", "北二条", "北三条", "麻生", "北二十四条"],
                "en_name": "Kita-ku",
                "cn_name": "北区"
            }
        }
    },
    "福岡県": {
        "code": "40",
        "cities": {
            "福岡市博多区": {
                "zip_codes": ["812-0001", "812-0002", "812-0003", "812-0004"],
                "phone_area_code": "092",
                "areas": ["博多駅前", "住吉", "祇園町", "上川端町", "中洲"],
                "en_name": "Hakata-ku",
                "cn_name": "博多区"
            },
            "福岡市中央区": {
                "zip_codes": ["810-0001", "810-0002", "810-0003"],
                "phone_area_code": "092",
                "areas": ["天神", "大名", "春吉", "赤坂", "本松"],
                "en_name": "Chuo-ku",
                "cn_name": "中央区"
            }
        }
    },
    "京都府": {
        "code": "26",
        "cities": {
            "京都市中京区": {
                "zip_codes": ["604-0001", "604-0002", "604-0003"],
                "phone_area_code": "075",
                "areas": ["二条", "御池", "河原町", "烏丸", "四条"],
                "en_name": "Nakagyo-ku",
                "cn_name": "中京区"
            },
            "京都市東山区": {
                "zip_codes": ["605-0001", "605-0002", "605-0003"],
                "phone_area_code": "075",
                "areas": ["清水", "祇園", "円山公園", "知恩院", "高台寺"],
                "en_name": "Higashiyama-ku",
                "cn_name": "东山区"
            }
        }
    },
    "愛知県": {
        "code": "23",
        "cities": {
            "名古屋市中区": {
                "zip_codes": ["460-0001", "460-0002", "460-0003"],
                "phone_area_code": "052",
                "areas": ["", "丸の内", "錦", "大須", "金山"],
                "en_name": "Naka-ku",
                "cn_name": "中区"
            },
            "名古屋市千種区": {
                "zip_codes": ["464-0001", "464-0002", "464-0003"],
                "phone_area_code": "052",
                "areas": ["千種", "今池", "池下", "覚王山", "星が丘"],
                "en_name": "Chikusa-ku",
                "cn_name": "千种区"
            }
        }
    },
    "兵庫県": {
        "code": "28",
        "cities": {
            "神戸市中��区": {
                "zip_codes": ["650-0001", "650-0002", "650-0003", "650-0004"],
                "phone_area_code": "078",
                "areas": ["元町", "三宮", "北野", "港島中町", "浜辺通"],
                "en_name": "Chuo-ku",
                "cn_name": "中央区"
            },
            "神戸市灘区": {
                "zip_codes": ["657-0001", "657-0002", "657-0003"],
                "phone_area_code": "078",
                "areas": ["六甲", "篠原", "摩耶", "岩屋", "王子町"],
                "en_name": "Nada-ku",
                "cn_name": "灘区"
            }
        }
    },
    "埼玉": {
        "code": "11",
        "cities": {
            "さいたま市大宮区": {
                "zip_codes": ["330-0801", "330-0802", "330-0803"],
                "phone_area_code": "048",
                "areas": ["土手町", "宮町", "高鼻町", "大門町"],
                "en_name": "Omiya-ku",
                "cn_name": "大宫区"
            },
            "川越市": {
                "zip_codes": ["350-0001", "350-0002", "350-0003"],
                "phone_area_code": "049",
                "areas": ["小仙波", "郭町", "菅原�", "連雀町", "元町"],
                "en_name": "Kawagoe-shi",
                "cn_name": "川越市"
            }
        }
    },
    "千葉": {
        "code": "12",
        "cities": {
            "千葉市中央区": {
                "zip_codes": ["260-0001", "260-0002", "260-0003"],
                "phone_area_code": "043",
                "areas": ["都町", "中央港", "新町", "栄町", "富士見"],
                "en_name": "Chuo-ku",
                "cn_name": "中央区"
            },
            "船橋市": {
                "zip_codes": ["273-0001", "273-0002", "273-0003"],
                "phone_area_code": "047",
                "areas": ["市場", "東船橋", "本町", "海神", "湊町"],
                "en_name": "Funabashi-shi",
                "cn_name": "船桥市"
            }
        }
    }
}

# 将常量移到函数外部或配置文件中
BLOOD_TYPES = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
CREDIT_CARD_TYPES = ["JCB", "VISA", "MasterCard"]
SYSTEMS = ["Windows 10", "Windows 8.1", "macOS", "Linux"]

def get_romaji_name(japanese_name):
    """使用 pykakasi 将日文名字转换为罗马字"""
    result = kks.convert(japanese_name)
    return ''.join([item['hepburn'].capitalize() for item in result])

def validate_phone_number(phone):
    """验证电话号码格式"""
    pattern = r"\+81-\d{2,4}-\d{3,4}-\d{3,4}"
    return bool(re.match(pattern, phone))

def calculate_age(birthday):
    """根据生日计算年龄"""
    birth_date = datetime.strptime(birthday, "%m/%d/%Y")
    today = datetime.now()
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    return age

def generate_japanese_info():
    """
    生成随机的日本人信息
    
    Returns:
        dict: 包含完整的日本人信息，包括：
            - 个人信息（姓名、年龄、性别等）
            - 地址信息（日文、英文、中文）
            - 联系方式
            - 职业和教育信息
            - 其他补充信息
    """
    try:
        if not JAPAN_REGIONS:
            raise ValueError("地区数据为空")
        
        prefecture = random.choice(list(JAPAN_REGIONS.keys()))
        if not prefecture:
            raise ValueError("无法获��有效的都道府县")
            
        # 优化地址生成逻辑
        def generate_address(prefecture, city, area, block, house, room=None):
            """生成多语言地址"""
            jp = f"{prefecture}{city}{area}{block}丁目{house}番"
            en = f"{house}-{block}"
            cn = f"{prefecture}{city}{area}{block}丁目{house}号"
            
            if room:
                jp += f"{room}号"
                en += f"-{room}"
                cn += f"{room}室"
                
            en += f" {area}, {city_info['en_name']}, {prefecture}, Japan"
            
            return jp, en, cn
        
        # 选择地区信息
        city = random.choice(list(JAPAN_REGIONS[prefecture]["cities"].keys()))
        city_info = JAPAN_REGIONS[prefecture]["cities"][city]
        area = random.choice(city_info["areas"])
        zip_code = random.choice(city_info["zip_codes"])
        
        # 生成地址号码（更符合日本实际情况）
        block_number = random.randint(1, 29)  # 丁
        house_number = random.randint(1, 20)  # 番号
        room_number = random.randint(1, 1000) if random.random() < 0.3 else None  # 30%概率有房间号
        
        # 构建详细地址号码
        address_number = f"{block_number}-{house_number}"
        if room_number:
            address_number += f"-{room_number}"
        
        # 生成电话号码 (确保区号正确)
        phone_area = city_info["phone_area_code"]
        phone_middle = f"{random.randint(1000,9999) if len(phone_area) < 3 else random.randint(100,999)}"
        phone_last = f"{random.randint(1000,9999) if len(phone_middle) == 4 else random.randint(100,999)}"
        phone = f"+81-{phone_area}-{phone_middle}-{phone_last}"
        
        # 生成姓名（使用 Faker 生成真实的日本姓名）
        last_name = fake_jp.last_name()
        first_name = fake_jp.first_name()
        full_name = f"{first_name} {last_name}"
        
        # 使用 pykakasi 生成更准确的罗马字转换
        last_name_romaji = get_romaji_name(last_name)
        first_name_romaji = get_romaji_name(first_name)
        full_name_romaji = f"{first_name_romaji} {last_name_romaji}"
        
        # 生成假名表示（平假名和片假名）
        name_readings = kks.convert(full_name)
        hiragana_name = ''.join([item['hira'] for item in name_readings])
        katakana_name = ''.join([item['kana'] for item in name_readings])
        
        # 添加身高体重计算
        height_cm = random.randint(150, 190)
        height_ft = f"{height_cm // 30.48:.0f}' {(height_cm % 30.48) / 2.54:.0f}\""
        
        weight_kg = round(random.uniform(45, 95), 1)
        weight_lbs = round(weight_kg * 2.20462, 1)
        
        # 构建完整地址
        jp_address = f"{prefecture}{city}{area}{block_number}丁目{house_number}番"
        if room_number:
            jp_address += f"{room_number}号"
        
        # 英文地址格式修改
        en_address = f"{house_number}-{block_number}"
        if room_number:
            en_address += f"-{room_number}"
        en_address += f" {area}, {city_info['en_name']}, {prefecture}, Japan"
        
        # 中文地址格式修改
        cn_address = f"{prefecture}{city}{area}{block_number}丁目{house_number}号"
        if room_number:
            cn_address += f"{room_number}室"
        
        # 其余代码保持不变...
        person_info = {
            "Address": jp_address,
            "Telephone": phone,
            "Address_Alias": "",
            "Trans_Address": en_address,
            "Trans_Cn_Address": cn_address,
            "Fax": "",
            "City": city.split("市")[1] if "市" in city else city,  # 提取城市名
            "Zip_Code": zip_code,
            "rowkey": str(uuid.uuid4()),
            "State": prefecture,  # 使用完整的都道府县名
            "State_Full": prefecture,  # 可以用来存储完整的都道府县名
            "Expires": (datetime.now() + timedelta(days=random.randint(365, 1825))).strftime("%m/%Y"),
            "Credit_Card_Type": random.choice(CREDIT_CARD_TYPES),
            "Credit_Card_Number": ''.join(random.choices(string.digits, k=16)),
            "CVV2": ''.join(random.choices(string.digits, k=3)),
            "Full_Name": full_name,
            "Gender": random.choice(["Male", "Female"]),
            "Full_Name_Tran": full_name_romaji,
            "Title": random.choice(["Mr.", "Mrs.", "Ms.", "Dr."]),
            "Birthday": fake_en.date_of_birth(minimum_age=18, maximum_age=80).strftime("%m/%d/%Y"),
            "Username": fake_en.user_name(),
            "Password": ''.join(random.choices(string.ascii_letters + string.digits, k=12)),
            "Height": f"{height_ft} ({height_cm}cm)",
            "Weight": f"{weight_lbs}lbs ({weight_kg}kg)",
            "Temporary_mail": f"{''.join(random.choices(string.ascii_lowercase, k=10))}@{fake_en.domain_name()}",
            "System": random.choice(SYSTEMS),
            "GUID": str(uuid.uuid4()),
            "Blood_Type": random.choice(BLOOD_TYPES),
            "Browser_User_Agent": fake_en.user_agent(),
            "Educational_Background": random.choice(["High School", "Some college", "Bachelor's Degree", "Master's Degree"]),
            "Hair_Color": "",
            "Occupation": fake_en.job(),
            "Website": fake_en.domain_name(),
            "Security_Question": "What is your mother's maiden name?",
            "Security_Answer": ''.join(random.choices(string.ascii_lowercase, k=12)),
            "Social_Security_Number": "",
            "Employment_Status": random.choice(["Full-time", "Part-time work", "Self-employed", "Student"]),
            "Monthly_Salary": f"{random.randint(200,900):,},000Yen"
        }
        
        # 添加更多的职业选项
        occupations = [
            "社員", "公務員", "教師", "医師", "看護師", "エンジニア",
            "デイナー", "営業職", "事務職", "研究員", "弁護士", "会計士"
        ]
        
        # 添加更真实的教育背景
        education_backgrounds = [
            "高校卒業", "専門学校卒業", "短期大学卒業", "大学卒業", "大学院卒業"
        ]
        
        # 修改月收入范围使其更符合实际
        salary_ranges = {
            "会社員": (250, 450),
            "公務員": (280, 500),
            "医師": (450, 1200),
            "エンジニア": (300, 600),
            "事務職": (200, 350),
            "default": (200, 400)  # 添加默认范围
        }
        
        # 优化职业选择和薪资计算
        occupation = random.choice(occupations)
        salary_range = salary_ranges.get(occupation, salary_ranges["default"])
        monthly_salary = f"{random.randint(salary_range[0], salary_range[1]):,},000円"
        
        person_info.update({
            "Address": jp_address,
            "Trans_Address": en_address,
            "Trans_Cn_Address": cn_address,
            "Telephone": phone,
            "Occupation": occupation,
            "Educational_Background": random.choice(education_backgrounds),
            "Monthly_Salary": monthly_salary,
            "Employment_Status": random.choice([
                "正社員", "契約約社員", "パート・アルバイト", "派遣社員", "自営業"
            ])
        })
        
        # 更新姓名相关信息
        name_info = {
            "Last_Name": last_name,
            "First_Name": first_name,
            "Last_Name_Romaji": last_name_romaji,
            "First_Name_Romaji": first_name_romaji,
            "Name_Kanji": full_name,
            "Name_Romaji": full_name_romaji,
            "Name_Hiragana": hiragana_name,
            "Name_Katakana": katakana_name
        }
        person_info.update(name_info)
        
        return person_info
    except Exception as e:
        app.logger.error(f"生成信息时发生错误: {str(e)}")
        raise

# 添加 API 路由
@app.route('/api/generate', methods=['GET'])
@limiter.limit("10 per minute")
def generate_info():
    """
    API端点：生成并返回随机日本人信息
    返回: JSON格式的随机生成的日本人信息
    """
    try:
        japanese_info = generate_japanese_info()
        return jsonify(japanese_info), 200, {'Content-Type': 'application/json; charset=utf-8'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate/batch/<int:count>', methods=['GET'])
def generate_batch(count):
    """
    API端点：批量生成多条日本人信息
    参数:
        count: 需要生成的信息条数
    返回: JSON格式的多条随机生成的日本人信息
    """
    try:
        if count < 1 or count > 100:  # 限制批量生成的数量
            return jsonify({"error": "Count must be between 1 and 100"}), 400
            
        results = [generate_japanese_info() for _ in range(count)]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "Japanese Info Generator API is running",
        "endpoints": {
            "generate_single": "/api/generate",
            "generate_batch": "/api/generate/batch/<count>"
        }
    })

# 添加全局错误处理
@app.errorhandler(Exception)
def handle_error(error):
    status_code = 500
    if hasattr(error, 'code'):
        status_code = error.code
    return jsonify({
        "error": str(error),
        "status_code": status_code
    }), status_code

# 移除或修改日志配置（因为 Vercel 是无服务器环境）
# 可以用 Vercel 的日志系统替代
def setup_logging():
    app.logger.setLevel(logging.INFO)

# 移除主程序入口的环境判断
if __name__ == "__main__":
    app.run()
