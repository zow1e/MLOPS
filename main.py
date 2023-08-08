import os
from flask import Flask, redirect, url_for, render_template, request, session, flash
from forms import createEvent, signupForm, loginForm, forgetpw, changPw,  addOrder, CreateQnForm
import shelve, account

# session timeout
import flask
# import flask_login
import datetime

from werkzeug.utils import secure_filename
# from flask_login import LoginManager
from werkzeug.datastructures import CombinedMultiDict
import smtplib
from email.message import EmailMessage


# admin name: admin
# admin email: admin@gmail.com
# admin pw: eventnest

# Paypal
# https://developer.paypal.com/developer/accounts
# Account: eventnest1@gmail.com
# Password: eventnest1*
# The above account if used to create the testing payment account => Adjust Funding Here

# https://www.sandbox.paypal.com/us/home
# user payment account
# payment account: eventnestbuyer1@personal.example.com
# payment password: p!:stYK7

# business account that receive payment
# business email: eventnestbusiness1@business.example.com
# business password: p-E"OA8s
# Check for payment paid/received from the link above

app = Flask(__name__)
app.config['SECRET_KEY'] = 'I have a dream'
app.config['UPLOAD_FOLDER'] = 'static/images'

@app.before_request
def before_request():
    flask.session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=30)
    flask.session.modified = True
    # flask.g.user = flask_login.current_user


@app.before_request
def before_request():
    flask.session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=30)
    flask.session.modified = True
#     flask.g.user = flask_login.current_user


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error404.html'), 404


# ----------------------------------------------------------------------------------------------------------------------------------------------------------
# Zowie
# login_manager = LoginManager()
# login_manager.init_app(app)
# @login_manager.user_loader

def load_user(user_id):
    return User.get(user_id)

def get_id(val, my_dict):
    for key, value in my_dict.items():
        if val == value.get_email():
            return key
    return 'None'

def get_pw(val, my_dict):
    for key, value in my_dict.items():
        if val == value.get_password():
            return key
    return 'None'
def get_name(val, my_dict):
    for key, value in my_dict.items():
        if val == value.get_password():
            return key
    return 'None'

@app.route('/login', methods=['GET', 'POST'])
def login():
    login = loginForm(request.form)

    if request.method == 'POST':
        users_dict = {}
        db = shelve.open('storage.db', 'r')
        users_dict = db['Users']

        key = get_id(login.email.data, users_dict)
        key2 = get_pw(login.password.data, users_dict)

        if key == 'None' or key != key2: 
            # print(key, login.email.data, users_dict) # test
            flash('Invalid login credentials', 'danger')

        elif login.email.data == 'admin@gmail.com' and login.password.data == 'eventnest':
            user = users_dict.get(key) # get( user_id )
            db.close()
            session['admin_in'] = user.get_name()

            session['username'] = user.get_name()
            session['user_id'] = key
            session['user_email'] = user.get_email()
            bday = user.get_birthdate()
            session['user_birthdate'] = bday.strftime("%d/%m/%y")
            
            return redirect(url_for('admin_homepage'))

        elif key == key2:
            user = users_dict.get(key) # get( user_id )
            db.close()
            session['logged_in'] = user.get_name()

            session['username'] = user.get_name()
            session['user_id'] = user.get_user_id()
            session['user_email'] = user.get_email()
            bday = user.get_birthdate()
            session['user_birthdate'] = bday.strftime("%d/%m/%y")
            return redirect(url_for('accountDetails', id = user.get_user_id()))

    return render_template('users/login.html', form=login)


@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('user_id')
   return redirect(url_for('home'))

@app.route('/adminlogout')
def adminlogout():
   # remove the username from the session if it is there
   session.pop('admin_in')
   session.pop('user_id')
   return redirect(url_for('home'))


