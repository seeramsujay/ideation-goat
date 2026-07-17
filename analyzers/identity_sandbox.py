import jwt
import time
from typing import Dict, Any, List, Optional

# Secret key used for signing/verification of the sandboxed tokens
SECRET_KEY = "ideation_goat_super_secret_sandbox_key"
ALGORITHM = "HS256"

def generate_mock_jwt_token(
    user_id: str, 
    roles: List[str], 
    permissions: List[str], 
    expires_in_seconds: int = 3600
) -> str:
    """
    Utility helper to generate signed mock JWT tokens for identity validation tests.
    """
    payload = {
        "sub": user_id,
        "roles": roles,
        "permissions": permissions,
        "iss": "IdeationGOAT-Auth",
        "iat": int(time.time()),
        "exp": int(time.time()) + expires_in_seconds
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_sandbox_identity(token: str, required_permission: Optional[str] = None) -> Dict[str, Any]:
    """
    Verifies a JWT token signature, expiration, and required permission scopes.
    """
    try:
        # Decode and verify the JWT signature and expiration
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM], 
            issuer="IdeationGOAT-Auth"
        )
        
        # Check permissions scope
        user_permissions = payload.get("permissions", [])
        authorized = True
        reason = "Token is valid and active."
        
        if required_permission and required_permission not in user_permissions:
            authorized = False
            reason = f"Access Denied: Missing required permission scope '{required_permission}'."
            
        return {
            "status": "authenticated" if authorized else "unauthorized",
            "user_id": payload.get("sub"),
            "roles": payload.get("roles", []),
            "permissions": user_permissions,
            "authorized": authorized,
            "reason": reason
        }
        
    except jwt.ExpiredSignatureError:
        return {
            "status": "expired",
            "authorized": False,
            "reason": "Authentication Failed: Token signature has expired."
        }
    except jwt.InvalidIssuerError:
        return {
            "status": "invalid_issuer",
            "authorized": False,
            "reason": "Authentication Failed: Untrusted token issuer."
        }
    except jwt.InvalidTokenError as ite:
        return {
            "status": "invalid_token",
            "authorized": False,
            "reason": f"Authentication Failed: Token signature validation error. {str(ite)}"
        }
