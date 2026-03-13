"""
物品比对模块
用于比对入场和离场物品，检测异常
"""
from typing import List, Dict, Tuple


class ItemComparator:
    """物品比对器"""
    
    @staticmethod
    def compare(entry_items: List[Dict], exit_items: List[Dict]) -> Tuple[str, List[Dict]]:
        """
        比对入场和离场物品
        
        Args:
            entry_items: 入场物品列表
            exit_items: 离场物品列表
            
        Returns:
            (状态, 异常列表)
            状态: "normal" 或 "anomaly"
            异常列表: 包含异常信息的字典列表
        """
        anomalies = []
        
        # 创建物品字典便于比对
        entry_dict = {item["name"]: item for item in entry_items}
        exit_dict = {item["name"]: item for item in exit_items}
        
        # 1. 检查多带物品（离场有但入场没有）
        for name, item in exit_dict.items():
            if name not in entry_dict:
                anomalies.append({
                    "type": "extra",
                    "title": "检测到多带物品",
                    "description": f'离场时发现"{name}"（{item["quantity"]}个），入场记录中不存在该物品',
                    "item_name": name,
                    "quantity": item["quantity"]
                })
        
        # 2. 检查少带物品（入场有但离场没有）
        for name, item in entry_dict.items():
            if name not in exit_dict:
                anomalies.append({
                    "type": "missing",
                    "title": "物品缺失",
                    "description": f'入场物品"{name}"（{item["quantity"]}个）在离场时未检测到',
                    "item_name": name,
                    "quantity": item["quantity"]
                })
        
        # 3. 检查数量异常（同一物品数量不一致）
        for name in set(entry_dict.keys()) & set(exit_dict.keys()):
            entry_qty = entry_dict[name]["quantity"]
            exit_qty = exit_dict[name]["quantity"]
            
            if entry_qty != exit_qty:
                anomalies.append({
                    "type": "quantity",
                    "title": "数量异常",
                    "description": f'物品"{name}"数量不一致：入场{entry_qty}个，离场{exit_qty}个',
                    "item_name": name,
                    "entry_quantity": entry_qty,
                    "exit_quantity": exit_qty
                })
        
        # 4. 检查重量异常（可选）
        entry_total_weight = sum(item.get("weight", 0) for item in entry_items)
        exit_total_weight = sum(item.get("weight", 0) for item in exit_items)
        
        weight_diff = abs(entry_total_weight - exit_total_weight)
        if weight_diff > 0.5:  # 重量差异超过 0.5kg
            anomalies.append({
                "type": "weight",
                "title": "重量异常",
                "description": f'总重量不一致：入场{entry_total_weight:.2f}kg，离场{exit_total_weight:.2f}kg',
                "entry_weight": entry_total_weight,
                "exit_weight": exit_total_weight,
                "weight_diff": weight_diff
            })
        
        # 确定状态
        status = "normal" if len(anomalies) == 0 else "anomaly"
        
        return status, anomalies
    
    @staticmethod
    def get_anomaly_summary(anomalies: List[Dict]) -> str:
        """获取异常摘要"""
        if not anomalies:
            return "正常"
        
        types = {}
        for anomaly in anomalies:
            atype = anomaly["type"]
            types[atype] = types.get(atype, 0) + 1
        
        summary_parts = []
        if types.get("extra"):
            summary_parts.append(f"多带{types['extra']}件物品")
        if types.get("missing"):
            summary_parts.append(f"缺失{types['missing']}件物品")
        if types.get("quantity"):
            summary_parts.append(f"{types['quantity']}件物品数量异常")
        if types.get("weight"):
            summary_parts.append("重量异常")
        
        return "、".join(summary_parts) if summary_parts else "异常"
