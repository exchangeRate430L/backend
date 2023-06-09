from ..app import db, ma, bcrypt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, AUTO_INCREMENT=True)
    user_name = db.Column(db.String(30), unique=True)
    hashed_password = db.Column(db.String(128))
    role = db.Column(db.String(45))
    usd_balance = db.Column(db.Float, nullable=True)
    lbp_balance = db.Column(db.Float, nullable=True)
    email = db.Column(db.String(128), nullable=True)
    alert = db.Column(db.Boolean, nullable=True)

    def __init__(self, user_name, password, role, usd_balance, lbp_balance, email, alert):
        super(User, self).__init__(user_name=user_name)
        self.hashed_password = bcrypt.generate_password_hash(password)
        self.role = role
        self.usd_balance = usd_balance
        self.lbp_balance = lbp_balance
        self.email = email
        self.alert = alert
class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "user_name", "hashed_password", "role", "usd_balance", "lbp_balance", "email", "alert")
        model = User
user_schema = UserSchema()