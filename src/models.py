import uuid as uid
from pathlib import PurePath
from fastapi import HTTPException, status
from sqlalchemy import ForeignKey, Row
from sqlalchemy import select, insert, and_
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    uuid: Mapped[uid.UUID] = mapped_column(default=uid.uuid4, unique=True)

    @classmethod
    async def create_user(cls, session: AsyncSession, username: str):
        user = await cls.select_user_by_username(session, username)

        if user is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Selected name already exists"
            )
        else:
            user_uuid = uid.uuid4()
            await session.execute(
                insert(cls), {"username": username, "uuid": user_uuid}
            )
            await session.commit()

        return await cls.select_user_by_username(session, username)

    @classmethod
    async def select_user_by_username(cls,
                                      session: AsyncSession,
                                      username: str
                                      ) -> Row | None:
        stmt = select(cls).where(cls.username == username)
        result = await session.scalars(stmt)
        instance = result.one_or_none()
        return instance

    @classmethod
    async def select_user_by_id_uuid(cls,
                                     session: AsyncSession,
                                     user_id: int,
                                     uuid: uid.UUID,
                                     ) -> Row | None:
        stmt = select(cls).where(
            and_(
                cls.id == user_id, cls.uuid == uuid
            )
        )
        result = await session.scalars(stmt)
        instance = result.one_or_none()
        return instance


class Mp3Record(Base):
    __tablename__ = 'mp3_record'

    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    uuid: Mapped[uid.UUID]
    path: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    @classmethod
    async def insert_mp3_returning_id(cls,
                                      session: AsyncSession,
                                      user_id: int,
                                      mp3_uuid: uid.UUID,
                                      path: PurePath
                                      ) -> Row:
        result = await session.scalars(
            insert(cls).returning(cls.id),
            {'user_id': user_id, 'uuid': mp3_uuid, 'path': str(path)}
        )
        await session.commit()

        mp3_record_id = result.one()
        return mp3_record_id

    @classmethod
    async def select_audio(cls,
                           session: AsyncSession,
                           user_id: int,
                           record_id: int
                           ) -> Row | None:
        stmt = \
            select(User.id, cls.path) \
            .join(cls, User.id == cls.user_id) \
            .where(cls.id == record_id, cls.user_id == user_id)
        result = await session.execute(stmt)
        instance = result.one_or_none()
        return instance
