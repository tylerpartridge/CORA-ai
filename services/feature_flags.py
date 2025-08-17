import json
import hashlib
from typing import Optional
from sqlalchemy.orm import Session


class FeatureFlags:
    def __init__(self, db: Session):
        self.db = db
        self._cache = {}

    def _get_flag(self, name: str):
        # Raw SQL to avoid ORM dependency on model definition differences
        row = self.db.execute(
            "SELECT name, enabled, rollout_percentage, user_whitelist, user_blacklist FROM feature_flags WHERE name = :n",
            {"n": name},
        ).fetchone()
        return row

    def is_enabled(self, flag_name: str, user_id: Optional[int] = None) -> bool:
        cache_key = f"{flag_name}:{user_id}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        row = self._get_flag(flag_name)
        if not row:
            self._cache[cache_key] = False
            return False

        enabled = bool(row[1])
        if not enabled:
            self._cache[cache_key] = False
            return False

        # Whitelist/blacklist
        if user_id is not None:
            if row[3]:
                try:
                    whitelist = json.loads(row[3])
                    if user_id in whitelist:
                        self._cache[cache_key] = True
                        return True
                except Exception:
                    pass
            if row[4]:
                try:
                    blacklist = json.loads(row[4])
                    if user_id in blacklist:
                        self._cache[cache_key] = False
                        return False
                except Exception:
                    pass

        # Gradual rollout
        rollout = int(row[2] or 0)
        if rollout < 100:
            if user_id is None:
                self._cache[cache_key] = False
                return False
            hv = int(hashlib.md5(f"{flag_name}:{user_id}".encode()).hexdigest(), 16) % 100
            result = hv < rollout
            self._cache[cache_key] = result
            return result

        self._cache[cache_key] = True
        return True

    def clear_cache(self):
        self._cache = {}


