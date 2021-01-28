def test_home_page_view(client):
    assert client.get("/").status_code == 200