@app.route('/anomalyDetectionInput', methods=['GET', 'POST'])
def create_user():
    signup = signupForm(request.form)
    if request.method == 'POST':

        users_dict = {}
        db = shelve.open('storage.db', 'c')

        try:
            users_dict = db['Users']
        except:
            print("Error in retrieving Users from storage.db.")
        
        if signup.password.data != signup.comfirmpw.data:
            flash('Passwords do not match.', 'danger')

        else:

            key = get_id(signup.email.data, users_dict)
            if key == 'None': 

                user = account.Account(signup.name.data, signup.email.data, signup.password.data, signup.birthdate.data)
                users_dict[user.get_user_id()] = user
                db['Users'] = users_dict

                # Test codes
                users_dict = db['Users']
                user = users_dict[user.get_user_id()]
                # print(user.get_name(), "was stored in storage.db successfully with user_id ==", user.get_user_id())

                db.close()

                session['user_created'] = user.get_name()

                session['username'] = signup.name.data
                

                return redirect(url_for('login'))

            else:
                flash('Email is used for an existing account.', 'danger')

    return render_template('corporateInput/signup.html', form=signup)


# reset password

@app.route('/forgetpw', methods=['GET', 'POST'])
def forgetpass():
    forgetpwform = forgetpw(request.form)
    if request.method == 'POST':
        users_dict = {}
        db = shelve.open('storage.db', 'r')
        users_dict = db['Users']

        key = get_id(forgetpwform.email.data, users_dict)

        if key == 'None': 
            flash('Email does not have an account', 'danger')
        
        else:
            sender_email = 'eventnest1@gmail.com'
            sender_pw = 'tenroviygfhwacpo'

            msg = EmailMessage()
            msg['Subject'] = 'Reset EventNest password'
            msg['From'] = sender_email
            msg['To'] = forgetpwform.email.data

            msg.set_content('Click the link to reset your password. http://127.0.0.1:5000{}'.format(url_for('newpass', id = key)))

            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.ehlo()
                smtp.starttls() 
                smtp.ehlo()


                smtp.login(sender_email, sender_pw)

                smtp.send_message(msg)
            
            return redirect(url_for('comfirmresetpw'))
    return render_template('users/forgetpw.html', form=forgetpwform)

@app.route('/comfirmreset')
def comfirmresetpw():
    return render_template('users/comfirmreset.html')

@app.route('/newpw/<uuid(strict=False):id>/', methods=['GET', 'POST'])
def newpass(id):
    newpw = changPw(request.form)
    if request.method == 'POST':
        users_dict = {}
        db = shelve.open('storage.db', 'w')
        users_dict = db['Users']

        user = users_dict.get(str(id))

        if newpw.newpassword.data != newpw.comfirmpw.data:
            flash('Passwords do not match.', 'danger')

        else:
            
            user.set_password(newpw.newpassword.data)

            db['Users'] = users_dict
            db.close()

            session['user_updated'] = user.get_name()    
            return redirect(url_for('login'))

    return render_template('users/newpw.html', form=newpw)


@app.route('/deleteacc/<uuid(strict=False):id>/')
def deleteacc(id):
    session.pop('user_id', None)
   
    users_dict = {}
    db = shelve.open('storage.db', 'w')
    users_dict = db['Users']

    users_dict.pop(str(id))

    db['Users'] = users_dict
    db.close()
    return redirect(url_for('home'))


# account made
@app.route('/profile')
def profile():
    return render_template('users/profile.html')

@app.route('/accountDetails')
def accountDetails():
    login = loginForm(request.form)

    users_dict = {}
    db = shelve.open('storage.db', 'r')
    users_dict = db['Users']
    db.close()

    users_list = [] # all users information

    
    for key in users_dict:
        user = users_dict.get(key)
        users_list.append(user)

    return render_template('users/accountDetails.html', users_list=users_list)

@app.route('/EditAcc/<uuid(strict=False):id>', methods=['GET', 'POST'])
def EditAcc(id):    
    update_user_form = signupForm(request.form)

    if request.method == 'POST':
        users_dict = {}
        db = shelve.open('storage.db', 'w')
        users_dict = db['Users']

        user = users_dict.get(str(id))
        user.set_name(update_user_form.name.data)
        user.set_email(update_user_form.email.data)

        db['Users'] = users_dict
        db.close()

        session['user_updated'] = user.get_name()  
        session['username'] = user.get_name()
        session['user_id'] = user.get_user_id()
        session['user_email'] = user.get_email()
        bday = user.get_birthdate()
        session['user_birthdate'] = bday.strftime("%d/%m/%y")
        return redirect(url_for('accountDetails'))

    else:
        users_dict = {}
        db = shelve.open('storage.db', 'r')
        users_dict = db['Users']
        db.close()

        user = users_dict.get(str(id))
        update_user_form.name.data = user.get_name()
        update_user_form.email.data = user.get_email()

        return render_template('users/EditAcc.html', form = update_user_form)

