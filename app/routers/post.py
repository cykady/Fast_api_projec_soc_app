from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
from app.oauth2 import get_current_user
from sqlalchemy import func

router = APIRouter(prefix='/posts', tags=['Posts'])

### READ ALL POSTS ###
@router.get('/',response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db),
              current_user: int = Depends(get_current_user),
              limit: int = 3,skip: int = 0,
              search: Optional[str] = ""
              ):

    post= db.query(
        models.Post, func.count(models.Votes.post_id).label("votes")).join(
        models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(
        models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return post

### CREATE NEW POST ###
@router.post('/', status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
def create_post(post: schemas.PostCreate,
                db: Session = Depends(get_db),
                current_user: int = Depends(get_current_user)):
    new_post = models.Post(owner_id = current_user.id,
                            **post.dict())
   #CREATE COMIT AND REFRESH 
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

### READ LAST POST ###
@router.get('/last',
            response_model=schemas.Post)
def read_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).order_by(models.Post.id.desc()).first()
    return posts

### READ POST BY ID ##
@router.get('/{id}',
            response_model=schemas.Post)
def get_post(id: int,
             db: Session = Depends(get_db),
             current_user: int = Depends(get_current_user)):
    my_posts = db.query(models.Post).filter(models.Post.id == id).first()

    #CHECK IF POST EXISTS
    if not my_posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Post not found")
    
    return my_posts

### DELETE POST ###
@router.delete('/{id}',
               status_code=status.HTTP_204_NO_CONTENT,)
def delete(id: int,
           db: Session = Depends(get_db),
           current_user: int = Depends(get_current_user)):

    #FIND POST BY ID
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    #CHECK IF POST EXISTS
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Post not found")
    
    #CHECK IF OWNER IS THE CURRENT USER
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not the owner of this post")
    #DELETE POST
    post_query.delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

### UPDATE POST ###
@router.put('/{id}',status_code=status.HTTP_202_ACCEPTED,response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db),current_user: int = Depends(get_current_user)):

    #FIND POST BY ID AND TAKE FIRST RESULT
    my_posts_query = db.query(models.Post).filter(models.Post.id == id)
    my_post = my_posts_query.first()
    #CHECK IF POST EXISTS
    if my_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,)
    
    #CHECK IF OWNER IS THE CURRENT USER
    if my_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="You are not the owner of this post")
    #UPDATE POST
    my_posts_query.update(post.dict(), synchronize_session=False)
    db.commit()

    return my_posts_query.first()