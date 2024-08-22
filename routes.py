from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import User, AuctionItem, Bid

main = Blueprint('main', __name__)

@main.route('/')
def home():
    auction_items = AuctionItem.query.all()
    return render_template('home.html', auction_items=auction_items)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('main.home'))
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.home'))
        flash('Invalid email or password.')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/create_auction', methods=['GET', 'POST'])
@login_required
def create_auction():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        starting_bid = float(request.form['starting_bid'])
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d %H:%M')
        auction_item = AuctionItem(title=title, description=description, starting_bid=starting_bid,
                                   end_date=end_date, owner_id=current_user.id)
        db.session.add(auction_item)
        db.session.commit()
        return redirect(url_for('main.home'))
    return render_template('manage_auction.html', action='Create')

@main.route('/update_auction/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_auction(item_id):
    auction_item = AuctionItem.query.get_or_404(item_id)
    if request.method == 'POST':
        auction_item.title = request.form['title']
        auction_item.description = request.form['description']
        auction_item.starting_bid = float(request.form['starting_bid'])
        auction_item.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d %H:%M')
        db.session.commit()
        return redirect(url_for('main.home'))
    return render_template('manage_auction.html', action='Update', auction_item=auction_item)

@main.route('/delete_auction/<int:item_id>')
@login_required
def delete_auction(item_id):
    auction_item = AuctionItem.query.get_or_404(item_id)
    if auction_item.owner_id == current_user.id:
        db.session.delete(auction_item)
        db.session.commit()
    return redirect(url_for('main.home'))

@main.route('/auction/<int:item_id>', methods=['GET', 'POST'])
def auction_item(item_id):
    auction_item = AuctionItem.query.get_or_404(item_id)
    if request.method == 'POST':
        bid_amount = float(request.form['bid_amount'])
        if bid_amount > auction_item.current_bid:
            bid = Bid(amount=bid_amount, user_id=current_user.id, auction_item_id=auction_item.id)
            auction_item.current_bid = bid_amount
            db.session.add(bid)
            db.session.commit()
            return redirect(url_for('main.auction_item', item_id=item_id))
    return render_template('auction_item.html', auction_item=auction_item)

@main.route('/profile')
@login_required
def profile():
    auction_items = AuctionItem.query.filter_by(owner_id=current_user.id).all()
    bids = Bid.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', auction_items=auction_items, bids=bids)
