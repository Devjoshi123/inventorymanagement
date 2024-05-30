
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_restful import Api
from models import db, User, Inventory
from api.inventory import InventoryAPI
from ml.predict import predict_inventory

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

api = Api(app)
api.add_resource(InventoryAPI, '/api/inventory')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def before_first_request():
    def create_tables():
     db.create_all()
    pass


@app.route('/')
@login_required
def index():
    inventory_items = Inventory.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', inventory_items=inventory_items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
@login_required
def add_inventory():
    item_name = request.form['item_name']
    quantity = request.form['quantity']
    new_item = Inventory(item_name=item_name, quantity=quantity, user_id=current_user.id)
    db.session.add(new_item)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
@login_required
def delete_inventory(id):
    item = Inventory.query.get(id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_inventory(id):
    item = Inventory.query.get(id)
    if item.user_id != current_user.id:
        return redirect(url_for('index'))
    if request.method == 'POST':
        item.item_name = request.form['item_name']
        item.quantity = request.form['quantity']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update.html', item=item)

@app.route('/predict', methods=['GET'])
@login_required
def predict():
    prediction = predict_inventory(current_user.id)
    return render_template('predict.html', prediction=prediction)

if __name__ == '__main__':
    app.run(debug=True)
