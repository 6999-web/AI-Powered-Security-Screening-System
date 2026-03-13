#!/usr/bin/env python3
"""
智能安检系统 - 完整功能测试脚本
"""

import requests
import json
import time
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8888"
API_BASE = f"{BASE_URL}/api"

# 测试数据
TEST_ID_CARD = "123456789012345678"
TEST_ID_CARD_2 = "987654321098765432"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, status, message=""):
    """打印测试结果"""
    if status:
        print(f"{Colors.GREEN}✅ {name}{Colors.END}")
    else:
        print(f"{Colors.RED}❌ {name}{Colors.END}")
    if message:
        print(f"   {message}")

def print_section(title):
    """打印测试章节"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Colors.END}\n")

def test_api_health():
    """测试 API 健康状态"""
    print_section("1. API 健康检查")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test("API 根端点", True, f"状态: {data.get('status')}")
            return True
        else:
            print_test("API 根端点", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("API 根端点", False, str(e))
        return False

def test_verify_identity():
    """测试身份验证"""
    print_section("2. 身份验证功能")
    
    try:
        # 测试用户 1
        data = {"idCard": TEST_ID_CARD}
        response = requests.post(f"{API_BASE}/verify-identity", data=data, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            user_id = result.get("userId")
            print_test("身份验证 - 用户1", True, f"用户ID: {user_id}")
            
            # 测试用户 2
            data = {"idCard": TEST_ID_CARD_2}
            response = requests.post(f"{API_BASE}/verify-identity", data=data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                user_id_2 = result.get("userId")
                print_test("身份验证 - 用户2", True, f"用户ID: {user_id_2}")
                return True
            else:
                print_test("身份验证 - 用户2", False, f"状态码: {response.status_code}")
                return False
        else:
            print_test("身份验证 - 用户1", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("身份验证", False, str(e))
        return False

def test_entry_check():
    """测试入场安检"""
    print_section("3. 入场安检功能")
    
    try:
        # 创建测试图片
        with open("test_image.jpg", "rb") as f:
            image_data = f.read()
        
        # 如果没有测试图片，创建一个简单的
        if not image_data:
            # 创建一个最小的 JPEG 文件
            jpeg_header = bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46])
            with open("test_image.jpg", "wb") as f:
                f.write(jpeg_header)
            with open("test_image.jpg", "rb") as f:
                image_data = f.read()
        
        # 生成用户 ID
        user_id = f"USER_{TEST_ID_CARD[-6:]}"
        
        # 上传入场图片
        files = {"image": ("test.jpg", image_data, "image/jpeg")}
        data = {"user_id": user_id, "channel_no": 1}
        
        response = requests.post(f"{API_BASE}/entry", files=files, data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            record_id = result.get("record_id")
            items = result.get("items", [])
            total_count = result.get("total_count", 0)
            
            print_test("入场安检", True, f"记录ID: {record_id}")
            print(f"   识别物品数: {len(items)}")
            print(f"   总件数: {total_count}")
            
            if items:
                print("   识别的物品:")
                for item in items[:3]:  # 只显示前3个
                    print(f"     - {item.get('name')} ({item.get('quantity')}个)")
            
            return True, user_id, record_id
        else:
            print_test("入场安检", False, f"状态码: {response.status_code}")
            try:
                print(f"   错误: {response.json()}")
            except:
                print(f"   响应: {response.text}")
            return False, None, None
    except Exception as e:
        print_test("入场安检", False, str(e))
        return False, None, None

def test_exit_check(user_id):
    """测试离场安检"""
    print_section("4. 离场安检功能")
    
    try:
        # 创建测试图片
        with open("test_image.jpg", "rb") as f:
            image_data = f.read()
        
        # 上传离场图片
        files = {"image": ("test.jpg", image_data, "image/jpeg")}
        data = {"user_id": user_id, "channel_no": 1}
        
        response = requests.post(f"{API_BASE}/exit", files=files, data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            record_id = result.get("record_id")
            items = result.get("items", [])
            status = result.get("comparison_status")
            anomalies = result.get("anomalies", [])
            
            print_test("离场安检", True, f"记录ID: {record_id}")
            print(f"   比对状态: {status}")
            print(f"   识别物品数: {len(items)}")
            
            if anomalies:
                print(f"   检测到异常: {len(anomalies)}")
                for anomaly in anomalies[:2]:
                    print(f"     - {anomaly.get('description', '未知异常')}")
            else:
                print("   无异常")
            
            return True
        else:
            print_test("离场安检", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("离场安检", False, str(e))
        return False

def test_statistics():
    """测试统计数据"""
    print_section("5. 统计数据功能")
    
    try:
        response = requests.get(f"{API_BASE}/statistics", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print_test("获取统计数据", True)
            print(f"   总入场: {result.get('total_entry', 0)}")
            print(f"   总离场: {result.get('total_exit', 0)}")
            print(f"   总异常: {result.get('total_alerts', 0)}")
            print(f"   当前在场: {result.get('current_inside', 0)}")
            return True
        else:
            print_test("获取统计数据", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("获取统计数据", False, str(e))
        return False

def test_recent_records():
    """测试最近记录"""
    print_section("6. 最近记录功能")
    
    try:
        response = requests.get(f"{API_BASE}/recent-records?limit=5", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            records = result.get("records", [])
            print_test("获取最近记录", True, f"记录数: {len(records)}")
            
            if records:
                print("   最近的记录:")
                for record in records[:3]:
                    print(f"     - {record.get('type')}: {record.get('user_id')} ({record.get('total_count')}件)")
            
            return True
        else:
            print_test("获取最近记录", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("获取最近记录", False, str(e))
        return False

def test_anomalies():
    """测试异常记录"""
    print_section("7. 异常记录功能")
    
    try:
        response = requests.get(f"{API_BASE}/anomalies?limit=10", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            anomalies = result.get("anomalies", [])
            print_test("获取异常记录", True, f"异常数: {len(anomalies)}")
            
            if anomalies:
                print("   最近的异常:")
                for anomaly in anomalies[:3]:
                    print(f"     - {anomaly.get('alert_type')}: {anomaly.get('detail', '未知')}")
            else:
                print("   暂无异常记录")
            
            return True
        else:
            print_test("获取异常记录", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("获取异常记录", False, str(e))
        return False

def test_channels():
    """测试通道信息"""
    print_section("8. 通道信息功能")
    
    try:
        response = requests.get(f"{API_BASE}/channels", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            channels = result.get("channels", [])
            print_test("获取通道信息", True, f"通道数: {len(channels)}")
            
            if channels:
                print("   通道信息:")
                for channel in channels:
                    status = "活跃" if channel.get("status") == "active" else "空闲"
                    print(f"     - {channel.get('name')}: {status}")
            
            return True
        else:
            print_test("获取通道信息", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("获取通道信息", False, str(e))
        return False

def test_compare():
    """测试比对结果"""
    print_section("9. 比对结果功能")
    
    try:
        user_id = f"USER_{TEST_ID_CARD[-6:]}"
        response = requests.get(f"{API_BASE}/compare/{user_id}", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print_test("获取比对结果", True)
            print(f"   用户ID: {result.get('user_id')}")
            print(f"   入场物品数: {len(result.get('entry_items', []))}")
            return True
        elif response.status_code == 404:
            print_test("获取比对结果", True, "用户未入场（预期行为）")
            return True
        else:
            print_test("获取比对结果", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("获取比对结果", False, str(e))
        return False

def main():
    """主测试函数"""
    print(f"\n{Colors.BLUE}")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  智能安检系统 - 完整功能测试".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    print(f"{Colors.END}\n")
    
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 地址: {BASE_URL}\n")
    
    # 测试结果统计
    results = []
    
    # 1. API 健康检查
    results.append(("API 健康检查", test_api_health()))
    
    # 2. 身份验证
    results.append(("身份验证", test_verify_identity()))
    
    # 3. 入场安检
    entry_result, user_id, record_id = test_entry_check()
    results.append(("入场安检", entry_result))
    
    # 4. 离场安检
    if user_id:
        results.append(("离场安检", test_exit_check(user_id)))
    
    # 5. 统计数据
    results.append(("统计数据", test_statistics()))
    
    # 6. 最近记录
    results.append(("最近记录", test_recent_records()))
    
    # 7. 异常记录
    results.append(("异常记录", test_anomalies()))
    
    # 8. 通道信息
    results.append(("通道信息", test_channels()))
    
    # 9. 比对结果
    results.append(("比对结果", test_compare()))
    
    # 打印总结
    print_section("测试总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"总测试数: {total}")
    print(f"通过: {Colors.GREEN}{passed}{Colors.END}")
    print(f"失败: {Colors.RED}{total - passed}{Colors.END}")
    print(f"成功率: {Colors.BLUE}{(passed/total)*100:.1f}%{Colors.END}\n")
    
    # 详细结果
    print("详细结果:")
    for name, result in results:
        status = f"{Colors.GREEN}✅ 通过{Colors.END}" if result else f"{Colors.RED}❌ 失败{Colors.END}"
        print(f"  {name}: {status}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 所有功能测试通过！系统已准备好投入使用。{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}⚠️ 部分功能测试失败，请检查日志。{Colors.END}\n")
        return 1

if __name__ == "__main__":
    exit(main())
