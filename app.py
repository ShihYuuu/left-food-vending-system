from asyncio.windows_events import NULL
from flask import Flask, request, session, render_template, jsonify, url_for, redirect
import datetime
import json
from project import app, db
# from project.userManager import User

app = Flask(__name__)

class User():

    def __init__(self, account, name, role):
        self.account = account
        self.name = name
        self.role = role
        self.date =  datetime.date.today() # datetime.date(2022, 5, 7)


user = None
homepage = None
cart = []

# 主頁 登入頁面
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')

# 登入後的畫面
@app.route('/home', methods=['GET','POST'])
def login():
    global user, homepage
    
    if request.method == 'POST':
        account = request.form['account']
        password = request.form['password']
        
        role = db.role_type(account)
        if role is not None:
            u = db.user_info(account)
            
            if u['Password'][0] == password:
                user = User(account, u['Name'][0], role)
                
                if role == 'Manager':
                    homepage = render_template('manager.html', name = user.name, date = user.date)
                    return homepage

                if u['Status'][0] == 'pending':
                    alert = '<font color="red">您的帳號還未審核通過</font>'
                    return render_template('home.html', alert = alert)

                if role == 'Seller':
                    homepage = render_template('seller.html', name = user.name, date = user.date)  
                elif role == 'Buyer':
                    homepage = render_template('buyer.html', name = user.name, date = user.date)

                return homepage

            else:
                alert = '<font color="red">Password is wrong</font>'
                return render_template('home.html', alert = alert)
        else:
            alert = '<font color="red">No account</font>'
            return render_template('home.html', alert = alert)
    else:
        return homepage

# 註冊畫面
@app.route('/enroll', methods=['GET','POST'])
def enroll():
    return render_template('enroll.html')

# 取得註冊資料
@app.route('/enroll_info', methods=['GET','POST'])
def enroll_info():

    role = request.form.getlist('role')[0]
    name = request.form['name']
    phone = request.form['phone']
    account = request.form['account']
    password = request.form['password']

    if role == 'buyer':
        db.create_user(account, password, name, phone, 'Buyer')
    elif role == 'seller':
        db.create_user(account, password, name, phone, 'Seller')
    
    return redirect(url_for('home'))

# 登出 回到主畫面
@app.route('/logout')
def logout():
    return redirect(url_for('home'))
# 個人 帳號頁面
@app.route('/account', methods=['GET','POST'])
def account():
    u = db.user_info(user.account)
    text_content = ''
    
    text_content += f'帳號：<div class="form-group"><input class="form-control" type="text" name="account" value="{u["Account"][0]}" disabled="disabled"></div>'
    text_content += f'密碼：<div class="form-group"><input class="form-control" type="text" name="password" value="{u["Password"][0]}"></div>'
    text_content += f'姓名：<div class="form-group"><input class="form-control" type="text" name="name" value="{u["Name"][0]}"></div>'
    text_content += f'電話：<div class="form-group"><input class="form-control" type="text" name="phone" value="{u["Phone"][0]}"></div>'
    # <div class="form-group"><input class="form-control" type="text" name="phone" value="{u["Phone"][0]}">></div>

    return render_template('account_self.html',
                            role = user.role, text_content = text_content)

# 個人 修改帳號
@app.route('/account_revise', methods=['GET','POST'])
def account_revise():

    password = request.form['password']
    name = request.form['name']
    phone = request.form['phone']
    
    if user.role == 'Buyer':
        db.revise_user(user.account, password, name, phone, 'Buyer')
    elif user.role == 'Seller':  
        db.revise_user(user.account, password, name, phone, 'Seller')

    return redirect(url_for('account'))

# manager 審核帳號
@app.route('/account_pending', methods=['GET', 'POST'])
def account_pending():

    pending_list = db.get_pending_list()
    
    table_content = ''
    selected_col = ['Account', 'Name', 'Phone']
    for role in pending_list:
        for i in range(len(pending_list[role]['Account'])):
            
            table_content += '<tr>'
            for col_name in selected_col:
                table_content += f'<td>{pending_list[role][col_name][i]}</td>'

            table_content += f'<td>{role}</td>'
            table_content += f'<td><form method="post" action="/approve">\
                                <button class="btn btn-primary" name=account value="{pending_list[role]["Account"][i]}"></i>通過</button>\
                                </form></td>\
                                <td><form method="post" action="/reject">\
                                <button class="btn btn-primary" name=account value="{pending_list[role]["Account"][i]}"></i>拒絕</button>\
                                </form>\
                                </td>'
                            # <button name="account" value="{pending_list[role]["Account"][i]}">通過</button>\
            table_content += '</tr>'

    # <tr> 
    #        <td>
    #            <form method="post" action="" >
    #             <button name="" value="">按鈕</button>
    #            </form>
    #        </td>
    # </tr>
    return render_template('pending.html',
                            table_content=table_content)

