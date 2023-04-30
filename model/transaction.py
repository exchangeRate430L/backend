from ..app import db, ma, datetime

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, AUTO_INCREMENT=True)
    usd_amount = db.Column(db.Float, nullable=True)
    lbp_amount = db.Column(db.Float, nullable=True)
    usd_to_lbp = db.Column(db.Boolean)
    added_date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    to_user_id = db.Column(db.Integer, nullable=True)

    def __init__(self, usd_amount, lbp_amount, usd_to_lbp, user_id, to_user_id):
        self.lbp_amount = lbp_amount
        self.usd_amount = usd_amount
        self.usd_to_lbp = usd_to_lbp
        self.user_id = user_id
        self.added_date = datetime.datetime.now()
        self.to_user_id = to_user_id

class TransactionSchema(ma.Schema):
    class Meta:
        fields = ("id", "usd_amount", "lbp_amount", "usd_to_lbp", "added_date", "user_id", "to_user_id")
        model = Transaction
transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)