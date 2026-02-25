from datetime import datetime, time
from typing import Optional

from sqlalchemy import (JSON, CheckConstraint, ForeignKey, Index, String,
                        UniqueConstraint, func)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase): ...


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    edited_at: Mapped[datetime] = mapped_column(onupdate=func.now(), default=func.now())

    characters: Mapped[list["Character"]] = relationship(back_populates="owner")
    chats: Mapped[list["Chat"]] = relationship(back_populates="owner")
    messages: Mapped[list["Message"]] = relationship(back_populates="owner")
    scheduled_tasks: Mapped[list["ScheduledTask"]] = relationship(
        back_populates="owner"
    )
    scheduled_messages: Mapped[list["ScheduledMessage"]] = relationship(
        back_populates="owner"
    )

    def __repr__(self):
        return f"<User {self.id} {self.username}>"


class Character(Base):
    __tablename__ = "character"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(50), index=True)
    system_prompt: Mapped[str]
    description: Mapped[str | None] = mapped_column(default=None)
    is_private: Mapped[bool]
    is_hidden_prompt: Mapped[bool]
    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    edited_at: Mapped[datetime] = mapped_column(onupdate=func.now(), default=func.now())

    owner: Mapped["User"] = relationship(back_populates="characters")
    chats: Mapped[list["Chat"]] = relationship(back_populates="character")

    @property
    def owner_username(self):
        return self.owner.username if self.owner else None

    def __repr__(self):
        return (
            f"<{'Public' if not self.is_private else 'Private'}"
            f"character {self.name} of user {self.owner_id}>"
        )


class Chat(Base):
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id", ondelete="CASCADE")
    )
    character_name: Mapped[str] = mapped_column(String(50))
    system_prompt: Mapped[str]
    description: Mapped[str | None] = mapped_column(default=None)
    is_hidden_prompt: Mapped[bool]
    is_active: Mapped[bool] = mapped_column(default=True)

    last_message_id: Mapped[int | None] = mapped_column(
        ForeignKey("message.id", ondelete="SET NULL")
    )
    last_message_text: Mapped[str | None] = mapped_column(default=None)
    last_message_datetime: Mapped[datetime] = mapped_column()
    structure: Mapped[list] = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    edited_at: Mapped[datetime] = mapped_column(onupdate=func.now(), default=func.now())

    owner: Mapped["User"] = relationship(back_populates="chats")
    character: Mapped["Character"] = relationship(back_populates="chats")
    last_message: Mapped[Optional["Message"]] = relationship(
        foreign_keys=[last_message_id]
    )
    messages: Mapped[list["Message"]] = relationship(back_populates="chat")
    scheduled_tasks: Mapped[list["ScheduledTask"]] = relationship(back_populates="chat")
    scheduled_messages: Mapped[list["ScheduledMessage"]] = relationship(
        back_populates="chat"
    )

    __table_args__ = (
        Index("ix_chat_last_msg_dt_desc", last_message_datetime.desc()),
        Index(
            "ix_chat_owner_last_msg_dt_desc", "owner_id", last_message_datetime.desc()
        ),
    )

    def __repr__(self):
        return (
            f"<Chat of user {self.owner_id} and character "
            f"{self.character_id} {self.character_name}"
        )


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(9))
    media_type: Mapped[str] = mapped_column(String(5))
    message: Mapped[str | None] = mapped_column(default=None)
    media: Mapped[str | None] = mapped_column(default=None)
    is_active: Mapped[bool] = mapped_column(default=True)
    conducted: Mapped[datetime] = mapped_column()
    history: Mapped[list] = mapped_column(JSON, default=list)
    info: Mapped[dict | None] = mapped_column(JSON, default=None)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    edited_at: Mapped[datetime] = mapped_column(onupdate=func.now(), default=func.now())

    owner: Mapped["User"] = relationship(back_populates="messages")
    chat: Mapped["Chat"] = relationship(back_populates="messages")
    scheduled_message: Mapped["ScheduledMessage"] = relationship(
        back_populates="message"
    )

    __table_args__ = (
        Index("ix_message_chat_conducted_desc", "chat_id", conducted.desc()),
        Index(
            "ix_message_owner_chat_conducted_desc",
            "owner_id",
            "chat_id",
            conducted.desc(),
        ),
    )

    def __repr__(self):
        return (
            f"<Message of user {self.owner_id} in chat "
            f"{self.chat_id} at {self.conducted}"
        )


class ScheduledTask(Base):
    __tablename__ = "scheduled_task"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id", ondelete="CASCADE"))
    center_time: Mapped[time]
    delta_minutes: Mapped[int]
    user_timezone: Mapped[int]
    prompt: Mapped[str | None] = mapped_column(default=None)
    use_time: Mapped[bool]
    is_active: Mapped[bool] = mapped_column(default=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    edited_at: Mapped[datetime] = mapped_column(onupdate=func.now(), default=func.now())

    owner: Mapped["User"] = relationship(back_populates="scheduled_tasks")
    chat: Mapped["Chat"] = relationship(back_populates="scheduled_tasks")
    scheduled_messages: Mapped[Optional["ScheduledMessage"]] = relationship(
        back_populates="task"
    )

    __table_args__ = (
        CheckConstraint(
            "delta_minutes >= 0 AND delta_minutes <= 360", name="ck_delta_minutes"
        ),
        Index("ix_scheduled_task_created_at_desc", created_at.desc()),
    )

    def __repr__(self):
        return f"<ScheduledTask of user {self.owner_id} at {self.center_time} +- {self.delta_minutes} minutes>"


class ScheduledMessage(Base):
    __tablename__ = "scheduled_message"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    task_id: Mapped[int | None] = mapped_column(
        ForeignKey("scheduled_task.id", ondelete="CASCADE"), default=None
    )
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id", ondelete="CASCADE"))
    message_id: Mapped[int | None] = mapped_column(
        ForeignKey("message.id", ondelete="SET NULL"), default=None
    )
    scheduled_at: Mapped[datetime] = mapped_column()
    is_sent: Mapped[bool] = mapped_column(default=False)
    sent_at: Mapped[datetime | None] = mapped_column(default=None)
    prompt: Mapped[str | None] = mapped_column(default=None)
    use_time: Mapped[bool]

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    edited_at: Mapped[datetime] = mapped_column(onupdate=func.now(), default=func.now())

    owner: Mapped["User"] = relationship(back_populates="scheduled_messages")
    task: Mapped["ScheduledTask"] = relationship(back_populates="scheduled_messages")
    chat: Mapped["Chat"] = relationship(back_populates="scheduled_messages")
    message: Mapped[Optional["Message"]] = relationship(
        back_populates="scheduled_message"
    )

    __table_args__ = (
        Index("ix_scheduled_message_scheduled_at_desc", scheduled_at.desc()),
        UniqueConstraint("task_id", "scheduled_at", name="uq_task_scheduled_at"),
    )

    def __repr__(self):
        message = f"<ScheduledMessage of user {self.owner_id} in chat {self.chat_id} scheduled at {self.scheduled_at} "
        if self.is_sent:
            message = message + f"was sent at {self.sent_at}>"
        else:
            message = message + "has not been sent yet>"
        return message