# manager 通過帳號
@app.route('/approve', methods=['GET', 'POST']) 
def approve():

    account = request.form['account']
    db.approve_account(user.account, account)
    return redirect(url_for('account_pending'))

# manager 拒絕帳號
@app.route('/reject', methods=['GET', 'POST'])
def reject():

    account = request.form['account']
    db.reject_account(account)
    return redirect(url_for('account_pending'))

# manager 管理帳號
@app.route('/account_manage', methods=['GET', 'POST'])
def account_manage():
    return render_template('management.html')

# manager 帳號資料
@app.route('/management', methods=['GET', 'POST'])
def management():

    role = request.form['role']
    table_content = ''

    if role == 'manager':
        table_content += '<tr>'
        table_content += '<td>帳號</td><td>密碼</td><td>姓名</td><td>權限</td>'
        table_content += '</tr>'

        selected_col = ['Account', 'Password', 'Name', 'Permission']
        info = db.get_role_info('Manager')

        for i in range(len(info['Account'])):
            table_content += "<tr>"
            for col_name in selected_col:
                table_content += f"<td>{info[col_name][i]}</td>"

            table_content += "</tr>"

    elif role == 'seller':
        table_content += '<tr>'
        table_content += '<td>帳號</td><td>密碼</td><td>商店</td><td>電話</td><td>狀態</td>'
        table_content += '</tr>'

        selected_col = ['Account', 'Password', 'Name', 'Phone', 'Status']
        info = db.get_role_info('Seller')

        for i in range(len(info['Account'])):
            table_content += "<tr>"
            for col_name in selected_col:
                table_content += f"<td>{info[col_name][i]}</td>"

            table_content += "</tr>"

    elif role == 'buyer':
        table_content += '<tr>'
        table_content += '<td>帳號</td><td>密碼</td><td>姓名</td><td>電話</td><td>狀態</td>'
        table_content += '</tr>'

        selected_col = ['Account', 'Password', 'Name', 'Phone', 'Status']
        info = db.get_role_info('Buyer')

        for i in range(len(info['Account'])):
            table_content += "<tr>"
            for col_name in selected_col:
                table_content += f"<td>{info[col_name][i]}</td>"

            table_content += "</tr>"


    return render_template('account_info.html',
                            role = role, table_content = table_content)

# manager 新增管理員
@app.route('/new_manager', methods=['GET', 'POST'])
def new_manager():
    return render_template('enroll_manager.html')


# seller 管理今日剩食
@app.route('/food_data', methods=['GET','POST'])
def food_data():

    food = db.food_today(user.account, user.date)

    food['DPrice'] = [round(p*d) for p,d in zip(food['Price'], food['Discount'])]
    selected_col = ['FoodItem', 'DPrice', 'Quantity']

    table_content = ""

    for i in range(len(food['DPrice'])):
        table_content += "<tr>"
        for col_name in selected_col:
            table_content += f"<td>{food[col_name][i]}</td>"

        table_content += "</tr>"

    # <tr>
    #     <td>aa</td>
    #     <td>bb</td>
    # </tr>

    # <tr>
    #     <td>cc</td>
    #     <td>dd</td>
    # </tr>

    return render_template('food_data.html',
                            date = user.date, table_content=table_content)

@app.route('/food_add', methods=['GET','POST'])
def food_add():
    return render_template('food_add.html')

@app.route('/food_add_info', methods=['GET','POST'])
def food_add_info():

    food = request.form['food']
    quantity = request.form['quantity']
    price = request.form['price']
    discount = request.form['discount']

    if (food != '') & (quantity != '') & (price != '') & (discount != ''):
        db.add_food(food, price, discount, quantity, user.account, user.date)
    else:
        warning = '<font color="red">不可輸入空值</font>'
        return render_template('food_add.html', warning = warning)

    return redirect(url_for('food_data'))

@app.route('/food_delete', methods=['GET','POST'])
def food_delete():

    food = db.food_today(user.account, user.date)

    checkbox_content = '<p>'
    for i in range(len(food['ID'])):
        checkbox_content += f'<div><input type="checkbox" class="form-check-input" id={food["ID"][i]} name="delete_food" value={food["ID"][i]}>'
        checkbox_content += f'<label class="form-check-label" for="dropdownCheck"><h4>{food["FoodItem"][i]}</h4></label></div>'
        
        # <input type="checkbox" class="form-check-input" id="dropdownCheck">
        # <label class="form-check-label" for="dropdownCheck">

    checkbox_content += '</p>'

    # <input type="checkbox" id="" name="" value="">
    # <label for="cbox"></label>

    return render_template('food_delete.html', checkbox_content=checkbox_content)

