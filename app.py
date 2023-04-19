import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .db_config import DB_CONFIG
from flask import request
from flask import jsonify
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_bcrypt import Bcrypt
from flask import abort
import jwt

app = Flask(__name__)

bcrypt = Bcrypt(app)

app.config[
    'SQLALCHEMY_DATABASE_URI'] = DB_CONFIG

CORS(app)

db = SQLAlchemy(app)

ma = Marshmallow(app)

SECRET_KEY = "b'|\xe7\xbfU3`\xc4\xec\xa7\xa9zf:}\xb5\xc7\xb9\x139^3@Dv'"

def create_token(user_id):
    payload = {'exp': datetime.datetime.utcnow() + datetime.timedelta(days=4),
               'iat': datetime.datetime.utcnow(),
               'sub': user_id
               }
    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm='HS256'
        )

def extract_auth_token(authenticated_request):
    auth_header = authenticated_request.headers.get('Authorization')
    if auth_header:
        return auth_header.split(" ")[1]
    else:
        return None
def decode_token(token):
    payload = jwt.decode(token, SECRET_KEY, 'HS256')
    return payload['sub']

class Auth():
    user_name = str
    password = str
    def __init__(self, user_name, password):
        self.user_name = user_name
        self.password = password

@app.route('/transaction', methods=['POST'])
def transaction():
    # usd_amount = request.json["usd_amount"]
    # lbp_amount = request.json["lbp_amount"]
    # usd_to_lbp = request.json["usd_to_lbp"]

    if(extract_auth_token(request) is None):
        from .model.transaction import Transaction
        entry = Transaction(usd_amount=request.json["usd_amount"],
                            lbp_amount=request.json["lbp_amount"],
                            usd_to_lbp=request.json["usd_to_lbp"],
                            user_id=None)
    else:
        from .model.transaction import Transaction
        from .model.user import User
        entry = Transaction(usd_amount=request.json["usd_amount"],
                            lbp_amount=request.json["lbp_amount"],
                            usd_to_lbp=request.json["usd_to_lbp"],
                            user_id=decode_token(extract_auth_token(request)))
    db.session.add(entry)
    db.session.commit()
    from .model.transaction import transaction_schema
    return jsonify(transaction_schema.dump(entry))

@app.route('/transaction', methods=['GET'])
def rate():
    if(extract_auth_token(request) is None):
        return abort(403)
    else:
        from .model.transaction import Transaction,transactions_schema
        transactions = Transaction.query.filter_by(user_id=decode_token(extract_auth_token(request)))
        return jsonify(transactions_schema.dump(transactions))

    
@app.route('/exchangeRate', methods=['GET'])
def exchange():
    START_DATE=datetime.datetime.now() - datetime.timedelta(days=3)
    END_DATE=datetime.datetime.now()
    from .model.transaction import Transaction
    transactions_usd = Transaction.query.filter(Transaction.added_date.between(START_DATE, END_DATE),Transaction.usd_to_lbp == True).all()
    transactions_lbp = Transaction.query.filter(Transaction.added_date.between(START_DATE, END_DATE),Transaction.usd_to_lbp == False).all()
    
    usd_sell = []
    usd_buy = []
    num_sell = 0
    num_buy = 0

    for e in transactions_usd:
        usd_sell.append(e)
        num_sell += 1
    for e in transactions_lbp:
        usd_buy.append(e)
        num_buy += 1

    sell_trans = len(usd_sell)
    buy_trans = len(usd_buy)

    change_sell_list = usd_sell[:-1]
    change_buy_list = usd_buy[:-1]

    change_sell_trans = len(change_sell_list)
    change_buy_trans = len(change_buy_list)


    if sell_trans != 0:
        sum = 0
        for i in range(sell_trans):
            sum += (usd_sell[i].lbp_amount / usd_sell[i].usd_amount)
            avg_usd_lbp = sum / sell_trans
    else:
        avg_usd_lbp = 0

    if change_buy_trans != 0:
        sum = 0
        for j in range(change_buy_trans):
            sum += (change_buy_list[j].lbp_amount / change_buy_list[j].usd_amount)
            avg_change_lbp_usd = sum / change_buy_trans
    else:
        avg_change_lbp_usd = 0


    if change_sell_trans != 0:
        sum = 0
        for i in range(change_sell_trans):
            sum += (change_sell_list[i].lbp_amount / change_sell_list[i].usd_amount)
            avg_change_usd_lbp = sum / change_sell_trans
    else:
        avg_change_usd_lbp = 0

    if buy_trans != 0:
        sum = 0
        for j in range(buy_trans):
            sum += (usd_buy[j].lbp_amount / usd_buy[j].usd_amount)
            avg_lbp_usd = sum / buy_trans
    else:
        avg_lbp_usd = 0
    return jsonify(usd_to_lbp=avg_usd_lbp, lbp_to_usd=avg_lbp_usd, num_buy=num_buy, num_sell=num_sell, avg_change_lbp_usd=avg_change_lbp_usd, avg_change_usd_lbp=avg_change_usd_lbp)

@app.route('/user', methods=['POST'])
def users():
    from .model.user import User, user_schema
    entry = User(user_name=request.json["user_name"], password=request.json["password"])
    db.session.add(entry)
    db.session.commit()
    return jsonify(user_schema.dump(entry))

@app.route('/authentication', methods=['POST'])
def authentication():
    entry = Auth(user_name = request.json['user_name'], password = request.json['password'])
    if(len(entry.user_name)==0 or len(entry.password)==0):
        return abort(400)
    else:
        from .model.user import User
        user = User.query.filter_by(user_name=entry.user_name).first()
        if user is None:
            return abort(403)
        else:
            if not bcrypt.check_password_hash(user.hashed_password, entry.password):
               return abort(403)
            else:
                token = create_token(user.id)
                return(jsonify({"token" : token}))

# for the backend

#   do the newBuyUsdRate-butUsdRate = change
#   do the newSellUsdRate-sellUsdRate = change