@app.route('/ChangePass/<uuid(strict=False):id>/', methods=['GET', 'POST'])
def ChangePass(id):
    changepass = changPw(request.form)

    if request.method == 'POST':
        users_dict = {}
        db = shelve.open('storage.db', 'w')
        users_dict = db['Users']

        user = users_dict.get(str(id))

        if changepass.nowpassword.data != user.get_password():
            flash('Password does not match current password.', 'danger')

        elif changepass.newpassword.data != changepass.comfirmpw.data:
            flash('New passwords do not match.', 'danger')

        else:
            user.set_password(changepass.newpassword.data)

            db['Users'] = users_dict
            db.close()

            session['user_updated'] = user.get_name()    
            return redirect(url_for('accountDetails'))

    return render_template('users/ChangePass.html', form=changepass)




# # ----------------------------------------------------------------------------------------------------------------------------------------------------------
# # Zhang Xiang
# @app.route('/')
# def home():
#     events_dict = {}
#     db = shelve.open('storage.db', 'c')
#     events_dict = db['Events']

#     db.close()

#     events_list = []
#     for key in events_dict:
#         event = events_dict.get(key)
#         events_list.append(event)

#     return render_template('home.html', count=len(events_list), events_list=events_list)


# @app.route('/ticketDetails/<uuid(strict=False):event_id>', methods=['GET', 'POST'])
# def ticket_details(event_id):

#     events_dict = {}
#     db = shelve.open('storage.db', 'r')
#     events_dict = db['Events']
#     db.close()

#     events_list = []
#     for key in events_dict:
#         event = events_dict.get(key)
#         events_list.append(event)

#     for page in events_list:
#         if page.get_event_id() == event_id:
#             retrieve_event = page

#     add_order_form = addOrder(request.form)
#     add_order_form.order_price.choices = [(i.get_seat_price(), i.get_seat_type())
#                                             for i in retrieve_event.get_seating_plan()]

#     if request.method == 'POST' and add_order_form.validate():

#         orders_dict = {}
#         db = shelve.open('storage.db', 'c')
#         try:
#             orders_dict = db['Orders']
#         except:
#             print('Error in retrieving Orders from storage.db')
    
#         dc = {v:k for k, v in add_order_form.order_price.choices}
#         key_list = list(dc.keys())
#         value_list = list(dc.values())
#         position = value_list.index(int(add_order_form.order_price.data))


#         new_order = Order.Order(
#                             retrieve_event.get_event_id(),
#                             retrieve_event.get_event_name(),
#                             retrieve_event.get_event_category(),
#                             retrieve_event.get_event_location(),
#                             retrieve_event.get_event_poster(),
#                             retrieve_event.get_seat_image(),
#                             retrieve_event.get_event_date(),
#                             retrieve_event.get_event_time(),
#                             retrieve_event.get_event_desc(),
#                             key_list[position],
#                             add_order_form.order_price.data,
#                             add_order_form.order_quantity.data,
#                             retrieve_event.get_seating_plan()
#                             )


        
#         orders_dict[new_order.get_order_id()] = new_order
#         db['Orders'] = orders_dict

#         db.close()

#         users_dict = {}
#         db = shelve.open('storage.db', 'w')
#         users_dict = db['Users']

#         user_id =  request.form['get_user_id']
#         user = users_dict.get(user_id)
#         user.set_cart_item(new_order)

#         db['Users'] = users_dict
#         db.close()


#         return redirect(url_for('cart_page', user_id = user_id))
#     return render_template('ticketDetails.html', event=retrieve_event, form=add_order_form)



