from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse,FileResponse
import os
from fastapi import HTTPException
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World666"}


#
# # 自己写一个路由
# @app.get("/hello")
# async def hello_fastapi():
#     return {"msg": "hello,fastapi"}
#
#
# @app.get("/user/hello")
# async def say_my_learning():
#     return {"msg": "我正在学习fastapi"}
#
#
# @app.get("/book/{id}")
# async def get_book(id: int = Path(..., gt=0, lt=101, description="书籍id，取值范围1-100")):
#     return {"id": id, "title": f"这是第{id}本书"}
#
#
# # @app.get("/hello/{name}")
# # async def say_hello(name: str):
# #     return {"message": f"Hello {name}"}
#
#
# # 自己尝试写一个作者名字的接口
# @app.get("/author/{name}")
# async def get_author(name: str = Path(..., min_length=2, max_length=10)):
#     return {"msg": f"这是{name}的信息"}
#
#
# @app.get("/new/news_list")
# async def get_new(
#         skip: int=Query(0,description="跳过的记录数",lt=100),
#         limit: int = Query(10, description="每页显示的记录数", gt=0, lt=100)
# ):
#     return {"msg":{
#         "skip":skip,
#         "limit":limit
#     }}

# 请求体参数的练习

# 注册：用户名和密码
# class User(BaseModel):
#     username: str = Field(default="admin", min_length=2, max_length=10, description="用户名，长度要求2-10")
#     password: str = Field(default="1234", min_length=6, max_length=20, description="密码，长度要求6-20")
#
#
# @app.post("/register")
# async def register(user: User):
#     return user


# 接口 -> 响应html代码
# @app.get("/html",response_class=HTMLResponse)
# async def get_html():
#     return "<h1>hello world</h1>"           # 注意，html代码要以字符串的形式出现


# 接口 -> 返回一张照片
@app.get("/files")
async def get_image():
    file_path='./files/image1.png'
    return FileResponse(file_path)

# practice 自定义响应数据格式
# 需求：新闻接口 -> 响应数据格式：id、title、content
class News(BaseModel):
    ids:int
    title:str
    contents:str

# @app.get("/news/{ids}",response_model=News)
# async def get_news(ids:int):
#     return {
#         "id":ids,
#         "title":f"这是第{ids}本书",
#         "contents":"这是一本好书"
#     }

# 异常响应处理
# 按照id查询新闻
@app.get("/news/{id}")
async def get_news(id:int):
    id_list=[1,2,3,4,5,6]
    if id not in id_list:
        raise HTTPException(status_code=404,detail="您查找的新闻不存在")
    return {
        "id":id
    }


    return
