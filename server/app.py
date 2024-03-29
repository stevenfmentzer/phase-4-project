from flask import Flask, abort, session, redirect, url_for, make_response, request, jsonify
from models import db, User, BankAccount, Bill, Income, Payment
#Import database and application from config.py
from config import app, db
import math


######### ROUTES / VIEWS #########

#### HOME ####
@app.route('/')
def home():
    return 'CreditScape'

#### LOGIN/OUT ####
@app.route('/login', methods=['POST'])
def login():
    # If a GET request is made to this endpoint, return 405 Method Not Allowed
    if request.method != 'POST':
        abort(405)
    if request.headers.get("Content-Type") == 'application/json':
        form_data = request.get_json()
    else: 
        form_data = request.form
    print(form_data)
    username = form_data['username']
    password = form_data['password']

    user = User.query.filter(User.username == username).first()
    print(user)
    if user.authenticate(password):
        session["user"] = user.id
        response = make_response(user.to_dict(),200)
        print(session["user"])
        print("SESSION>USER SET")

    else:
        response = make_response({"Error": "Not valid password"}, 400)
    return response

@app.route('/logout')
def logout():
    # Rest Session User
    session["user"] = None
    # Return to home screen
    return redirect(url_for('home'))

@app.route('/session', methods=['GET', 'POST'])
def check_session():
    if request.method == 'POST':
        data = request.json  # Assuming the client sends JSON data
        username = data.get('username')
        password = data.get('password')

        # Validate username and password (e.g., check against database)
        user = User.query.filter(User.username == username).first()
        if user and user.authenticate(password):  # Example: assuming User model has a check_password method
            session['user'] = user.id  # Set user ID in session
            response = make_response(user.to_dict(),200)
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

    elif request.method == 'GET':
        # Handle the GET request (e.g., checking user session)
        if 'user' in session:
            user = User.query.get(session['user'])
            if user:
                return jsonify({'success': True, 'message': 'User session found', 'user': user.to_dict()}), 200
        return jsonify({'success': False, 'message': 'No user session found'}), 404
    return response
    

#### USER #### 
@app.route('/register', methods=['POST'])
def register():
    # If a GET request is made to this endpoint, return 405 Method Not Allowed
    if request.method != 'POST':
        abort(405)
    try: 
        if request.headers.get("Content-Type") == 'application/json':
            form_data = request.get_json()
        else: 
            form_data = request.form
            
        existing_user = User.query.filter(User.username == form_data['username']).first()
    
        if existing_user:
            response = make_response({'Error' : 'Username already exists. Please choose a new one'},409)
        else: 
            new_user = User(
                            first_name=form_data['first_name'],
                            last_name=form_data['last_name'],
                            username=form_data['username']
                            )
            new_user.password_hash = form_data['password'] 
            
            db.session.add(new_user)
            db.session.commit()

            response = make_response(new_user.to_dict(only=('id','first_name','last_name')), 201)
    except Exception as e:
        print("Exception:", e)
        response = make_response({"ERROR" : e },404)
    return response

@app.route('/account/<int:id>', methods=['GET','PATCH','DELETE'])
def user_by_id(id):
    try: 
        user = User.query.filter(User.id == id).first()
    
        if request.method == 'GET':
            response = make_response(user.to_dict(only=('first_name','last_name')), 200)
        elif request.method == 'PATCH':

            if request.headers.get("Content-Type") == 'application/json':
                form_data = request.get_json()
            else: 
                form_data = request.form
                
            for attr in form_data: 
                setattr(user, attr, form_data[attr])
                
            db.session.commit()
            response = make_response(user.to_dict(only=('first_name','last_name')), 202)
        elif request.method == 'DELETE':
            db.session.delete(user)
            db.session.commit()
            response = make_response('',202)
        else:
            abort(405)
    except Exception as e:
        print("Exception:", e)
        response = make_response({"ERROR" : e }, 404)
    return response    

