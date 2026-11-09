from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.db import get_session
from app.models import User, UserRole

SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


async def get_current_user(session: SessionDep, settings: SettingsDep) -> User:
    """STUB di autenticazione: restituisce (e crea al volo) un utente demo.

    TODO(corso): sostituire con autenticazione reale (JWT/OIDC) — vedi RF-01
    in docs/specifiche.md e l'open point OP-001 in docs/open-points.md.
    """
    user = await session.scalar(select(User).where(User.email == settings.demo_user_email))
    if user is None:
        user = User(email=settings.demo_user_email, full_name="Utente Demo", role=UserRole.ADMIN)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
