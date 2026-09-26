from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.product.models import Product
from app.modules.product.repository import ProductRepository
from decimal import Decimal

# 产品业务层
class ProductService:

    def __init__(self, session:AsyncSession):
        self.session = session
        self.repository = ProductRepository(session)

    async def list_product(self, category) -> list[Product]:
        """
        根据保险产品分类来查询产品列表
        :param category: 产品分类
        :return: 产品列表
        """
        return await self.repository.find_by_category(category)

    async def list_candidates(
        self,
        categories: list[str],
        premium_min: Decimal | None,
        limit_per_category: int,
    ) -> list[Product]:
        candidate_products: list[Product] = []

        for category in dict.fromkeys(categories):
            products = await self.repository.find_limited_by_category(
                category=category,
                premium_min=premium_min,
                limit=limit_per_category,
            )
            candidate_products.extend(products)

        return candidate_products