# @app.route('/updateTicketDetails/<uuid(strict=False):order_id>/<uuid(strict=False):user_id>/', methods=['GET', 'POST'])
# def update_ticket_details(order_id, user_id):

#     update_order_form = addOrder(request.form)
    
#     if request.method == 'POST':

#         db = shelve.open('storage.db', 'w')
#         users_dict = db['Users']

#         user = users_dict.get(str(user_id))
#         user_cart_list = user.get_cart_item()

#         for page in user_cart_list:
#             if page.get_order_id() == order_id:
#                 retrieve_order = page
        
        
#         update_order_form.order_price.choices = [(i.get_seat_price(), i.get_seat_type())
#                                         for i in retrieve_order.get_order_seating_plan()]
#         # Retrieve/Search for "seat type" from corresponding "seat price" by finding its index
#         dc = {v:k for k, v in update_order_form.order_price.choices}
#         key_list = list(dc.keys())
#         value_list = list(dc.values())
#         position = value_list.index(int(update_order_form.order_price.data))

#         retrieve_order.set_order_seat_type(key_list[position])
#         retrieve_order.set_order_seat_price(update_order_form.order_price.data)
#         retrieve_order.set_order_quantity(update_order_form.order_quantity.data)

#         db['Users'] = users_dict

#         return(redirect(url_for('cart_page', user_id = user_id)))

#     else:

#         users_dict = {}
#         db = shelve.open('storage.db', 'r')
#         users_dict = db['Users']
#         db.close()
    
#         user = users_dict.get(str(user_id))
#         user_cart_list = user.get_cart_item()

#         for page in user_cart_list:

#             if page.get_order_id() == order_id:
#                 retrieve_order = page

#         update_order_form.order_price.choices = [(i.get_seat_price(), i.get_seat_type())
#                                         for i in retrieve_order.get_order_seating_plan()]
        
#         dc = {v:k for k, v in update_order_form.order_price.choices}
#         key_list = list(dc.keys())
#         value_list = list(dc.values())
        
#         update_order_form.order_price.data = retrieve_order.get_order_seat_price()
#         update_order_form.order_quantity.data = retrieve_order.get_order_quantity()

#     return render_template('updateTicketDetails.html', order=retrieve_order, form=update_order_form)



# @app.route('/cart/<uuid(strict=False):user_id>')
# def cart_page(user_id):

#     users_dict = {}
#     db = shelve.open('storage.db', 'r')
#     users_dict = db['Users']
#     db.close()
    

#     user = users_dict.get(str(user_id))
#     user_cart_list = user.get_cart_item()
#     # Store all ticket price in a list "store_order_price"
#     store_order_price = []
#     for i in user_cart_list:
#         store_order_price.append(i.order_cost(i.get_order_seat_price(), i.get_order_quantity()))
#     # Add all cost together in a list
#     total_cost = "{:.2f}".format(sum(store_order_price))


#     return render_template('cart.html',user_cart=user_cart_list, count=len(user_cart_list), payable= total_cost)

# @app.route('/clearCart/<uuid(strict=False):user_id>/')
# def clear_cart(user_id):

#     users_dict = {}
#     db = shelve.open('storage.db', 'r')
#     users_dict = db['Users']
#     db.close()

#     user = users_dict.get(str(user_id))
#     user_cart_list = user.get_cart_item()

#     # Store data into Payments
#     payments_dict = {}
#     db = shelve.open('storage.db', 'c')

#     try:
#         payments_dict = db['Payments']
#     except:
#         print('Error in retrieving Payments from storage.db')
    
#     new_payment = Payment.Payment(
#         user_cart_list
#     )
    
    
#     payments_dict[new_payment.get_payment_id()] = new_payment
#     db['Payments'] = payments_dict

#     db.close()

#     # Assign paid item into a cart.
#     users_dict = {}
#     db = shelve.open('storage.db', 'w')
#     users_dict = db['Users']
#     user = users_dict.get(str(user_id))

#     # Pass payment into user
#     user.set_paid_item(new_payment)


