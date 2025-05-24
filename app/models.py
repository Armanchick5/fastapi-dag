from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
import datetime

from database import Base


class Graph(Base):
    __tablename__ = 'graphs'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    nodes = relationship('Node', back_populates='graph', cascade='all, delete-orphan')
    edges = relationship('Edge', back_populates='graph', cascade='all, delete-orphan')


class Node(Base):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    graph_id = Column(Integer, ForeignKey('graphs.id', ondelete='CASCADE'))

    graph = relationship('Graph', back_populates='nodes')
    outgoing = relationship('Edge', back_populates='source', foreign_keys='Edge.source_node_id',
                            cascade='all, delete-orphan')
    incoming = relationship('Edge', back_populates='target', foreign_keys='Edge.target_node_id')

    __table_args__ = (
        UniqueConstraint('graph_id', 'name', name='uq_node_graph_name'),
    )


class Edge(Base):
    __tablename__ = 'edges'
    id = Column(Integer, primary_key=True, index=True)
    source_node_id = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'))
    target_node_id = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'))
    graph_id = Column(Integer, ForeignKey('graphs.id', ondelete='CASCADE'))

    graph = relationship('Graph', back_populates='edges')
    source = relationship('Node', back_populates='outgoing', foreign_keys=[source_node_id])
    target = relationship('Node', back_populates='incoming', foreign_keys=[target_node_id])

    __table_args__ = (
        UniqueConstraint('graph_id', 'source_node_id', 'target_node_id', name='uq_edge_graph_source_target'),
    )
