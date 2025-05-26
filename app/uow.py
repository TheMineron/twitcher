from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Iterator


class UnitOfWork:
    def __init__(self, engine):
        self.Session = sessionmaker(bind=engine)
        self.session = None

    def __enter__(self):
        self.session = self.Session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()

    @contextmanager
    def start(self) -> Iterator['UnitOfWork']:
        try:
            yield self
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
