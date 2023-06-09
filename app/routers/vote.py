from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session
from app.oauth2 import get_current_user

#CREATE ROUTER
router = APIRouter(prefix='/vote', tags=['Vote'])

###VOTE POST###
@router.post('/',status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote,
         db: Session = Depends(get_db),
         current_user: int = Depends(get_current_user)
         ):
    
    #CHECK IF POST EXISTS
    post_query = db.query(models.Post).filter(models.Post.id == vote.post_id)
    post = post_query.first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post doesn't exist")
    
    #CHECK IF USER ALREADY VOTED
    vote_query=db.query(models.Votes).filter(models.Votes.post_id == vote.post_id, models.Votes.user_id == current_user.id)
    _vote = vote_query.first()
    if (vote.dir == 1):
        #IF USER ALREADY VOTED
        if _vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="You already voted this post")
        #IF NOT VOTED
        new_vote = models.Votes(post_id=vote.post_id,
                                user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Vote successful"}
    else:
        #UNVOTE POST THAT USER ALREADY VOTED
        if not _vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="You can't unvote a post you didn't vote")
        else:
            #UNVOTE
            vote_query.delete(synchronize_session=False)
            db.commit()
            return {"message": "Vote deleted"}