#     # Empty user cart
#     user_cart_list = user.get_cart_item()
#     user_cart_list.clear()


#     db['Users'] = users_dict
#     db.close()

#     users_dict = {}
#     db = shelve.open('storage.db', 'r')
#     users_dict = db['Users']
#     db.close()

#     users_list = []
#     for key in users_dict:
#         user = users_dict.get(key)
#         users_list.append(user)
    
    
#     paid_list = []
#     store_payment = []
#     for i in users_list:
#         for payment in i.get_paid_item():
#             store_payment.append(payment)
    
#     # Retrieve Last paid order for confirmation page
#     get_last_payment = store_payment[-1]
    
#     for order in get_last_payment.get_order_history():
#         paid_list.append(order)

#     store_order_price = []
#     for i in paid_list:
#         store_order_price.append(i.order_cost(i.get_order_seat_price(), i.get_order_quantity()))

#     total_cost = "{:.2f}".format(sum(store_order_price))


#     return render_template('confirmationPage.html', amount_paid = total_cost, ordered_ticket = paid_list)




# @app.route('/deleteOrder/<uuid(strict=False):order_id>/<uuid(strict=False):user_id>/', methods=['GET', 'POST'])
# def delete_order(order_id, user_id):

#     users_dict = {}
#     db = shelve.open('storage.db', 'w')
#     users_dict = db['Users']
#     user = users_dict.get(str(user_id))

#     user_cart_list = user.get_cart_item()

#     count = -1
#     for i in user_cart_list:
#         count += 1
#         if i.get_order_id() == order_id:
#             user_cart_list.pop(count)

    
#     db['Users'] = users_dict
#     db.close()

#     # return redirect(url_for('cart_page'))
#     return redirect(url_for('cart_page', user_id = user_id))



# @app.route('/createEventForm', methods = ['GET', 'POST'])
# def create_event():

#     event_form = createEvent(CombinedMultiDict((request.files, request.form)))
    


#     if request.method == 'POST' and event_form.validate():
#         posterFile = event_form.event_poster.data # First grab the file
#         seatFile = event_form.seat_image.data # First grab the file

#         savePosterPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(posterFile.filename))
#         posterFile.save(savePosterPath) # Save the file

#         saveSeatPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(seatFile.filename))
#         seatFile.save(saveSeatPath) # Save the file

#         events_dict = {}
#         db = shelve.open('storage.db', flag='c', writeback=True)
#         try:
#             events_dict = db['Events']
#         except:
#             print('Error in retrieving Events from storage.db')




#         new_event = Event.Event(
#                             event_form.event_name.data,
#                             event_form.event_category.data,
#                             event_form.event_location.data,
#                             event_form.event_date.data,
#                             event_form.event_time.data,
#                             event_form.event_poster.data.filename,
#                             event_form.seat_image.data.filename,
#                             event_form.event_desc.data,
#                             )
#         # Retrieve seating plan from the form filled using WTForms FieldList                   
#         seating_plan_list = []
#         for i in event_form.data['seating_plan']:

#             seat = Seat.Seat(i['seat_type'],
#                              i['seat_available'],
#                              i['seat_price'])
#             # Add seating plan to seating_plan_list
#             seating_plan_list.append(seat)
        
#         new_event.set_seating_plan(seating_plan_list)



#         events_dict[new_event.get_event_id()] = new_event
#         db['Events'] = events_dict

#         db.close()


#         return redirect(url_for('admin_homepage'))
#     return render_template('createEventForm.html', form=event_form)


# @app.route('/updateEventForm/<uuid(strict=False):id>/', methods = ['GET', 'POST'])
# def update_event(id):
#     update_event_form = createEvent(CombinedMultiDict((request.files, request.form)))
#     if request.method == 'POST' and update_event_form.validate():
#         posterFile = update_event_form.event_poster.data # First grab the file
#         seatFile = update_event_form.seat_image.data # First grab the file

#         savePosterPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(posterFile.filename))
#         posterFile.save(savePosterPath) # Save the file

#         saveSeatPath = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(seatFile.filename))
#         seatFile.save(saveSeatPath) # Save the file

        
#         db = shelve.open('storage.db', 'w')
#         events_dict = db['Events']

