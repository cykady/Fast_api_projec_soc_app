from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import pytest
from app.oauth2 import create_access_token
from app.main import app
from app.config import settings
from app.database import get_db, Base
from app.schemas import Token
from app import models
#TEST DATABASE (url_test)
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_user}:{settings.database_password}@{settings.database_hostname}/{settings.database_name}_test"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency, override
@pytest.fixture(scope="function")
def session():
    Base.metadata.drop_all(bind=engine) #drop all tables
    Base.metadata.create_all(bind=engine) #create all tables
    db = TestSessionLocal() 
    try:
        yield db
    finally:
        db.close()

@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

@pytest.fixture()
def test_user2(client):
    user_data2 = {"email": "test2@email.com",
                 "password": "password123"}
    res = client.post("/users/", json=user_data2)

    assert res.status_code == 201

    new_user2 = res.json()
    new_user2['password'] = user_data2['password']
    return new_user2

@pytest.fixture()
def test_user(client):
    user_data = {"email": "test@email.com",
                 "password": "password123"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture()
def token(test_user):
    return create_access_token ({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture
def test_posts(test_user, session,test_user2):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "owner_id": test_user['id']
    }, {
        "title": "2nd title",
        "content": "2nd content",
        "owner_id": test_user['id']
    },
        {
        "title": "3rd title",
        "content": "3rd content",
        "owner_id": test_user['id']
    },
        {
        "title": "4rd title",
        "content": "4rd content",
        "owner_id": test_user2['id']
    }]
    
    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, posts_data)
    posts = list(post_map)
    
    session.add_all(posts)
    session.commit()
    posts = session.query(models.Post).all()
    return posts
    