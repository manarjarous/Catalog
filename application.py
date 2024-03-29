from flask import Flask, render_template, request
from flask import redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc
from database_setup import Category, Base, CategoryItem, User
from flask import session as login_session
from functools import wraps
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


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
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
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
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user '
                                            'is already connected.'),
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

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;"> '
    print "done!"
    return output

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
    except SQLAlchemyError:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user '
                                            'not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for'
                                            ' given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('showlogin'))
    return wrap


@app.route('/catalog/JSON')
def categoriesJSON():
    categories = session.query(Category).options(
        joinedload(Category.items)).all()
    return jsonify(Catalog=[dict(c.serialize, Items=[i.serialize
                                                     for i in c.items])
                            for c in categories])


@app.route('/catalog/<category_name>/JSON')
def categorieItemsJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(CategoryItem).filter_by(category_id=category.id)
    return jsonify(Items=[i.serialize for i in items])


@app.route('/catalog/<category_name>/<item_title>/JSON')
def itemJSON(category_name, item_title):
    Item = session.query(CategoryItem).filter_by(title=item_title).one()
    return jsonify(Item=Item.serialize)


@app.route('/')
@app.route('/catalog')
def showcategories():
    categories = session.query(Category).all()
    lastestItems = session.query(CategoryItem).order_by(
        desc(CategoryItem.created_at)).limit(7)
    if 'username' not in login_session:
        return render_template('publicCategory.html', categories=categories,
                               lastestItems=lastestItems)
    else:
        return render_template('category.html', categories=categories,
                               lastestItems=lastestItems)


@app.route('/catalog/newCategory', methods=['GET', 'POST'])
@login_required
def createCategory():
    if request.method == 'POST':
        newCategory = Category(name=request.form['name'],
                               user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('addItem'))
    else:
        return render_template('newCategory.html')


@app.route('/catalog/<category_name>/')
def showItems(category_name):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(CategoryItem).filter_by(category_id=category.id)
    creator = getUserInfo(category.user_id)
    return render_template('categoryItems.html', categories=categories,
                           category=category, items=items)


@app.route('/catalog/newitem', methods=['GET', 'POST'])
@login_required
def addItem():
    categories = session.query(Category).filter_by(
        user_id=login_session['user_id']).all()
    if request.method == 'POST':
        category = session.query(Category).filter_by(
            name=request.form.get('categoryselect')).one()
        creator = getUserInfo(category.user_id)
        newItem = CategoryItem(title=request.form['title'],
                               description=request.form['description'],
                               category_id=category.id,
                               user_id=category.user_id)
        if creator.id != login_session['user_id']:
            user_id = getUserID(login_session['email'])
            flash("You are not authorized to add new Item into."
                  "You need to create own category")
            return redirect(url_for('createCategory'))
        session.add(newItem)
        session.commit()
        return redirect(url_for('showItems', category_name=category.name))
    else:
        return render_template('newItem.html', categories=categories)


@app.route('/catalog/<category_name>/<item_title>/')
def showItem(item_title, category_name):
    item = session.query(CategoryItem).filter_by(title=item_title).one()
    category = session.query(Category).filter_by(id=item.category_id).one()
    creator = getUserInfo(category.user_id)
    if 'username' not in login_session or \
            creator.id != login_session['user_id']:
        return render_template('publicItem.html', item=item, category=category)
    else:
        return render_template('item.html', item=item, category=category)


@app.route('/catalog/<category_name>/<item_title>/edit',
           methods=['GET', 'POST'])
@login_required
def editItem(item_title, category_name):
    editedItem = session.query(CategoryItem).filter_by(title=item_title).one()
    category = session.query(Category).filter_by(
        id=editedItem.category_id).one()
    categories = session.query(Category).filter_by(
        user_id=login_session['user_id']).all()
    creator = getUserInfo(category.user_id)
    if request.method == 'POST':
        if creator.id != login_session['user_id']:
            flash("You are not authorized to edit this Item."
                  "You need to select another Item")
            return redirect(url_for('showItems', category_name=category_name))
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('showItems', category_name=category_name))
    else:
        return render_template('editItem.html', item=editedItem,
                               category=category, categories=categories)


@app.route('/catalog/<category_name>/<item_title>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteItem(item_title, category_name):
    itemToDelete = session.query(
        CategoryItem).filter_by(title=item_title).one()
    category = session.query(Category).filter_by(
        id=itemToDelete.category_id).one()
    creator = getUserInfo(category.user_id)
    if request.method == 'POST':
        if creator.id != login_session['user_id']:
            flash("You are not authorized to delete this Item."
                  "You need to select another Item")
            return redirect(url_for('showItems', category_name=category_name))
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('showItems', category_name=category_name))
    else:
        return render_template('deleteItem.html', item=itemToDelete,
                               category=category)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
