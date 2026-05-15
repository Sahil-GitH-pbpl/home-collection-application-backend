from sqlalchemy.orm import Session

from app.models.user import User


class AuthRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_for_login(self, username: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.name == username)
            .order_by(User.id.asc())
            .first()
        )

