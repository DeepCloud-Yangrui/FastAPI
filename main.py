from datetime import datetime
from fastapi import FastAPI, Path, Query,Depends        # 2.导入depends
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse,FileResponse
import os
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func, Float,select
from sqlalchemy.testing import in_

app=FastAPI()


# 1、创建异步引擎
ASYNC_DATABASE_URL = "mysql+aiomysql://root:yr20020914@100.105.90.7:3306/fastAPI_first?charset=utf8mb4"
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,  # 可选，输出SQL日志用的
    pool_size=10,   # 设置连接池活跃的连接数
    max_overflow=20,    # 允许额外的连接数
)

# 2、定义模型类： 基类＋表对应的模型类
# 基类：创建时间、更新时间
# 书籍表：id、书名、作者、价格、出版社
class Base(DeclarativeBase):
    create_time:Mapped[datetime] = mapped_column(DateTime,server_default=func.now(),comment="创建时间")
    update_time:Mapped[datetime] = mapped_column(DateTime,server_default=func.now(),onupdate=func.now(),comment="更新时间")
class Book(Base):
    __tablename__ = "book"

    id:Mapped[int] = mapped_column(Integer,primary_key=True,comment="书籍id")
    bookname:Mapped[str] = mapped_column(String(255),comment="书名")
    author:Mapped[str] = mapped_column(String(255),comment="作者")
    price:Mapped[float] = mapped_column(Float,comment="价格")
    publisher:Mapped[str] = mapped_column(String(255),comment="出版社")

# 3、建表：定义函数建表  -> FastAPI启动的时候调用建表的函数
async def create_table():
    # 获取异步引擎，创建事务列表
    async with async_engine.begin() as conn:
        # 创建表
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
    await create_table()

@app.get("/")
async def root():
    return {"message": "fastapi_first"}


# 需求：查询功能的接口  查询图书 -> 依赖注入：创建依赖项获取数据库会话，然后Depends注入路由处理函数
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,          # 绑定数据库引擎
    class_=AsyncSession,        # 指定会话类型
    expire_on_commit=False    # 提交后会话不过期，不会重新查询数据库
)

# 依赖项
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session       # 返回数据库会话给路由函数
            await session.commit()      # 提交事务
        except Exception:
            await session.rollback()    # 有异常，回滚，保持数据一致性
            raise           # 这里为什么不用raise e？

# 路由处理函数

class BookUpdate(BaseModel):
    # id:int
    bookname:str
    author:str
    price:float
    publisher:str

# 需求：实现模糊查询
# @app.post("/book/get_book_price")
# async def add_book(
#         book:BookBase,      # 请求体参数
#         db:AsyncSession = Depends(get_db)
# ):
#     # ORM对象
#     book_obj = Book(**book.__dict__)
#     db.add(book_obj)
#     await db.commit()
#     return {"message": "添加成功"}


# 需求：修改图书的信息
@app.put("/book/update_book/{book_id}")
async def update_book(
        book_id:int,
        new_data:BookUpdate,
        db:AsyncSession = Depends(get_db)
):
    # 1. 根据id查询到图书对象
    db_book = await db.get(Book, book_id)
    if not db_book:
        raise HTTPException(status_code=404, detail="图书不存在")

    # 2. 修改图书信息
    db_book.bookname = new_data.bookname
    db_book.author = new_data.author
    db_book.price = new_data.price
    db_book.publisher = new_data.publisher

    # 3提交到数据库
    await db.commit()
    return db_book


# 需求：删除指定书籍
@app.delete("/book/delete_book/{book_id}")
async def delete_book(
        book_id:int,
        db:AsyncSession = Depends(get_db)
):
    # 1. 根据id查询到图书对象
    target_book = await db.get(Book, book_id)
    if target_book is None:
        raise HTTPException(status_code=404, detail="图书不存在")

    # 2. 删除图书对象
    await db.delete(target_book)
    # 3. 提交到数据库
    await db.commit()

    return {"message": "删除成功"}