from database import session_factory


def get_session():
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