#         event = events_dict.get(id)
#         event.set_event_name(update_event_form.event_name.data)
#         event.set_event_category(update_event_form.event_category.data)
#         event.set_event_location(update_event_form.event_location.data)
#         event.set_event_date(update_event_form.event_date.data)
#         event.set_event_poster(update_event_form.event_poster.data.filename)
#         event.set_seat_image(update_event_form.seat_image.data.filename)
#         event.set_event_desc(update_event_form.event_desc.data)

#         seating_plan_list = []
#         for i in update_event_form.data['seating_plan']:
#             seat = Seat.Seat(i['seat_type'],
#                              i['seat_available'],
#                              i['seat_price'])
#             seating_plan_list.append(seat)
        
#         event.set_seating_plan(seating_plan_list)

        
#         db['Events'] = events_dict
#         db.close()



#         return redirect(url_for('admin_homepage'))
#     else:

#         events_dict = {}
#         db = shelve.open('storage.db', 'r')
#         events_dict = db['Events']
#         db.close()

#         event = events_dict.get(id)
        
#         update_event_form.event_name.data = event.get_event_name()
#         update_event_form.event_category.data = event.get_event_category()
#         update_event_form.event_location.data = event.get_event_location()
#         update_event_form.event_date.data = event.get_event_date()
#         update_event_form.event_time.data = event.get_event_time()
#         update_event_form.event_poster.data = event.get_event_poster()
#         update_event_form.seat_image.data = event.get_seat_image()
#         update_event_form.event_desc.data = event.get_event_desc()
#         update_event_form.seating_plan = event.get_seating_plan()

#         return render_template('updateEventForm.html', form=update_event_form)

# @app.route('/deleteEvent/<uuid(strict=False):id>/', methods=['GET', 'POST'])
# def delete_event(id):
#     events_dict = {}
#     db = shelve.open('storage.db', 'w')
#     events_dict = db['Events']

#     events_dict.pop(id)

#     db['Events'] = events_dict
#     db.close()

#     return redirect(url_for('admin_homepage'))



# @app.route('/homeAdmin')
# def admin_homepage():
#     events_dict = {}
#     db = shelve.open('storage.db', 'r')
#     events_dict = db['Events']

#     db.close()

#     events_list = []
#     for key in events_dict:
#         event = events_dict.get(key)
#         events_list.append(event)



#     return render_template('homeAdmin.html', count=len(events_list), events_list=events_list)



# # ----------------------------------------------------------------------------------------------------------------------------------------------------------
# # Parik

# @app.route('/custDashboard/<uuid(strict=False):id>/')
# def paymentcard(id):
#     payments_dict = {}
      
#     db = shelve.open('storage.db', 'r')
#     payments_dict = db['Users']
#     db.close()
#     user = payments_dict.get(str(id))
#     #get the id
#     user_payment_list = user.get_paid_item()
#     # to get the specific user payments thru the key
#     #paid_item then payment(get_order_history) then can access the accessor methods of the order.py


#     payments_list = []  
#     for key in payments_dict:
#         order = payments_dict.get(key)
#         payments_list.append(order)

#     sales= []
#     for g in user_payment_list:
#         for i in g.get_order_history():
#             sales.append((int(i.get_order_quantity()) * int(i.get_order_seat_price())))
#     ssales = sum(sales)

#     sports_cat = []
#     for g in user_payment_list:
#         for i in g.get_order_history():
#                 if i.get_order_category() == 'S':
#                     sports_cat.append(i.get_order_category())

#     concert_cat = []
#     for g in user_payment_list:
#         for i in g.get_order_history():
#                 if i.get_order_category() == 'C':
#                     concert_cat.append(i.get_order_category())

#     tickets_sold = []
#     for g in user_payment_list:
#         for i in g.get_order_history():
#             tickets_sold.append((int(i.get_order_quantity())))
#     total_tickets_sold = sum(tickets_sold)


#     values = [25, 40, 30, 48,50,60]
#     BarVal = [13, 45, 26, 55, 44, 50]
#     labels = ["Jan", "Feb", "Mar", "Apr", "May","Jul"]


