"""压力测试数据准备脚本

批量创建测试用户、生成 JWT Token、预创建会话、准备问题池。
运行方式:
    cd backend
    $env:PYTHONPATH="."
    python ../tests/load/create_test_users.py
"""

import asyncio
import json
import os
import sys

# 将 backend 目录加入 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

from app.core.security import create_access_token, hash_password
from app.db.session import async_session_factory
from app.models.user import User
from app.models.conversation import Conversation

# ---- 配置 ----
TEST_USER_COUNT = 100
TEST_USER_PASSWORD = "test123456"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")


# ---- 问题池（100 条电商场景问题） ----
QUESTIONS = [
    # 商品信息类
    "这个手机电池容量是多少？",
    "这款笔记本电脑的屏幕分辨率是多少？",
    "这件衣服是什么材质的？",
    "这个产品的重量是多少？",
    "这款耳机的降噪效果怎么样？",
    "这个包包的尺寸是多少？",
    "这款手表防水吗？",
    "这个充电器支持快充吗？",
    "这款相机的像素是多少？",
    "这个水杯的容量是多大？",
    # 价格优惠类
    "这个商品有没有优惠券？",
    "现在的活动价格是多少？",
    "有没有限时折扣？",
    "会员价和普通价差多少？",
    "满减活动怎么参加？",
    "新用户有什么优惠吗？",
    "这个商品可以分期付款吗？",
    "能用花呗支付吗？",
    "有没有团购优惠？",
    "积分可以抵扣吗？",
    # 物流配送类
    "一般下单后几天能到？",
    "可以指定配送时间吗？",
    "偏远地区包邮吗？",
    "快递是顺丰还是圆通？",
    "可以加急发货吗？",
    "物流信息在哪里查看？",
    "收到货发现包装破损怎么办？",
    "可以改收货地址吗？",
    "海外能发货吗？",
    "自提点在哪些城市有？",
    # 退换货政策类
    "七天无理由退货有什么条件？",
    "退货的运费谁承担？",
    "换货的流程是什么？",
    "退货后多久能收到退款？",
    "拆封了还能退吗？",
    "衣服试穿不合适可以换吗？",
    "电子产品激活后还能退吗？",
    "赠品需要一起退回去吗？",
    "退货需要提供什么凭证？",
    "超过七天还能退换吗？",
    # 售后服务类
    "这个产品的保修期是多久？",
    "保修需要什么凭证？",
    "人为损坏在保修范围内吗？",
    "售后维修点在哪里？",
    "可以延保吗？",
    "配件损坏可以单买吗？",
    "保修期内维修免费吗？",
    "外地怎么申请售后？",
    "维修大概要多久？",
    "有没有以旧换新服务？",
    # 产品比较类
    "这款和另一款有什么区别？",
    "同价位的产品哪个性价比高？",
    "新款和老款有什么改进？",
    "这个品牌和其他品牌比有什么优势？",
    "适合学生用的有哪些？",
    "给老人买哪个合适？",
    "商务用途推荐哪款？",
    "性价比最高的是哪个？",
    "最畅销的是哪款？",
    "有没有类似的替代品？",
    # 使用方法类
    "这个产品怎么使用？",
    "有什么注意事项？",
    "需要自己安装吗？",
    "有没有使用教程视频？",
    "可以连接手机APP吗？",
    "支持哪些操作系统？",
    "需要什么配件配合使用？",
    "清洁保养怎么做？",
    "电池能持续多久？",
    "支持蓝牙连接吗？",
    # 库存与预售类
    "这款有现货吗？",
    "什么时候补货？",
    "可以预约购买吗？",
    "限量款还会补吗？",
    "预售商品什么时候发货？",
    "实体店有货吗？",
    "这个颜色还有吗？",
    "断码了还能调货吗？",
    "热门型号会溢价吗？",
    "可以预订下一批吗？",
    # 账号与服务类
    "如何修改收货地址？",
    "怎么注销账号？",
    "忘记密码怎么找回？",
    "如何绑定手机号？",
    "会员等级怎么提升？",
    "怎么查看历史订单？",
    "发票怎么开具？",
    "客服工作时间是几点？",
    "投诉建议在哪里提交？",
    "企业采购有优惠吗？",
]