#### BILLS ####
@app.route('/bills/<int:id>', methods=['GET','POST'])
def user_bills(id):
    try: 
        if request.method == 'GET':
            bills = [bill.to_dict() for bill in Bill.query.filter(Bill.user_id == id).all()]
            response = make_response(bills, 200)
        elif request.method == 'POST':
            print("POST")
            if request.headers.get("Content-Type") == 'application/json':
                form_data = request.get_json()
            else: 
                form_data = request.form

            print("ADDING")
            new_bill = Bill(user_id = form_data['user_id'],
                            name = form_data['name'],
                            lender_name = form_data['lender_name'],
                            description = form_data['description'],
                            pay_date = form_data['pay_date'],
                            bill_type = form_data['bill_type'],
                            balance_init = form_data['balance_init'],
                            balance_remain = form_data['balance_remain'],
                            min_pay_value = form_data['min_pay_value'],
                            apr_rate = form_data['apr_rate']
                            )
        
            db.session.add(new_bill)
            db.session.commit()

            response = make_response(new_bill.to_dict(), 201)
        else:
            abort(405)
    except Exception as e:
        print("Exception:", e)
        response = make_response({"ERROR" : e },404)
    return response

@app.route('/bill/<int:id>', methods=['GET','PATCH','DELETE'])
def bill_by_id(id):
    try: 
        bill = Bill.query.filter(Bill.id == id).first()
        if request.method == 'GET':
            response = make_response(bill.to_dict(), 200)
        elif request.method == 'PATCH':
            if request.headers.get("Content-Type") == 'application/json':
                form_data = request.get_json()
            else: 
                form_data = request.form
                    
            for attr in form_data: 
                setattr(bill, attr, form_data[attr])
        
                db.session.commit()
                response = make_response(bill.to_dict(), 202)
        elif request.method == 'DELETE':
            db.session.delete(bill)
            db.session.commit()
            response = make_response('',202)
        else:
            abort(405)
    except Exception as e:
        print("Exception:", e)
        response = make_response({"ERROR" : e }, 404)
    return response

#### BANKS ####
@app.route('/banks', methods=['GET','POST'])
def banks():
    try:
        if request.method == 'GET':
            banks = [bank.to_dict() for bank in BankAccount.query.all()]
            response = make_response(banks, 200)
        elif request.method == 'POST':
            if request.headers.get("Content-Type") == 'application/json':
                form_data = request.get_json()
            else: 
                form_data = request.form
        
            new_bank = BankAccount( user_id = form_data["user_id"],
                                    name = form_data['name'],
                                    balance = form_data['balance']
                                    )
            
            db.session.add(new_bank)
            db.session.commit()
            response = make_response(new_bank.to_dict(), 201)
        else:
            abort(405)

    except Exception as e:
        print("Exception:", e)
        response = make_response({"ERROR" : e },404)
    return response

@app.route('/banks/<int:id>')
def user_banks(id):
    try:
        banks = [bank.to_dict() for bank in BankAccount.query.filter(BankAccount.user_id == id).all()]
        response = make_response(banks, 200)
    except Exception as e:
        print("Exception:", e)
        response = make_response({"ERROR" : e },404)
    print(banks)
    return response


@app.route('/bank/<int:id>', methods=['GET','PATCH','DELETE'])
def bank_by_id(id):
    try: 
        bank = BankAccount.query.filter(BankAccount.user_id == session["user"]).filter(BankAccount.id == id).first()
        if request.method == 'GET':
            response = make_response(bank.to_dict(), 200)
        elif request.method == 'PATCH':
            if request.headers.get("Content-Type") == 'application/json':
                form_data = request.get_json()
            else: 
                form_data = request.form
                    
            for attr in form_data: 
                setattr(bank, attr, form_data[attr])
        
            db.session.commit()
            response = make_response(bank.to_dict(), 202)
        elif request.method == 'DELETE':
            db.session.delete(bank)
            db.session.commit()
            response = make_response('',202)
        else:
            abort(405)
    except Exception as e:
        print("Exception:", e)
        response = make_response({"ERROR" : e }, 404)
    return response