#     return render_template('custDashboard.html',payments_list=user_payment_list,values=values,BarVal=BarVal,labels=labels,ssales=ssales,total_tickets_sold=total_tickets_sold,sports_cat=len(sports_cat),concert_cat=len(concert_cat))

# @app.route('/adminDashboard')
# def new():
#     users_dict = {}
      
#     db = shelve.open('storage.db', 'r')
#     users_dict = db['Users']
#     db.close()

#     users_list = []  
#     for key in users_dict:
#         user = users_dict.get(key)
#         if user.get_email() != 'admin@gmail.com':
#             users_list.append(user)
#     #paid_item then payment(get_order_history) then can access the accessor methods of the order.py
        

#     order_price_list = []
#     for i in users_list:
#         for payment in i.get_paid_item():
#             for order in payment.get_order_history():
#                 order_price_list.append(order.order_cost(order.get_order_quantity(), order.get_order_seat_price()))

#     ssales = sum(order_price_list)


#     sports_cat = []
#     for i in users_list:
#         for payment in i.get_paid_item():
#             for order in payment.get_order_history():
#                 if order.get_order_category() == 'S':
#                     sports_cat.append(order.get_order_category())

#     concert_cat = []
#     for i in users_list:
#         for payment in i.get_paid_item():
#             for order in payment.get_order_history():
#                 if order.get_order_category() == 'C':
#                     concert_cat.append(order.get_order_category())

#     indicator_ticket_list = []
#     count = 300 + len(users_list)
#     indicator_ticket_list.append(int("{:.0f}".format(((count - 350)/count) * 100)))


#     indicator_sales_list = []
#     indicator_sales_list.append(int("{:.0f}".format((((2000 +ssales) - 1500)/(2000 + ssales)) * 100)))    

#     values = [9930, 9000, 3000, 6000,2000,7000]
#     BarVal = [3019, 7000, 1500, 8000, 6000, 5000]
#     labels = ["Jan", "Feb", "Mar", "Apr", "May","Jul"]


#     forarc = ((250 + ssales)/ 10000) * 100
#     narc1 = "{:.0f}".format(((250 + ssales)/ 10000) * 100) + "%"
#     anarac1 = narc1

#     total_sales_per_user =[]
#     name_of_all_user = []
#     id = []

#     order_quantity_list = []
#     for i in users_list:
#         for payment in i.get_paid_item():
#             for order in payment.get_order_history():
#                 order_quantity_list.append(order.get_order_quantity())

#     stickets = sum(order_quantity_list)

#     # { 'a':3,'ab':2,'abc':1,'abcd':0 }
#     # [('a', 3), ('ab', 2), ('abc', 1), ('abcd', 0)]
#     for key,value in users_dict.items():
#         sales_per_user = []
#         if value.get_name() != "admin":
#             #store the total sales from each user as every user can have multiple orders
#             for payment in value.get_paid_item():
#                 for order in payment.get_order_history():
#                     g =(order.order_cost(order.get_order_quantity(), order.get_order_seat_price()))
#                     sales_per_user.append(g)
#             total_sales_per_user.append(sum(sales_per_user))
#             id.append(key)
#             # get the name of the user in list
#             name = value.get_name()
#             # store the user_if in list
#             name_of_all_user.append(name)
    

# # sorted_zip = [(spent, 'user id'), (spent, 'user id')] - zip list into (spent,user id)
# # zip: takes iterables as it's arguments and takes one element from each iterable, placing them in a tuple.
# # sorted: will sort the data. By default, a tuple element is sorted on the element in the 0 index, so the score in this case. Reverse=True will sort it descending first.
# # the [:3] is slice notation, saying give me all elements from the beginning up to the 3rd element.



    

    
#     return render_template('adminDashboard.html',stickets = stickets,top_cust=sorted(zip(total_sales_per_user, name_of_all_user,id), reverse=True)[:3],users_dict=users_dict,forarc=forarc,anarac1=anarac1,values=values,labels=labels,BarVal=BarVal,new=new,count=len(users_list),sales_line_list=sum(order_price_list),sports_cat=len(sports_cat),concert_cat=len(concert_cat),ssales=ssales,indicator_sales=indicator_sales_list,indicator_ticket=indicator_ticket_list)




