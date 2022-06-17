from cocat.db import DB, mongodb_client

def test_mongo_running():
    assert mongodb_client.server_info() is not None, mongodb_client.server_info()