#### INCOMES ####
@app.route('/incomes/<int:id>', methods=['GET','POST'])
def user_incomes(id):
    try:
        if request.method == 'GET':
            incomes = [income.to_dict() for income in Income.query.filter(Income.user_id == id).all()]
            response = make_response(incomes, 200)
        elif request.method == 'POST':
            if request.headers.get("Content-Type") == 'application/json':
                form_data = request.get_json()
            else: 
                form_data = request.form

            new_income = Income(user_id = form_data['user_id'],
                                    bank_account_id = form_data['bank_account_id'],
                                    pay_value = form_data['pay_value'],
                                    pay_freq = form_data['pay_freq']
                                    )
            
            db.session.add(new_income)
            db.session.commit()

            # response = make_response(new_income.to_dict('-user.incomes', '-bank.incomes'), 201)
            response = make_response(new_income.to_dict(), 201)
        else:
            abort(405)
    except Exception as e:
        print("Exception:", e)
        response = make_response({"ERROR" : e },404)
    return response

@app.route('/income/<int:id>', methods=['GET','PATCH','DELETE'])
def income_by_id(id):
    try: 
        income = Income.query.filter(Income.user_id == session["user"]).filter(Income.id == id).first()
        if request.method == 'GET':
            response = make_response(income.to_dict(), 200)
        elif request.method == 'PATCH':
            if request.headers.get("Content-Type") == 'application/json':
                form_data = request.get_json()
            else: 
                form_data = request.form
                    
            for attr in form_data: 
                setattr(income, attr, form_data[attr])
            
                db.session.commit()
                response = make_response(income.to_dict(), 202)
        elif request.method == 'DELETE':
            db.session.delete(income)
            db.session.commit()
            response = make_response('',202)
        else:
            abort(405)
    except Exception as e:
        print("Exception:", e)
        response = make_response({"ERROR" : e }, 404)
    return response

#### PAYMENTS ####
def get_payments_for_user(user_id):
    try:
        payments = db.session.query(Payment).\
            join(BankAccount, Payment.bank_account_id == BankAccount.id).filter(BankAccount.user_id == user_id).all()
    except Exception as e:
        print("Exception:", e)
    return payments

@app.route('/payments/<int:id>', methods=['GET','POST'])
def user_payments(id):
    try:
        if request.method == 'GET':
            payments = [payment.to_dict() for payment in get_payments_for_user(id)]
            response = make_response(payments, 200)
        elif request.method == 'POST':
            if request.headers.get("Content-Type") == 'application/json':
                form_data = request.get_json()
            else: 
                form_data = request.form
        
            new_payment = Payment(bank_account_id = form_data['bank_account_id'],
                                    bill_id = form_data['bill_id'],
                                    pay_date = form_data['pay_date'],
                                    pay_value = form_data['pay_value']
                                    )
            
            db.session.add(new_payment)
            db.session.commit()

            response = make_response(new_payment.to_dict(), 201)
        else:
            abort(405)
    except Exception as e:
        print("Exception:", e)
        response = make_response({"ERROR" : e },404)
    return response

@app.route('/payment/<int:id>', methods=['GET','PATCH','DELETE'])
def payment_by_id(id):
    try: 
        payment = Payment.query.filter(Payment.id == id).first()
        bank_account = BankAccount.query.filter(BankAccount.id == payment.bank_account_id).first()
    
        if bank_account.user_id == session["user"]:
            if request.method == 'GET':
                response = make_response(payment.to_dict(), 200)
            elif request.method == 'PATCH':
                if request.headers.get("Content-Type") == 'application/json':
                    form_data = request.get_json()
                else: 
                    form_data = request.form

                for attr in form_data: 
                    setattr(payment, attr, form_data[attr])
            
                db.session.commit()
                response = make_response(payment.to_dict(), 202)
            elif request.method == 'DELETE':
                db.session.delete(payment)
                db.session.commit()
                response = make_response('',202)
            else:
                abort(405)
        else: 
            response = make_response({"ERROR": "Unauthorized access, Payment ID does not belong to user"}, 403)
    except Exception as e:
        print("Exception:", e)
        response = make_response({"ERROR" : e }, 404)
    return response


if __name__ == '__main__':
    app.run(port=5555, debug=True)

