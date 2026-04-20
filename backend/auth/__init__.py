"""Modulo de autenticacao do backend.

Exemplo de uso em rotas protegidas:

```python
from fastapi import Depends, HTTPException, status
from backend.auth.security import verify_token, get_token_from_header

@router.get("/protected")
def protected_route(authorization: str = Header(None)):
    token = get_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    user_id = payload.get("sub")
    # ... usar user_id
```

Fluxo de autenticacao:
1. POST /auth/register - Cria novo usuario
2. POST /auth/login - Retorna JWT token
3. GET /protected + Authorization: Bearer {token} - Acessa rota protegida
"""

