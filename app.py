import datetime
import itertools
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
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

app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONFIG

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
                            to_user_id=request.json["to_user_id"],
                            user_id=None)
        
    else:
        from .model.transaction import Transaction
        entry = Transaction(usd_amount=request.json["usd_amount"],
                            lbp_amount=request.json["lbp_amount"],
                            usd_to_lbp=request.json["usd_to_lbp"],
                            to_user_id=request.json["to_user_id"],
                            user_id=decode_token(extract_auth_token(request)))
        from .model.user import User
        if entry.user_id:
            user = User.query.get(entry.user_id)
            toUser = User.query.get(entry.to_user_id)

        if entry.usd_to_lbp:
            user.usd_balance -= entry.usd_amount
            toUser.usd_balance += entry.usd_amount
        else:
            user.usd_balance += entry.usd_amount
            toUser.usd_balance -= entry.usd_amount

        if entry.usd_to_lbp:
            user.lbp_balance += entry.lbp_amount
            toUser.lbp_balance -= entry.lbp_amount
        else:
            user.lbp_balance -= entry.lbp_amount
            toUser.lbp_balance += entry.lbp_amount
        db.session.add(user)
        db.session.commit()
    

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

    if sell_trans != 0:
        sums = 0
        for i in range(sell_trans):
            sums += (usd_sell[i].lbp_amount / usd_sell[i].usd_amount)
            avg_usd_lbp = sums / sell_trans
    else:
        avg_usd_lbp = 0

    if buy_trans != 0:
        sums= 0
        for j in range(buy_trans):
            sums += (usd_buy[j].lbp_amount / usd_buy[j].usd_amount)
            avg_lbp_usd = sums / buy_trans
    else:
        avg_lbp_usd = 0

    
    from .model.storage import Storage
    store = Storage(avg_usd_lbp=avg_usd_lbp, avg_lbp_usd=avg_lbp_usd)
    db.session.add(store)
    db.session.commit()
    from .model.storage import storage_schema
    jsonify(storage_schema.dump(store))


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
        transactions = Transaction.query.filter(or_(Transaction.user_id == decode_token(extract_auth_token(request)), Transaction.to_user_id == decode_token(extract_auth_token(request))))
        return jsonify(transactions_schema.dump(transactions))

@app.route('/exchangeRate', methods=['GET'])
def exchange():
    START_DATE=datetime.datetime.now() - datetime.timedelta(days=3)
    END_DATE=datetime.datetime.now()
    from .model.transaction import Transaction
    from .model.storage import Storage
    transactions_usd = Transaction.query.filter(Transaction.added_date.between(START_DATE, END_DATE),Transaction.usd_to_lbp == True).all()
    transactions_lbp = Transaction.query.filter(Transaction.added_date.between(START_DATE, END_DATE),Transaction.usd_to_lbp == False).all()
    average = Storage.query.filter(Storage.added_date.between(START_DATE, END_DATE)).all()
    last_row = Storage.query.filter(Storage.added_date.between(START_DATE, END_DATE)).order_by(Storage.id.desc()).first()
    second_last_row = Storage.query.filter(Storage.added_date.between(START_DATE, END_DATE)).order_by(Storage.id.desc()).offset(2).first()
    change_usd_lbp = last_row.avg_usd_lbp - second_last_row.avg_usd_lbp
    change_lbp_usd = last_row.avg_lbp_usd - second_last_row.avg_lbp_usd

    usd_sell = []
    usd_buy = []
    num_sell = 0
    num_buy = 0

    #added data for chart
    combined_data_hour = []
    for transaction in average:
        combined_data_hour.append({'time': transaction.added_date.timestamp() * 1000,
                     'sell': transaction.avg_usd_lbp,
                     'buy': transaction.avg_lbp_usd})
        
    combined_data_day = []
    for transaction in average:
        combined_data_day.append({
            'date': transaction.added_date.strftime('%Y-%m-%d %H:%M:%S'),
            'sell': transaction.avg_usd_lbp,
            'buy': transaction.avg_lbp_usd})


    for e in transactions_usd:
        usd_sell.append(e)
        num_sell += 1
    for e in transactions_lbp:
        usd_buy.append(e)
        num_buy += 1

    sell_trans = len(usd_sell)
    buy_trans = len(usd_buy)

    if sell_trans != 0:
        sums = 0
        for i in range(sell_trans):
            sums += (usd_sell[i].lbp_amount / usd_sell[i].usd_amount)
            avg_usd_lbp = sums / sell_trans
    else:
        avg_usd_lbp = 0


    if buy_trans != 0:
        sums= 0
        for j in range(buy_trans):
            sums += (usd_buy[j].lbp_amount / usd_buy[j].usd_amount)
            avg_lbp_usd = sums / buy_trans
    else:
        avg_lbp_usd = 0
    
    return jsonify(
    combined_data_hour=combined_data_hour, 
    combined_data_day=combined_data_day,
    usd_to_lbp=avg_usd_lbp, 
    lbp_to_usd=avg_lbp_usd, 
    num_buy=num_buy, 
    num_sell=num_sell, 
    change_usd_lbp=change_usd_lbp,
    change_lbp_usd=change_lbp_usd,
)


@app.route('/user', methods=['POST'])
def users():
    from .model.user import User, user_schema
    entry = User(user_name=request.json["user_name"], password=request.json["password"], role=request.json["role"], usd_balance=request.json['usd_balance'], lbp_balance=request.json['lbp_balance'], email=request.json['email'])
    db.session.add(entry)
    db.session.commit()
    return jsonify(user_schema.dump(entry))


@app.route('/balance', methods=['GET'])
def get_balance():
    if(extract_auth_token(request) is None):
        return abort(403)
    else:
        from .model.user import User,user_schema
        user = User.query.get(decode_token(extract_auth_token(request)))
        usd_balance = user.usd_balance
        lbp_balance = user.lbp_balance
        user_name = user.user_name
        user_id = user.id
        user_email = user.email
        print(user)
        return jsonify(usd_balance=usd_balance, lbp_balance=lbp_balance, user_name=user_name, user_id = user_id, user_email=user_email)
    
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
                role = user.role
                usd_balance = user.usd_balance
                lbp_balance = user.lbp_balance
                user_id = user.id
                return(jsonify({"token" : token, "role" : role, "usd_balance": usd_balance, "lbp_balance": lbp_balance, "user_id": user_id}))

# for the backend

#   do the newBuyUsdRate-butUsdRate = change
#   do the newSellUsdRate-sellUsdRate = change