async def create_test_users(count: int = TEST_USER_COUNT) -> list[dict]:
    """批量创建测试用户并返回用户信息列表"""
    users = []
    async with async_session_factory() as db:
        for i in range(1, count + 1):
            username = f"loadtest_{i:03d}"
            user = User(
                username=username,
                password_hash=hash_password(TEST_USER_PASSWORD),
                is_admin=False,
                is_active=True,
            )
            db.add(user)
        await db.commit()
        print(f"[OK] 已创建 {count} 个测试用户")

        # 重新查询获取 ID
        from sqlalchemy import select
        result = await db.execute(
            select(User).where(User.username.like("loadtest_%")).order_by(User.id)
        )
        db_users = result.scalars().all()

        for u in db_users:
            users.append({
                "username": u.username,
                "user_id": u.id,
                "is_admin": u.is_admin,
            })

    return users


def generate_tokens(users: list[dict]) -> list[dict]:
    """为每个用户生成 JWT token"""
    tokens = []
    for u in users:
        token = create_access_token({
            "sub": str(u["user_id"]),
            "username": u["username"],
        })
        tokens.append({
            "username": u["username"],
            "user_id": u["user_id"],
            "token": token,
        })
    print(f"[OK] 已生成 {len(tokens)} 个 JWT Token")
    return tokens


async def create_conversations(tokens: list[dict], per_user: int = 2) -> dict:
    """为每个用户预创建会话，返回 {user_id: [conv_id, ...]} 映射"""
    conversations = {}
    async with async_session_factory() as db:
        for t in tokens:
            conv_ids = []
            for j in range(per_user):
                conv = Conversation(
                    user_id=t["user_id"],
                    title=f"压测会话{j + 1}",
                )
                db.add(conv)
                await db.flush()
                conv_ids.append(conv.id)
            conversations[str(t["user_id"])] = conv_ids
        await db.commit()
    print(f"[OK] 已为 {len(tokens)} 个用户各创建 {per_user} 个会话")
    return conversations


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 50)
    print("  压力测试数据准备")
    print("=" * 50)

    # Step 1: 创建测试用户
    print("\n[Step 1/4] 创建测试用户...")
    users = await create_test_users(TEST_USER_COUNT)

    # Step 2: 生成 JWT Token
    print("\n[Step 2/4] 生成 JWT Token...")
    tokens = generate_tokens(users)

    # Step 3: 预创建会话
    print("\n[Step 3/4] 创建测试会话...")
    conversations = await create_conversations(tokens, per_user=2)

    # Step 4: 保存数据文件
    print("\n[Step 4/4] 保存数据文件...")

    # tokens.json
    tokens_path = os.path.join(OUTPUT_DIR, "loadtest_tokens.json")
    with open(tokens_path, "w", encoding="utf-8") as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)
    print(f"   → {tokens_path}")

    # questions.json
    questions_path = os.path.join(OUTPUT_DIR, "loadtest_questions.json")
    with open(questions_path, "w", encoding="utf-8") as f:
        json.dump(QUESTIONS, f, ensure_ascii=False, indent=2)
    print(f"   → {questions_path}")

    # conversations.json
    convs_path = os.path.join(OUTPUT_DIR, "loadtest_conversations.json")
    with open(convs_path, "w", encoding="utf-8") as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)
    print(f"   → {convs_path}")

    # 打印汇总信息
    print("\n" + "=" * 50)
    print("  [OK] 数据准备完成!")
    print("=" * 50)
    print(f"  测试用户数: {len(users)}")
    print(f"  JWT Token 数: {len(tokens)}")
    print(f"  会话数: {sum(len(v) for v in conversations.values())}")
    print(f"  问题池大小: {len(QUESTIONS)}")
    print(f"  测试用户密码: {TEST_USER_PASSWORD}")
    print(f"\n  数据目录: {OUTPUT_DIR}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
