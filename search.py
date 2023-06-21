from sqlalchemy.orm import Session
from library import User, Grant, Foundation

def search(query: str, session: Session):
    users = session.query(User).filter(User.name.ilike(f"%{query}%")).all()
    grants = session.query(Grant).filter(Grant.name.ilike(f"%{query}%") | Grant.description.ilike(f"%{query}%")).all()
    return users, grants