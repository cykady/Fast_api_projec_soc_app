from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import ustils, models, schemas, database
from sqlalchemy.orm import Session

router = APIRouter(prefix='/users', tags=['Users'])

#CREATE NEW USER
@router.post('/', status_code=status.HTTP_201_CREATED,response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate ,db: Session = Depends(database.get_db)):
    #hash the passwrod - user.password
    hashed_password = ustils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
     
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

#RETRIEVE USER INFORMATION
@router.get('/{user_id}',response_model=schemas.UserOut)
def read_user(user_id: int,db: Session = Depends(database.get_db)):
    my_users = db.query(models.User).filter(models.User.id == user_id).first()
    if not my_users:
        raise HTTPException(status_code=404, detail="User not found")
    return my_users