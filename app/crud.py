from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from models import Graph, Node, Edge
from schemas import GraphCreate, NodeBase, EdgeBase


async def create_graph(db: AsyncSession, graph_in: GraphCreate) -> int:
    if not graph_in.nodes:
        raise HTTPException(status_code=400, detail='Graph must contain at least one node')

    new_graph = Graph()
    db.add(new_graph)
    await db.flush()

    name_to_id = {}
    for node in graph_in.nodes:
        db_node = Node(name=node.name, graph_id=new_graph.id)
        db.add(db_node)
        await db.flush()
        name_to_id[node.name] = db_node.id

    edges = []
    for edge in graph_in.edges:
        if edge.source not in name_to_id or edge.target not in name_to_id:
            raise HTTPException(status_code=400, detail='Edge references unknown node')
        edges.append((name_to_id[edge.source], name_to_id[edge.target]))

    from collections import defaultdict, deque
    graph_map = defaultdict(list)
    indegree = defaultdict(int)
    for src, tgt in edges:
        graph_map[src].append(tgt)
        indegree[tgt] += 1
        indegree.setdefault(src, indegree.get(src, 0))

    queue = deque([n for n, d in indegree.items() if d == 0])
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for nbr in graph_map[node]:
            indegree[nbr] -= 1
            if indegree[nbr] == 0:
                queue.append(nbr)
    if visited != len(indegree):
        raise HTTPException(status_code=400, detail='Graph must be acyclic')

    for src_id, tgt_id in edges:
        db_edge = Edge(source_node_id=src_id, target_node_id=tgt_id, graph_id=new_graph.id)
        db.add(db_edge)

    await db.commit()
    return new_graph.id


async def get_graph(db: AsyncSession, graph_id: int):
    result = await db.execute(select(Graph).where(Graph.id == graph_id))
    graph = result.scalars().first()
    if not graph:
        raise HTTPException(status_code=404, detail='Graph not found')

    nodes = [NodeBase(name=node.name) for node in graph.nodes]
    edges = [EdgeBase(source=edge.source.name, target=edge.target.name) for edge in graph.edges]
    return type('GraphRead', (), {'id': graph.id, 'nodes': nodes, 'edges': edges})()


async def get_adjacency_list(db: AsyncSession, graph_id: int) -> dict:
    result = await db.execute(select(Edge).where(Edge.graph_id == graph_id))
    edges = result.scalars().all()

    adj = {}
    for edge in edges:
        adj.setdefault(edge.source.name, []).append(edge.target.name)
    return adj


async def delete_node(db: AsyncSession, graph_id: int, node_name: str) -> None:
    result = await db.execute(
        select(Node).where(Node.graph_id == graph_id, Node.name == node_name)
    )
    node = result.scalars().first()
    if not node:
        raise HTTPException(status_code=404, detail='Node not found')

    await db.delete(node)
    await db.commit()
