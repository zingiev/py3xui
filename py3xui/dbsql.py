import sqlalchemy as sql


metadata = sql.MetaData()


sessions = sql.Table(
    'sessions', metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('name', sql.String, nullable=False),
    sql.Column('value', sql.String, nullable=False),
    sql.Column('domain', sql.String, nullable=False),
    sql.Column('path', sql.String, nullable=False),
    sql.Column('secure', sql.String, nullable=False),
)

inbounds = sql.Table(
    'inbounds', metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('inbound_id', sql.Integer, nullable=False),
    sql.Column('name', sql.String, nullable=False),
    sql.Column('session', sql.ForeignKey('sessions.id', ondelete='CASCADE'))
)

clients = sql.Table(
    'clients', metadata,
    sql.Column('id', sql.Integer, primary_key=True),
    sql.Column('client_id', sql.Integer, nullable=False),
    sql.Column('uuid', sql.String, nullable=False),
    sql.Column('email', sql.String, nullable=False),
    sql.Column('inbound', sql.ForeignKey('inbounds.id', ondelete='CASCADE'))
)
