from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from link import *
from api.sql import *
import imp, random, os, string
from werkzeug.utils import secure_filename
from flask import current_app

UPLOAD_FOLDER = 'static/product'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

manager = Blueprint('manager', __name__, template_folder='../templates')

def config():
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    config = current_app.config['UPLOAD_FOLDER'] 
    return config

@manager.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return redirect(url_for('manager.productManager'))

@manager.route('/productManager', methods=['GET', 'POST'])
@login_required
def productManager():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('index'))
        
    if 'delete' in request.values:
        pid = request.values.get('delete')
        data = Record.delete_check(pid)
        
        if(data != None):
            flash('failed')
        else:
            data = Product.get_product(pid)
            Product.delete_product(pid)
    
    elif 'edit' in request.values:
        pid = request.values.get('edit')
        return redirect(url_for('manager.edit', pid=pid))
    
    book_data = book()
    return render_template('productManager.html', book_data = book_data, user=current_user.name)

def book():
    book_row = Product.get_all_product()
    book_data = []
    for i in book_row:
        book = {
            '商品編號': i[0],
            '商品名稱': i[1],
            '商品售價': i[2],
            '商品類別': i[3]
        }
        book_data.append(book)
    return book_data

@manager.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = ""
        while(data != None):
            number = str(random.randrange( 10000, 99999))
            en = random.choice(string.ascii_letters)
            pid = en + number
            data = Product.get_product(pid)

        pname = request.values.get('pname')
        price = request.values.get('price')
        category = request.values.get('category')
        pdesc = request.values.get('description')

        # 檢查是否正確獲取到所有欄位的數據
        if pname is None or price is None or category is None or pdesc is None:
            flash('所有欄位都是必填的，請確認輸入內容。')
            return redirect(url_for('manager.productManager'))

        # 檢查欄位的長度
        if len(pname) < 1 or len(price) < 1:
            flash('商品名稱或價格不可為空。')
            return redirect(url_for('manager.productManager'))


        if (len(pname) < 1 or len(price) < 1):
            return redirect(url_for('manager.productManager'))
        
        Product.add_product(
            {'pid' : pid,
            'pname' : pname,
            'price' : price,
            'category' : category,
            'pdesc':pdesc,
            'mid': current_user.id
            }
        )

        return redirect(url_for('manager.productManager'))

    return render_template('productManager.html')

@manager.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('bookstore'))

    if request.method == 'POST':
        Product.update_product(
            {
            'pname' : request.values.get('pname'),
            'price' : request.values.get('price'),
            'category' : request.values.get('category'), 
            'pdesc' : request.values.get('description'),
            'pid' : request.values.get('pid')
            }
        )
        
        return redirect(url_for('manager.productManager'))

    else:
        product = show_info()
        return render_template('edit.html', data=product)


def show_info():
    pid = request.args['pid']
    data = Product.get_product(pid)
    pname = data[1]
    price = data[2]
    category = data[3]
    description = data[4]

    product = {
        '商品編號': pid,
        '商品名稱': pname,
        '單價': price,
        '類別': category,
        '商品敘述': description
    }
    return product


@manager.route('/orderManager', methods=['GET', 'POST'])
@login_required
def orderManager():
    if request.method == 'POST':
        pass
    else:
        order_row = TRANSACTION.get_order()
        order_data = []
        for i in order_row:
            order = {
                '訂單編號': i[0],
                '訂購人': i[1],
                '訂單總價': i[2],
                '訂單時間': i[3],
                '訂單狀態': i[4]
            }
            order_data.append(order)
            
        orderdetail_row = TRANSACTION.get_orderdetail()
        order_detail = []

        for j in orderdetail_row:
            orderdetail = {
                '訂單編號': j[0],
                '商品名稱': j[1],
                '商品單價': j[2],
                '訂購數量': j[3]
            }
            order_detail.append(orderdetail)

    return render_template('orderManager.html', orderData = order_data, orderDetail = order_detail, user=current_user.name)


@manager.route('/update_order_status', methods=['POST'])
@login_required
def update_order_status():
    # 只允許 manager 更新狀態
    if current_user.role == 'user':
        flash('No permission')
        return redirect(url_for('manager.orderManager'))

    oid = request.form.get('oid')
    stage = request.form.get('stage')

    if not oid or stage is None:
        flash('invalid')
        return redirect(url_for('manager.orderManager'))

    try:
        TRANSACTION.update_stage(oid, stage)
        flash('updated')
    except Exception as e:
        print('update_order_status error:', e)
        flash('failed')

    return redirect(url_for('manager.orderManager'))

@manager.route('/userManager', methods=['GET', 'POST'])
@login_required
def userManager():
    user_data = []

    if request.method == 'POST':
        if 'delete' in request.values:
            uid = request.values.get('delete')
            if str(uid) == str(current_user.id):
                flash('cannot_delete')
            else:
                orders = Member.get_order(uid)
                if orders is not None and len(orders) > 0:
                    flash('failed')
                else:
                    try:
                        Cart.clear_cart(uid)
                    except Exception:
                        pass
                    User_List.delete_user(uid)
        elif 'edit' in request.values:
            uid = request.values.get('edit')
            return redirect(url_for('manager.userEdit', uid=uid))
            


    user_row = User_List.get_user()
    for i in user_row:
        user = {
            '使用者編號': i[0],
            '使用者名稱': i[1],
            '使用者帳號': i[2],
            '身分': i[3]
        }
        user_data.append(user)

    return render_template('userManager.html', userData=user_data, user=current_user.name, current_id=current_user.id)


@manager.route('/userEdit', methods=['GET', 'POST'])
@login_required
def userEdit():
    if request.method == 'POST':
        mid = request.form.get('mid')
        name = request.form.get('name')
        account = request.form.get('account')
        identity = request.form.get('identity')

        if identity not in ('user', 'manager'):
            flash('Invalid identity')
            return redirect(url_for('manager.userManager'))

        User_List.update_user({'mid': mid, 'name': name, 'account': account, 'identity': identity})
        return redirect(url_for('manager.userManager'))

    else:
        uid = request.args.get('uid')
        if uid is None:
            return redirect(url_for('manager.userManager'))

        data = User_List.get_user_by_mid(uid)
        if data is None:
            flash('User not found')
            return redirect(url_for('manager.userManager'))

        user = {
            'mid': data[0],
            'name': data[1],
            'account': data[2],
            'identity': data[3]
        }

        return render_template('userEdit.html', data=user, user=current_user.name)


@manager.route('/reviewManager', methods=['GET', 'POST'])
@login_required
def reviewManager():
    # 顯示評論並支援刪除
    if request.method == 'POST':
        if 'delete' in request.values:
            rno = request.values.get('delete')
            try:
                Review.delete_review(rno)
            except Exception as e:
                # 若刪除失敗則顯示錯誤訊息
                flash('failed')

    review_row = Review.get_review()
    book_data = []
    for i in review_row:
        review = {
            '評論編號': i[0],
            '商品名稱': i[1],
            '使用者名稱': i[2],
            '評論評分': i[3],
            '評論內容': i[4],
            '評論時間': i[5]
        }
        book_data.append(review)

    return render_template('reviewManager.html', book_data=book_data, user=current_user.name)