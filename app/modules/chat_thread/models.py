from uuid import UUID, uuid4
from sqlalchemy import BigInteger, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID #起别名是因为导入了两个名字相同的模块UUID，不起别名的话后导入的会覆盖新导入的
from sqlalchemy.orm import Mapped, mapped_column
from app.common.models import Base, CreateAtMixin, UpdateAtMixin

class ChatThread(Base, CreateAtMixin, UpdateAtMixin):
    """客服会话"""

    __tablename__ = "chat_threads" #记得用魔法方法设置一个表名

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4, #注意是把uuid4这个函数传给SQL alchemy，不能传uuid4（），否则在创建类的时候uuid4（）会生成一个固定的uuid，导致以后的默认值是同一个uuid值
    )
    user_id: Mapped[int] = mapped_column(BigInteger)
    title: Mapped[str] = mapped_column(
        String(200),
        default="新会话",
        server_default="新会话",
    )