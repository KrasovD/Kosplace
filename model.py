from sqlalchemy import create_engine, Column, MetaData, Table, Integer, DateTime, String

engine = create_engine('sqlite:///kos_report.db')

meta_data = MetaData()

z_report= Table(
    'z_report',
    meta_data,
    Column('id', Integer, primary_key=True),
    Column('shift_id', Integer),
    Column('terminal', String),
    Column('open_date', DateTime),
    Column('cash', Integer),
    Column('card', Integer),
    Column('count', Integer),
    Column('avg_check', Integer),
    Column('total', Integer)
)

user_id = Table(
    'user_id',
    meta_data,
    Column('user_id', Integer, unique=True)
)

if __name__ == '__main__':
    meta_data.create_all(engine)