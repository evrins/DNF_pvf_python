from sqlalchemy import select
from sqlalchemy.orm import Session

from dnfpkgtool.db.model.account_cargo import AccountCargo
from dnfpkgtool.db.repo.base_repo import BaseRepo


class AccountCargoRepo(BaseRepo):
    def __init__(self):
        super().__init__('taiwan_cain')

    def query_by_m_id(self, m_id: int) -> AccountCargo:
        with Session(self.get_engine()) as session:
            stmt = select(AccountCargo).where(AccountCargo.m_id == m_id)
            return session.scalars(stmt).first()


def get_account_cargo_repo() -> AccountCargoRepo:
    return AccountCargoRepo()
