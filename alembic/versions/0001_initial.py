from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'graphs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    op.create_table(
        'nodes',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('graph_id', sa.Integer, sa.ForeignKey('graphs.id', ondelete='CASCADE'), nullable=False),
        sa.UniqueConstraint('graph_id', 'name', name='uq_node_graph_name'),
    )
    op.create_index('ix_nodes_name', 'nodes', ['name'])

    op.create_table(
        'edges',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('source_node_id', sa.Integer, sa.ForeignKey('nodes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_node_id', sa.Integer, sa.ForeignKey('nodes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('graph_id', sa.Integer, sa.ForeignKey('graphs.id', ondelete='CASCADE'), nullable=False),
        sa.UniqueConstraint('graph_id', 'source_node_id', 'target_node_id', name='uq_edge_graph_source_target'),
    )
    op.create_index('ix_edges_source', 'edges', ['source_node_id'])
    op.create_index('ix_edges_target', 'edges', ['target_node_id'])


def downgrade():
    op.drop_table('edges')
    op.drop_table('nodes')
    op.drop_table('graphs')
