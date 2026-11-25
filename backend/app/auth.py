from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from argon2 import PasswordHasher, exceptions as argon_errors
import jwt
from sqlalchemy.orm import Session
from .db import get_db
from .models import User
from .config import settings

hashing=PasswordHasher()
security=HTTPBearer(auto_error=False)
ROLES=['Store Manager','Supply Chain Analyst','Inventory Planner','Category Manager','Procurement Manager','Administrator']

def hash_password(p): return hashing.hash(p)
def verify_password(p,h):
    try:return hashing.verify(h,p)
    except (argon_errors.VerifyMismatchError,argon_errors.InvalidHashError,argon_errors.VerificationError):return False
def make_token(user):
    return jwt.encode({'sub':str(user.id),'role':user.role,'exp':datetime.now(timezone.utc)+timedelta(hours=8)},settings.jwt_secret,algorithm='HS256')
def current_user(creds:HTTPAuthorizationCredentials=Depends(security),db:Session=Depends(get_db)):
    if not creds: raise HTTPException(status.HTTP_401_UNAUTHORIZED,'Authentication required')
    try:
        claims=jwt.decode(creds.credentials,settings.jwt_secret,algorithms=['HS256']); uid=int(claims['sub'])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED,'Invalid or expired token')
    user=db.get(User,uid)
    if not user or not user.active: raise HTTPException(status.HTTP_401_UNAUTHORIZED,'Account disabled or missing')
    return user

def allowed(*roles):
    def check(user:User=Depends(current_user)):
        if user.role not in roles and user.role!='Administrator':
            raise HTTPException(403,'Insufficient role permissions')
        return user
    return check
