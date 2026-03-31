from app import db

class Credential(db.Model):
    __tablename__ = "credentials"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100))
    password = db.Column(db.String(255))
    type = db.Column(db.String(50))  # ssh, database, api
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "type": self.type,
            "created_at": str(self.created_at)
        }