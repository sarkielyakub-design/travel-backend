from fastapi import Depends, HTTPException
from app.api.deps import get_current_user


def require_role(required_role: str):
    def role_checker(user = Depends(get_current_user)):
        if user.role != required_role:
            raise HTTPException(status_code=403, detail=f"{required_role} only")
        return user

    return role_checker