from pydantic import BaseModel

class TokenResponse(BaseModel):
    """
    Standard OAuth2 response schema for returning JWTs.
    """
    access_token: str
    token_type: str = "bearer"
    # We can add refresh_token here later
