from sqlalchemy.orm import relationship, DeclarativeBase, declared_attr, mapped_column, Mapped
from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, create_engine, insert
from sqlalchemy.sql import func

import uuid
import datetime

class BasicBase(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f'{cls.__name__.lower()}_table'
        
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp())

class User(BasicBase):
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    events = relationship('Event', back_populates='user')

class Event(BasicBase):
    title: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[datetime.datetime] = mapped_column(nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey('user_table.id'), nullable=False)
    
    user = relationship('User', back_populates='events')
    

if __name__ == "__main__":
    engine = create_engine("sqlite:///./events.db", echo=False)
    BasicBase.metadata.create_all(engine)
    

    with engine.connect() as conn:
        result = conn.execute(
            insert(User).returning(User.username, User.id),
            [
                {'username': 'Jacob'},
                {'username': 'Mason'},
                {'username': 'Mitch'},
                {'username': 'Janeane'}
            ]
        )
        
        for n, i in result:
            print(n, i)
            
        conn.commit()
    
    with engine.connect() as conn:
        result = conn.execute(
            insert(Event),
            [
                {'title': 'Birth', 'date': datetime.date(2024, 8, 27), 'user_id': uuid.UUID('c18d4f33e44e4bb09736831a6cdcecc5')}
            ]
        )
        
        conn.commit()
