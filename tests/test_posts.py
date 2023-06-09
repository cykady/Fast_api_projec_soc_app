from app import schemas
import pytest

#ALL POSTS TESTS
def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")
    def validate(post):
        return schemas.PostOut(**post)
    posts_map = map(validate, res.json())
    #posts_list = list(posts_map)
    assert len(res.json()) == len(test_posts)
    assert res.status_code == 200

def test_unauthorized_get_all_posts(client,test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401

#ONE POST TESTS
def test_get_one_post_not_exist(authorized_client):
    res = authorized_client.get("/posts/100")
    assert res.status_code == 404

def test_unauthorized_get_one_post(client,test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401

def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    post = schemas.Post(**res.json())
    assert res.status_code == 200
    assert post.id == test_posts[0].id
    assert post.content == test_posts[0].content
    assert post.title == test_posts[0].title

#CREATE POST TESTS
@pytest.mark.parametrize("title, content ,published",[
    ("first test title", "first test content", True),
    ("second test title", "second test content", False),
    ("thirt test title", "thirt test content", False,)
])
def test_create_post(authorized_client, test_user, test_posts, title, content, published):
    res = authorized_client.post(
        "/posts/", json={"title": title, "content": content, "published": published})
    post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert post.title == title
    assert post.content == content
    assert post.published == published
    assert post.owner_id == test_user['id']

@pytest.mark.parametrize("title, content ,published",[
    ("first test title", "first test content", True),
    ("second test title", "second test content", False),
    ("thirt test title", "thirt test content", False,)
])
def test_create_post_published_off(authorized_client, test_user, title, content, published):
    res = authorized_client.post(
        "/posts/", json={"title": title, "content": content})
    post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert post.title == title
    assert post.content == content
    assert post.published == True
    assert post.owner_id == test_user['id']

#DELETE POST TESTS
def test_delete_unauthorized_post(client, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401
def test_try_delete_not_exist_post(authorized_client):
    res = authorized_client.delete("/posts/100")
    assert res.status_code == 404
def test_delete_post_other_user(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert res.status_code == 403
def test_delete_post(authorized_client, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 204

#UPDATE POST TESTS
def test_update_unauthorized_post(client, test_posts):
    res = client.put(f"/posts/{test_posts[0].id}", json={"title": "updated title","content": "updated content"})
    assert res.status_code == 401
def test_try_update_not_exist_post(authorized_client,test_posts):
    res = authorized_client.put("/posts/100", json={"title": "updated title","content": "updated content","id": test_posts[0].id})
    assert res.status_code == 404
def test_update_post_other_user(authorized_client, test_posts):
    res = authorized_client.put(f"/posts/{test_posts[3].id}", json={"title": "updated title","content": "updated content","id":test_posts[3].id})
    assert res.status_code == 403
def test_update_post(authorized_client, test_posts):
    res = authorized_client.put(f"/posts/{test_posts[0].id}", json={"title": "updated title","content": "updated content","id":test_posts[0].id})
    post = schemas.Post(**res.json())
    assert res.status_code == 202
    assert post.title == "updated title"
    assert post.content == "updated content"


#pytest tests\test_posts.py -v -s