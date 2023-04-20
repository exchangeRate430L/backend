from ..app import db, ma, datetime

class Storage(db.Model):
    id = db.Column(db.Integer, primary_key=True, AUTO_INCREMENT=True)
    avg_usd_lbp = db.Column(db.Integer)
    avg_lbp_usd = db.Column(db.Integer)
    added_date = db.Column(db.DateTime)

    def __init__(self, avg_usd_lbp, avg_lbp_usd):
        self.avg_usd_lbp = avg_usd_lbp
        self.avg_lbp_usd = avg_lbp_usd
        self.added_date = datetime.datetime.now()

class StorageSchema(ma.Schema):
    class Meta:
        fields = ("id", "avg_usd_lbp", "avg_lbp_usd", "added_date")
        model = Storage
storage_schema = StorageSchema()
storages_schema = StorageSchema(many=True)