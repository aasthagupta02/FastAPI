from typing import Optional
from fastapi import Body, FastAPI, Response,status,HTTPException,Depends
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from random import randrange
from . import models
from .database import engine,get_db
import time
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

#Class to have format of posts data
class Post(BaseModel):
    title: str
    content: str
    published: bool = True  #this was default value
    rating: Optional[int] = None #this is option value

while True:
    try:
   # Connect to an existing database
        conn = psycopg2.connect(host='localhost', database ='fastapi',user='postgres', password = 'admin', cursor_factory=RealDictCursor)
    # Open a cursor to perform database operations
        cur = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
         print("Connecting to database failed")
         print("Error: ", error)

#array of dictionary to retrieve all the posts, currently hardcoded data
my_posts=[{"title":"Nokia","content":"Old mobile company","id":1,"published":False,"rating":"3"},
              {"title":"Apple","content":"Everyones favourite","id":2,"published":True,"rating":"5"}]
print(my_posts) 

def find_post(id):   #this is how developer debug, taught by Neeraj , he used print statement
    response=""
    for p in my_posts:
        print(p)        
        if p['id']==id:
            print("came into if condition")
            response=p
    return response 

def find_post_index(id):
    for i, p in enumerate(my_posts):
     if p['id']==id:
       return i    

@app.get("/")
def root():
    return {"message":"Welcome to my API!!"}

# @app.get("/sqlalchemy")
# def test_posts(db: Session = Depends(get_db)):
#     posts = db.query(models.Post).all() 
#     return{"data": posts}
    

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cur.execute("""SELECT * FROM posts""")
    # posts=cur.fetchall()
    # print ("Posts",posts)
    posts = db.query(models.Post).all() 
    return {"data":posts} #get all the posts

@app.post("/posts",status_code=status.HTTP_201_CREATED)  #Check the decorator used for status code
def create_posts(post: Post, db: Session = Depends(get_db)):
    #  cur.execute("""INSERT INTO posts (title, content, published) VALUES(%s,%s,%s) RETURNING * """,(post.title,post.content,post.published))
    #  new_posts=cur.fetchone()
    #  conn.commit()
     new_posts = models.Post(title=post.title,content=post.content, published = post.published)
     db.add(new_posts)
     db.commit()
     db.refresh(new_posts)
     return {"data": new_posts}

@app.get("/posts/latest")
def get_latest_posts():
    posts=my_posts[len(my_posts)-1]
    return {"details": posts}
    
@app.get("/posts/{id}") 
def get_post(id: int, db: Session = Depends(get_db)):
#    cur.execute("""SELECT * from posts where id = %s""", (str(id)))
#    post = cur.fetchone()
   post = db.query(models.Post).filter(models.Post.id == id)
   print(post)
   if not post:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f"post with id: {id} was not found")
    #    response.status_code = status.HTTP_404_NOT_FOUND    
    #    return{'message': f"post with id: {id} was not found" }   
   return {"detail":post}

@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id: int):
    cur.execute("""DELETE FROM posts where id = %s RETURNING *""",(str(id)))
    deleted_post= cur.fetchone()
    conn.commit()
    if deleted_post == None:
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f"post with id: {id} does not exists") 
       
    return{Response(status_code=status.HTTP_204_NO_CONTENT)} #here in delete, 
#We cannot pass message here, this is the standard of 204 status code and the FastAPI

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
   cur.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",(post.title,post.content, post.published, (str(id))))
   updated_post = cur.fetchone()
   conn.commit()
   if updated_post == None:
     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail = f"post with id: {id} does not exists")    

   return {'data': updated_post}



   

