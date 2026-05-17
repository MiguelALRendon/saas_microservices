from sqlalchemy import Column, String, DateTime
from app.models.base import ConceptBase


class PushSubscription(ConceptBase):
    __tablename__ = 'push_subscriptions'

    endpoint = Column(String(500), nullable=False, unique=True)
    p256dh = Column(String(255), nullable=False)
    auth = Column(String(255), nullable=False)
    user_agent = Column(String(500), nullable=True)
    last_used = Column(DateTime, nullable=True)

    def __repr__(self):
        return f'<PushSubscription {self.endpoint[:40]}>'