# # ----------------------------------------------------------------------------------------------------------------------------------------------------------
# # Rawtbhik
# @app.route('/success', methods=['GET', 'POST'])
# def message():
#    return redirect('messages')

# @app.route('/createQn', methods=['GET', 'POST'])
# def create_qn():
#     create_qn_form = CreateQnForm(request.form)
#     if request.method == 'POST' and create_qn_form.validate():
#         qns_dict = {}
#         db = shelve.open('storage.db', 'c')

#         try:
#             qns_dict = db['Questions']
#         except:
#             print("Error in retrieving Users from storage.db.")

#         qn = Question.Question(create_qn_form.name.data,
#                             create_qn_form.gender.data,
#                             create_qn_form.email.data,
#                             create_qn_form.subject.data,
#                             create_qn_form.remarks.data,
#                             create_qn_form.answers.data
#                             )

#         qns_dict[qn.get_qn_id()] = qn
#         db['Questions'] = qns_dict


#         return redirect(url_for('retrieve_faq'))
#     return render_template('createQn.html', form=create_qn_form)





# @app.route('/retrieveQns')
# def retrieve_qns():
#     qns_dict = {}
#     db = shelve.open('storage.db', 'r')
#     qns_dict = db['Questions']
#     db.close()

#     qns_list = []
#     for key in qns_dict:
#         qn = qns_dict.get(key)
#         qns_list.append(qn)
        
#     return render_template('retrieveQns.html', count=len(qns_list),qns_list=qns_list)


        
# @app.route('/updateQn/<uuid(strict=False):id>/', methods=['GET', 'POST'])
# def update_qn(id):
#     update_qn_form = CreateQnForm(request.form)
#     if request.method == 'POST' and update_qn_form.validate():
#         qns_dict = {}
#         db = shelve.open('storage.db', 'w')
#         qns_dict = db['Questions']

#         qn = qns_dict.get(id)
#         qn.set_name(update_qn_form.name.data)
#         qn.set_email(update_qn_form.email.data)
#         qn.set_gender(update_qn_form.gender.data)
#         qn.set_subject(update_qn_form.subject.data)
#         qn.set_remarks(update_qn_form.remarks.data)
#         qn.set_answers(update_qn_form.answers.data)
        
        

#         db['Questions'] = qns_dict
#         db.close()

#         return redirect(url_for('retrieve_qns'))
#     else:
#         qns_dict = {}
#         db = shelve.open('storage.db', 'r')
#         qns_dict = db['Questions']
#         db.close()

#         qn = qns_dict.get(id)
#         update_qn_form.name.data = qn.get_name()
#         update_qn_form.email.data = qn.get_email()
#         update_qn_form.gender.data = qn.get_gender()
#         update_qn_form.subject.data = qn.get_subject()
#         update_qn_form.remarks.data = qn.get_remarks()
#         update_qn_form.answers.data = qn.get_answers()

#         return render_template('updateQn.html', form=update_qn_form)

# @app.route('/deleteQn/<uuid(strict=False):id>', methods=['POST'])
# def delete_qn(id):
#     qns_dict = {}
#     db = shelve.open('storage.db', 'w')
#     qns_dict = db['Questions']

#     qns_dict.pop(id)

#     db['Questions'] = qns_dict
#     db.close()

#     return redirect(url_for('retrieve_qns'))



# @app.route('/faq')
# def retrieve_faq():
#     qns_dict = {}
#     db = shelve.open('storage.db', 'r')
#     qns_dict = db['Questions']
#     db.close()

#     qns_list = []
#     for key in qns_dict:
#         qn = qns_dict.get(key)
#         qns_list.append(qn)
        
#     return render_template('faq.html', count=len(qns_list),qns_list=qns_list)

# @app.route('/aboutUs')
# def about_us():
#    return render_template('aboutUs.html')



if __name__ == '__main__':
    app.run(debug=True)

