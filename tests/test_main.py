import os
import sys
import asyncio
import pytest
from httpx import AsyncClient
from fastapi import status

from app.main import app
from app.database import Base, engine


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
async def prepare_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(prepare_db):
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_and_get_graph(client):
    payload = {
        'nodes': [{'name': 'A'}, {'name': 'B'}],
        'edges': [{'source': 'A', 'target': 'B'}]
    }
    resp = await client.post('/api/graph/', json=payload)
    assert resp.status_code == status.HTTP_201_CREATED
    gid = resp.json()['id']

    resp = await client.get(f'/api/graph/{gid}/')
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data['id'] == gid
    assert {'name': 'A'} in data['nodes']
    assert {'source': 'A', 'target': 'B'} in data['edges']


@pytest.mark.asyncio
async def test_adjacency_list(client):
    payload = {
        'nodes': [{'name': 'X'}, {'name': 'Y'}, {'name': 'Z'}],
        'edges': [{'source': 'X', 'target': 'Y'}, {'source': 'X', 'target': 'Z'}]
    }
    resp = await client.post('/api/graph/', json=payload)
    gid = resp.json()['id']

    resp = await client.get(f'/api/graph/{gid}/adjacency_list')
    assert resp.status_code == status.HTTP_200_OK
    adj = resp.json()['adjacency_list']
    assert adj['X'] == ['Y', 'Z']


@pytest.mark.asyncio
async def test_delete_node(client):
    payload = {
        'nodes': [{'name': 'D'}, {'name': 'E'}],
        'edges': [{'source': 'D', 'target': 'E'}]
    }
    resp = await client.post('/api/graph/', json=payload)
    gid = resp.json()['id']

    resp = await client.delete(f'/api/graph/{gid}/node/D')
    assert resp.status_code == status.HTTP_204_NO_CONTENT

    resp = await client.get(f'/api/graph/{gid}/')
    data = resp.json()
    assert {'name': 'D'} not in data['nodes']
