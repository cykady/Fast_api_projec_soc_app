from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas,models,ustils
from app.oauth2 import create_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=['Authentication'])

#LOGIN Authentication
@router.post('/login',status_code=status.HTTP_200_OK)
def login(user_credencial: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credencial.username).first()
    
    #CHECK IF USER EXIST
    if not user:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User not found")
    if not ustils.verify(user_credencial.password,user.password):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Incorrect password")
    
    #GENERATE TOKEN AND RETURN
    access_token = create_access_token(data={'user_id':user.id})
    return {"access_token":access_token,"token_type":"bearer"}