from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from app.modules.product.models import Product

# 产品数据表的数据层
class ProductRepository:

    def __init__(self, session:AsyncSession):
        self.session = session

    async def find_by_category(self, category) -> list[Product]:
        """
        根据分类名称去数据库中查询对应的数据列表
        :param category: 分类名称
        :return: 产品列表
        """
        # select * from products where status = 'active';
        # select * from products where status = 'active' and category = category;

        # 0.准备查询条件
        conditions = [Product.status == 'active']
        if category:
            conditions.append(Product.category == category)

        # [Product.status == 'active', Product.category == category]

        # 1.将SQL语句翻译成Python代码
        sql = select(Product).where(*conditions)

        # 2.执行SQL语句
        exec_result = await self.session.execute(sql)

        # 3.解析最终的结果
        return exec_result.scalars().all()

    async def find_limited_by_category(
            self,
            category: str,
            premium_min: Decimal | None,
            limit: int,
    ) -> list[Product]:
        conditions = [
            Product.status == "active",
            Product.category == category,
        ]
        if premium_min is not None:
            conditions.append(Product.min_premium < premium_min)

        products = await self.session.scalars(
            select(Product)
            .where(*conditions)
            .order_by(
                Product.min_premium.asc().nullslast(),
                Product.id.asc(),
            )
            .limit(limit)
        )
        return products.all()