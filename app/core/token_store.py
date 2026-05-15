from threading import Lock


class ActiveTokenStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._by_user_id: dict[int, str] = {}

    def set_active_token(self, user_id: int, token_id: str) -> None:
        with self._lock:
            self._by_user_id[user_id] = token_id

    def is_token_active(self, user_id: int, token_id: str | None) -> bool:
        if not token_id:
            return False
        with self._lock:
            return self._by_user_id.get(user_id) == token_id

    def clear_active_token(self, user_id: int, token_id: str | None = None) -> None:
        with self._lock:
            current = self._by_user_id.get(user_id)
            if current is None:
                return
            if token_id is None or current == token_id:
                self._by_user_id.pop(user_id, None)


active_token_store = ActiveTokenStore()