@app.route('/food_delete_info', methods=['GET','POST'])
def food_delete_info():
    delete_list = request.form.getlist('delete_food')

    # print(delete_list)
    for i in delete_list:
        db.delete_food(i)

    return redirect(url_for('food_data'))

# seller 查詢今日訂單
@app.route('/order', methods=['GET', 'POST'])
def order():

    order = db.order_today(user.account, user.date)

    selected_col = ['FoodItem', 'Quantity']
    table_content = ""
    id = 0
    # print(order)
    for i in range(len(order['Buyer'])):
        id += 1
        table_content += "<tr>"
        table_content += f"<td>{id}</td>"
        table_content += f"<td>&nbsp;{db.buyer[order['Buyer'][i]]}</td>"
        
        for col_name in selected_col:
            table_content += f"<td>{order[col_name][i]}</td>"

        table_content += "</tr>"
    
    return render_template('order_today.html',
                            date = user.date, table_content = table_content)

# Buyer 查詢剩食
@app.route('/search', methods=['GET', 'POST'])
def search():

    table_content = ''
    if request.method == 'POST':
        sstore = request.form['search_store']
        sfood = request.form['search_food']

        if (sstore == '') & (sfood == ''):
            food = db.food_today('*', user.date)
        else:
            food = db.search(sstore, sfood, user.date)
    else:
        food = db.food_today('*', user.date)

    food['DPrice'] = [round(p*d) for p,d in zip(food['Price'], food['Discount'])]
    selected_col = ['FoodItem', 'DPrice', 'Quantity']

    table_content = ""

    for i in range(len(food['DPrice'])):
        table_content += "<tr>"
        table_content += f"<td>&nbsp;{db.seller[food['Seller'][i]]}</td>"
        for col_name in selected_col:
            table_content += f"<td>&nbsp;{food[col_name][i]}</td>"
        table_content += f'<td><button class="btn-outline-primary" onclick="add_to_cart({food["ID"][i]})"><i class="ti-heart"></i> 加入</button></td>'
        # <button onclick="add_to_cart({food["ID"][i]})">加入</button>
        
        table_content += "</tr>"


    return render_template('search.html', 
                            date = user.date, table_content = table_content)

# buyer 新增到購物車
@app.route('/add_to_cart', methods=['GET', 'POST'])
def add_to_cart():
    global cart

    id = request.get_json()['id']
    quantity = int(request.get_json()['quantity'])
    cart.append([id, quantity])
    # print(cart)
    return 'true'

@app.route('/cart_info', methods=['GET', 'POST'])
def cart_info():

    total_amount = 0
    table_content = ''

    for item in cart:
        table_content += '<tr>'
        id = item[0]
        q = item[1]

        info = db.get_food_by_id(id)
        table_content += f'<td>{info[5]}</td>\
                           <td>{info[1]}</td>\
                           <td>{info[2] * info[3]}</td>\
                           <td>{q}</td>'
        table_content += '</tr>'
        total_amount += round(info[2] * info[3]) * q

    return render_template('cart.html',
                            date = user.date,
                            table_content = table_content,
                            total_amount = total_amount)

# buyer 下訂單
@app.route('/place_order', methods=['GET', 'POST'])
def place_order():
    global cart
    
    total_amount = 0

    oid = db.add_order(user.date, user.account)
    # print(oid)
    for item in cart:
        
        id = item[0]
        q = item[1]
        info = db.get_food_by_id(id)
        print(info)

        total_amount += round(info[2] * info[3]) * q
        db.add_food_item(oid, info[1],	q, info[5])
        db.update_food_quantity(info[0], info[4]-q)

    db.update_amount(oid, total_amount)
    cart.clear()

    return redirect(url_for('cart_info'))

@app.route('/record', methods=['GET', 'POST'])
def record():
    # print(user.role)
    if user.role == 'Buyer':
        role = '賣家'
        service = 'Seller'
        account = db.seller
    elif user.role == 'Seller':
        role = '買家'
        service = 'Buyer'
        account = db.buyer

    table_content = f"<tr><td>&nbsp;編號</td>\
                    <td>&nbsp;日期</td>\
                    <td>&nbsp;品項</td>\
                    <td>&nbsp;數量</td>\
                    <td>&nbsp;{role}</td></tr>"

    order = db.order_record(user.role, user.account)
    selected_col = ['Date', 'FoodItem', 'Quantity']
    id = 0
    for i in range(len(order['Date'])):
        id += 1
        table_content += "<tr>"
        table_content += f"<td>{id}</td>"
        for col_name in selected_col:
            table_content += f"<td>{order[col_name][i]}</td>"

        table_content += f"<td>&nbsp;{account[order[service][i]]}</td>"

        table_content += "</tr>"

    return render_template('order_record.html', table_content = table_content)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)