import logging
from langchain_core.tools import tool

# 配置日志，方便后续排查大模型传参错误
logger = logging.getLogger(__name__)

@tool
def query_order(order_id: str) -> str:
    """根据订单号查询订单状态"""
    try:
        # 模拟数据库查询
        orders = {
            "OR2024001": {"status": "已发货", "express": "顺丰", "eta": "2026-06-20"},
            "OR2024002": {"status": "配送中", "express": "中通", "eta": "2026-06-17"},
            "OR2024003": {"status": "已签收", "express": "圆通", "eta": "2026-06-15"},
            "OR2024004": {"status": "待发货", "express": None, "eta": None}
        }
        
        # 统一将 order_id 转为字符串，防止大模型传入数字类型导致查不到
        order = orders.get(str(order_id))
        
        if not order:
            return f"未找到订单 {order_id}，请核对订单号是否正确。"
            
        return (
            f"订单 {order_id} 状态: {order['status']} | "
            f"快递: {order['express'] or '暂无'} | "
            f"预计送达: {order['eta'] or '待确认'}"
        )
    except Exception as e:
        logger.error(f"查询订单异常: {e}, 订单号: {order_id}")
        return "系统繁忙，订单查询服务暂时不可用，请稍后再试。"


@tool
def query_inventory(product_id: str) -> str:
    """查询商品库存"""
    try:
        inventory = {
            "P001": {"name": "智能手表", "stock": 50},
            "P002": {"name": "蓝牙耳机", "stock": 0},
            "P003": {"name": "充电宝", "stock": 120}
        }
        
        product = inventory.get(str(product_id))
        if not product:
            return f"未找到商品 {product_id}，请核对商品编号。"
            
        stock_status = "充足" if product['stock'] > 0 else "缺货"
        return f"商品 {product['name']} 当前库存: {product['stock']}件 ({stock_status})"
        
    except Exception as e:
        logger.error(f"查询库存异常: {e}, 商品ID: {product_id}")
        return "系统繁忙，库存查询服务暂时不可用。"


@tool
def return_policy() -> str:
    """查询退换货规则"""
    return (
        "【退换货规则】\n"
        "1. 商品签收后7天内支持无理由退货\n"
        "2. 质量问题30天内免费换货\n"
        "3. 退货需保证商品完好且不影响二次销售\n"
        "4. 非质量问题退货运费由买家承担\n"
        "5. 如需申请，请联系客服 400-888-0000"
    )


@tool
def submit_refund(order_id: str, amount: float, reason: str) -> str:
    """提交退款申请（高风险操作，需要用户确认后执行）"""
    try:
        # 核心优化：强制类型转换与业务校验
        amount = float(amount)
        if amount <= 0:
            return "退款金额必须大于0，请重新确认退款金额。"
            
        # 模拟业务逻辑
        result = (
            f"✅ 退款申请已提交\n"
            f"订单号：{order_id}\n"
            f"退款金额：{amount:.2f}元\n"
            f"退款原因：{reason}\n"
            f"当前状态:审核中(预计1-3个工作日原路退回)"
        )
        logger.info(f"退款申请成功: 订单{order_id}, 金额{amount}")
        return result
        
    except ValueError:
        # 捕获大模型传错金额格式（比如传了中文数字）
        logger.warning(f"退款金额格式错误: {amount}")
        return "退款金额格式不正确，请提供准确的数字金额（如：299.00）。"
    except Exception as e:
        logger.error(f"提交退款异常: {e}")
        return "系统繁忙，退款申请提交失败，请联系人工客服处理。"