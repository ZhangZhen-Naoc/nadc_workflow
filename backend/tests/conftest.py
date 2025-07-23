import pytest

from app import app, db


@pytest.fixture(scope="function")
def app_context():
    """推送Flask app context的fixture"""
    ctx = app.app_context()
    ctx.push()
    db.drop_all()
    db.create_all()
    yield
    ctx.pop()
