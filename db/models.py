from db import db


class Equipment(db.Model):
    __tablename__ = 'equipment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    equipment_id = db.Column(db.String(120), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Float, nullable=False)

    def __init__(self, equipment_id , timestamp, value):
        self.equipment_id = equipment_id
        self.timestamp = timestamp
        self.value = value
