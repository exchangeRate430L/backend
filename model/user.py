from ..app import db, ma, bcrypt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, AUTO_INCREMENT=True)
    user_name = db.Column(db.String(30), unique=True)
    hashed_password = db.Column(db.String(128))
    role = db.Column(db.String(45))
    usd_balance = db.Column(db.Float, nullable=True)
    lbp_balance = db.Column(db.Float, nullable=True)

    def __init__(self, user_name, password, role, usd_balance, lbp_balance):
        super(User, self).__init__(user_name=user_name)
        self.hashed_password = bcrypt.generate_password_hash(password)
        self.role = role
        self.usd_balance = usd_balance
        self.lbp_balance = lbp_balance
class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_name", "hashed_password", "role", "usd_balance", "lbp_balance")
        model = User
user_schema = UserSchema()