from datetime import date
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status

from app.core.security import create_access_token
from app.core.token_store import active_token_store
from app.models.user import User
from app.repositories.auth_repository import AuthRepository
from app.schemas.auth import LoginResponse, UserInfo


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    @staticmethod
    def _is_user_active(status: object) -> bool:
        if status is None:
            return True
        text = str(status).strip().lower()
        return text in {"1", "active", "true", "yes"}

    @staticmethod
    def _allowed_passwords_from_dob(dob: date | None) -> set[str]:
        if not dob:
            return set()
        if isinstance(dob, str):
            text = dob.strip()
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%d%m%Y", "%Y%m%d"):
                try:
                    dob = datetime.strptime(text, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                return set()
        return {
            dob.strftime("%d%m%Y"),
            dob.strftime("%Y%m%d"),
            dob.strftime("%d-%m-%Y"),
            dob.strftime("%Y-%m-%d"),
        }

    def login(self, username: str, password: str) -> LoginResponse:
        user: User | None = self.repository.get_user_for_login(username=username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if not self._is_user_active(user.status):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is inactive",
            )

        allowed_passwords = self._allowed_passwords_from_dob(user.dob)
        if password not in allowed_passwords:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        token_id = str(uuid4())
        token = create_access_token(subject=str(user.id), token_id=token_id)
        active_token_store.set_active_token(user_id=user.id, token_id=token_id)
        return LoginResponse(
            access_token=token,
            user=UserInfo(id=user.id, name=user.name, designation=user.designation),
        )
