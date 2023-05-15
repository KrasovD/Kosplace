from sqlalchemy import create_engine, insert, select
import model
engine = create_engine('sqlite:///kos_report.db')

def test_user():
    with engine.connect() as conn:
        db_shift = conn.execute(select(model.user_id)).all()
        print(db_shift)

def test_shift():
    with engine.connect() as conn:
        db_shift = conn.execute(select(model.z_report)).all()
        print(db_shift)

if __name__=='__main__':
    #test_shift()
    test_user()
