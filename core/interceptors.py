"""
core/interceptors.py
AG-UI Dynamic Approval Interceptors & Challenge Verification
============================================================
Middleware decorator system for tool ecosystems.
Functions marked with @requires_approval create a cryptographic challenge
token and route to the AG-UI human-in-the-loop gate before committing writes.
"""

import functools
import secrets
import time
from typing import Callable, Dict, Any


class PendingApprovalStore:
    """In-memory challenge token manager for human-in-the-loop actions."""
    def __init__(self):
        self._pending: Dict[str, Dict[str, Any]] = {}

    def create_challenge(self, action_name: str, args: tuple, kwargs: dict, risk_level: str = "HIGH") -> str:
        token = secrets.token_hex(16)
        self._pending[token] = {
            "token": token,
            "action_name": action_name,
            "args": args,
            "kwargs": kwargs,
            "risk_level": risk_level,
            "created_at": time.time(),
            "status": "PENDING"
        }
        return token

    def verify_and_consume(self, token: str) -> Dict[str, Any]:
        """Validates token and consumes it (one-time use)."""
        if token not in self._pending:
            raise ValueError("Invalid or expired AG-UI Approval Token.")
        item = self._pending.pop(token)
        return item

    def get_pending(self, token: str) -> Dict[str, Any]:
        return self._pending.get(token)


approval_store = PendingApprovalStore()


def requires_approval(action_name: str, risk_level: str = "HIGH"):
    """
    Decorator for sensitive functions requiring AG-UI approval.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Check if execution context contains verified AG-UI token
            approval_token = kwargs.pop("_ag_ui_token", None)
            if approval_token:
                # Token verified
                approval_store.verify_and_consume(approval_token)
                return func(*args, **kwargs)

            # Generate challenge token and raise suspension
            challenge = approval_store.create_challenge(
                action_name=action_name,
                args=args,
                kwargs=kwargs,
                risk_level=risk_level
            )
            return {
                "status": "APPROVAL_REQUIRED",
                "challenge_token": challenge,
                "action_name": action_name,
                "risk_level": risk_level,
                "message": f"🛡️ AG-UI Interceptor halted execution. Requires human confirmation."
            }
        return wrapper
    return decorator
