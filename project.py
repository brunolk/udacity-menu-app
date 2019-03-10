'''
Connect to database and add CRUD functionality
'''

from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash,
                   jsonify)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from database_setup import Base, Restaurant, MenuItem, User

from flask import session as login_session
import random
import string

# libraries to handle oauth authentication
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# create an instance of Flask class with the name
# of the running application as the argument.
app = Flask(__name__)

# create session and content to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = scoped_session(DBSession)


# show all restaurants
@app.route('/')
@app.route('/restaurants/')
def showRestaurants():
    restaurants = session.query(Restaurant)
    # authentication check
    if 'username' not in login_session:
        return render_template('restaurantspublic.html',
                               restaurants=restaurants)
    return render_template('restaurants.html',
                           restaurants=restaurants)


# create new restaurant
@app.route('/restaurants/new/', methods=['GET', 'POST'])
def newRestaurant():
    # authentication check
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))

    # create new restaurant
    if request.method == 'POST':
        new_restaurant = Restaurant(name=request.form['name'],
                                    user_id=login_session['user_id'])
        session.add(new_restaurant)
        session.commit()
        flash('new restaurant created!')
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newRestaurant.html')


# edit restaurant
@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    # authentication check
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    edit_restaurant = session.query(Restaurant).filter_by(
        id=restaurant_id).one()

    # authorisation check
    creator = getUserInfo(edit_restaurant.user_id)
    if creator.id != login_session['user_id']:
        flash('You are not allowed to edit this restaurant')
        return redirect(url_for('showRestaurants'))

    # edit restaurant
    if request.method == 'POST':
        if request.form['name']:
            edit_restaurant.name = request.form['name']
        session.add(edit_restaurant)
        session.commit()
        flash('restaurant updated!')
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editRestaurant.html',
                               restaurant=edit_restaurant)


# delete restaurant
@app.route('/restaurants/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    # authentication check
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    delete_restaurant = session.query(Restaurant).filter_by(
        id=restaurant_id).one()

    # authorisation check
    creator = getUserInfo(delete_restaurant.user_id)
    if creator.id != login_session['user_id']:
        flash('You are not allowed to delete this restaurant')
        return redirect(url_for('showRestaurants'))

    # delete restaurant
    if request.method == 'POST':
        session.delete(delete_restaurant)
        session.commit()
        flash('restaurant deleted!')
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleteRestaurant.html',
                               restaurant=delete_restaurant)


# show restaurant menu
@app.route('/restaurants/<int:restaurant_id>/')
@app.route('/restaurants/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    # authentication check
    if 'username' not in login_session:
        return render_template('menupublic.html',
                               restaurant=restaurant,
                               items=menu_items)
    return render_template('menu.html',
                           restaurant=restaurant,
                           items=menu_items)


# create restaurant menu
@app.route('/restaurants/<int:restaurant_id>/menu/new/',
           methods=['GET', 'POST'])
def newMenu(restaurant_id):
    # authentication check
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        new_menu_item = MenuItem(name=request.form['name'],
                                 course=request.form['course'],
                                 description=request.form['description'],
                                 price=request.form['price'],
                                 restaurant_id=restaurant_id,
                                 user_id=login_session['user_id']
                                 )
        session.add(new_menu_item)
        session.commit()
        flash('new item created!')
        return redirect(url_for('showMenu',
                        restaurant_id=restaurant.id))
    else:
        return render_template('newMenuItem.html',
                               restaurant=restaurant)


# edit restaurant menu
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit/',
           methods=['GET', 'POST'])
def editMenu(restaurant_id, menu_id):
    # authentication check
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    edit_menu_item = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id, id=menu_id).one()

    # authorisation check
    creator = getUserInfo(restaurant.user_id)
    if creator.id != login_session['user_id']:
        flash('You are not allowed to edit this menu item')
        return redirect(url_for('showMenu',
                        restaurant_id=restaurant.id))

    # edit menu item
    if request.method == 'POST':
        if request.form['name']:
            edit_menu_item.name = request.form['name']
        if request.form['course']:
            edit_menu_item.course = request.form['course']
        if request.form['description']:
            edit_menu_item.description = request.form['description']
        if request.form['price']:
            edit_menu_item.price = request.form['price']
        session.add(edit_menu_item)
        session.commit()
        flash('item updated!')
        return redirect(url_for('showMenu',
                        restaurant_id=restaurant.id))
    else:
        return render_template('editMenuItem.html',
                               restaurant=restaurant,
                               item=edit_menu_item)


# delete restaurant menu
@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete/',
           methods=['GET', 'POST'])
def deleteMenu(restaurant_id, menu_id):
    # authentication check
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    delete_menu_item = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id, id=menu_id).one()

    # authorisation check
    creator = getUserInfo(restaurant.user_id)
    if creator.id != login_session['user_id']:
        flash('You are not allowed to delete this menu item')
        return redirect(url_for('showMenu',
                        restaurant_id=restaurant.id))

    # delete menu item
    if request.method == 'POST':
        session.delete(delete_menu_item)
        session.commit()
        flash('item deleted!')
        return redirect(url_for('showMenu',
                        restaurant_id=restaurant.id))
    else:
        return render_template('deleteMenuItem.html',
                               restaurant=restaurant,
                               item=delete_menu_item)


# JSON APIs implementation
@app.route('/JSON/')
@app.route('/restaurants/JSON/')
def showRestaurantsJSON():
    restaurants = session.query(Restaurant)
    return jsonify(Restaurant=[i.serialize for i in restaurants])


@app.route('/restaurants/<int:restaurant_id>/JSON/', methods=['GET', 'POST'])
def showRestaurantJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    return jsonify(Restaurant=[restaurant.serialize])


@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
def showMenuJSON(restaurant_id):
    menu_items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return jsonify(MenuItem=[i.serialize for i in menu_items])


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON/',
           methods=['GET', 'POST'])
def showMenuItemJSON(restaurant_id, menu_id):
    menu_item = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id, id=menu_id).one()
    return jsonify(Restaurant=[menu_item.serialize])


# get client id from downloded json file from Google Credentials
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


# create anti-forgery state token
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
                                  string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# create server-side function to validade login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # if it's a new user, create a new user in the database
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += ' -webkit-border-radius: 150px;-moz-border-radius: 150px;">'
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


# create sign out function
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token='
    url = url + login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        flash('Successfully disconnected!')
        return redirect(url_for('showRestaurants'))
    else:
        flash('Failed to revoke token for given user.')
        return redirect(url_for('showRestaurants'))


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
