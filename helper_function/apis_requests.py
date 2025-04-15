from fastapi import Header
def get_current_user(token: str = Header(..., description="User authentication token")):
    return token