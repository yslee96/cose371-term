import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
connect = psycopg2.connect("host=postgres dbname=db user=postgres password=2015150220")
cur = connect.cursor() 

@app.route('/')
def main():
    return render_template("main.html")

@app.route('/register', methods=['post'])
def register():
    id = request.form["id"]
    password = request.form["password"]
    send = request.form["send"]
    if send == "login":
        cur.execute("SELECT * FROM users WHERE id = '{}' AND password = '{}';".format(id, password))
        login_result = cur.fetchall()
        if login_result: # admin 추가
            return redirect(url_for('login_action', user_id = id))
        return render_template("login_fail.html")  
    elif send == "sign up":
        # need to check redundancy first(ID_collision)
        cur.execute("SELECT * FROM users WHERE id = '{}';".format(id))
        collision_result = cur.fetchall()
        if not collision_result:
            # if there's no collision, proceed to signing up
            cur.execute("INSERT INTO users VALUES('{}', '{}');".format(id, password))
            cur.execute("INSERT INTO account VALUES('{}', 10000, 'beginner');".format(id))
            connect.commit()
        else:
            # there is collision
            return render_template("ID_collision.html")
    return render_template("main.html")

@app.route('/login_action/<user_id>')
def login_action(user_id):
    cur.execute("SELECT balance, rating FROM account WHERE id ='{}';".format(user_id))
    user_info = cur.fetchall()
    cur.execute("WITH code_cnt(code, cnt) AS (SELECT code, count(code) FROM trade GROUP BY code), \
                max_cnt(value) AS (SELECT max(cnt) FROM code_cnt), \
                max_code(code) AS (SELECT code FROM code_cnt, max_cnt WHERE code_cnt.cnt = max_cnt.value) \
                SELECT type FROM category, max_code WHERE category.code = max_code.code;")
    popular_category = cur.fetchall()
    cur.execute("WITH buying_cnt(buyer,cnt) AS (SELECT buyer,count(buyer) FROM trade GROUP BY buyer), \
                max_cnt(value) AS (SELECT max(cnt) FROM buying_cnt) \
                SELECT buyer FROM buying_cnt, max_cnt WHERE buying_cnt.cnt = max_cnt.value;")
    best_buyer = cur.fetchall()
    cur.execute("WITH selling_cnt(seller,cnt) AS (SELECT seller,count(seller) FROM trade GROUP BY seller), \
                max_cnt(value) AS (SELECT max(cnt) FROM selling_cnt) \
                SELECT seller FROM selling_cnt, max_cnt WHERE selling_cnt.cnt = max_cnt.value;")    
    best_seller = cur.fetchall()
    site_info = popular_category + best_buyer + best_seller
    cur.execute("SELECT * FROM items;")
    item_info = cur.fetchall()
    return render_template("login_success.html", id = user_id, u_info = user_info, s_info = site_info, items = item_info)

@app.route('/return', methods=['post'])
def re_turn():
    return render_template("main.html")

@app.route('/logout')
def logout():
    return redirect(url_for('main'))

@app.route('/admin_function', methods=['post'])
def admin_function():
    send = request.form["send"]
    
    cur.execute("SELECT * FROM category;")
    category_list = cur.fetchall()
    cur.execute("SELECT * FROM users;")
    user_list = cur.fetchall()
    cur.execute("SELECT * FROM trade;")
    trade_list = cur.fetchall() 
    return render_template('admin_page.html', function = send, categories = category_list, users = user_list, trades = trade_list)

@app.route('/admin_action', methods=['post'])
def admin_action():
    send = request.form["send"]
    code_num = request.form["code"]
    code_type = request.form["type"]

    if send == "cancel":
        return redirect(url_for('login_action', user_id = 'admin'))   

    cur.execute("SELECT code FROM category WHERE code = '{}';".format(code_num))
    num_result = cur.fetchall()
    cur.execute("SELECT type FROM category WHERE type = '{}';".format(code_type))
    type_result = cur.fetchall()
    
    #check constraints
    if not code_num or not code_num.isdigit() or len(code_num)>2:
        return render_template('admin_action_fail.html', cause='num_invalid')
    if not code_type or code_type.isdigit() or len(code_type)>20:
        return render_template('admin_action_fail.html', cause='type_invalid')

    #check redundancy
    if num_result:
        return render_template('admin_action_fail.html', cause='num_collision')
    if type_result:
        return render_template('admin_action_fail.html', cause='type_collision')

    cur.execute("INSERT INTO category VALUES('{}', '{}');".format(code_num, code_type))
    connect.commit()
    cur.execute("SELECT * FROM category;")
    category_list = cur.fetchall()
    return render_template('admin_page.html', function = 'add category', categories = category_list)

@app.route('/admin_collect', methods=['post'])
def admin_collect():
    send = request.form["send"]
    monthly_fee = request.form["fee"]

    if send == 'cancel':
        return redirect(url_for('login_action', user_id = 'admin'))

    cur.execute("SELECT count(id) FROM account;")
    user_cnt = cur.fetchall()
    cur.execute("SELECT id, balance FROM account WHERE balance < '{}';".format(monthly_fee))
    user_unpayed = cur.fetchall()
    admin_revenue = int(monthly_fee) * (user_cnt[0][0] - len(user_unpayed))

    cur.execute("UPDATE account SET balance = balance - '{}' WHERE balance >= '{}';".format(int(monthly_fee), int(monthly_fee)))
    cur.execute("UPDATE account SET balance = balance + '{}' WHERE id = 'admin'".format(admin_revenue))
    connect.commit()
    return render_template('admin_collect.html', unpayed_user_list = user_unpayed , user_cnt = user_cnt , revenue = admin_revenue )

@app.route('/item_add', methods=['post'])
def item_add():
    user_id = request.form["id"]
    cur.execute("SELECT * FROM category;")
    category = cur.fetchall() 
    return render_template('item_add.html', category_list = category, id = user_id)

@app.route('/item_adding', methods=['post'])
def item_adding():
    code = request.form["code"]
    name = request.form["name"]
    price = request.form["price"] 
    stock = request.form["stock"]
    seller = request.form["seller"]    
    send = request.form["send"]
    
    cur.execute("SELECT code FROM category WHERE code ='{}';".format(code))
    code_exist = cur.fetchall()
    cur.execute("SELECT id FROM users WHERE id ='{}';".format(seller))
    id_exist = cur.fetchall()
    if send == "add":
        add_success = False
        #check constraints
        if code_exist and id_exist and int(price)>=0 and int(stock)>0:
            cur.execute("SELECT * FROM items WHERE code='{}' AND name='{}' AND price='{}' AND seller = '{}';".format(code, name, price, seller))
            item_exist = cur.fetchall()
            if item_exist:
                cur.execute("UPDATE items SET stock = stock + '{}' WHERE code='{}' AND name='{}' AND price='{}' AND seller = '{}';".format(stock, code, name, price, seller))
            else:
                cur.execute("INSERT INTO items VALUES('{}', '{}', '{}', '{}', '{}');".format(code, name, price, stock, seller))
            connect.commit()            
            add_success = True
        return render_template('item_add_action.html', success = add_success, id = seller)
    return redirect(url_for('login_action', user_id = seller))

@app.route('/item_buy', methods=['post'])
def item_buy():
    cur_code = request.form["code"]
    cur_name = request.form["name"]
    cur_price = request.form["price"]
    cur_stock = request.form["stock"]
    cur_seller = request.form["seller"]
    user_id = request.form["id"]
    cur.execute("SELECT balance, rating FROM account WHERE id = '{}';".format(user_id))
    user_info = cur.fetchall()
    return render_template('item_buy.html', id = user_id, u_info = user_info, code = cur_code, name = cur_name, price = cur_price, stock = cur_stock, seller=cur_seller)

@app.route('/item_buying', methods=['post'])
def item_buying():
    send = request.form["send"]
    quantity = int(request.form["how_many"])
    user_id = request.form["id"]
    user_balance = int(request.form["balance"])
    user_rating = request.form["rating"]
    item_price = int(request.form["price"])
    item_stock = int(request.form["stock"])
    item_code = request.form["code"]
    item_name = request.form["name"]
    seller = request.form["seller"]
    
    if send =="cancel":
        return redirect(url_for('login_action', user_id = user_id))
    if quantity <= 0:
        return render_template("item_buy_fail.html", id = user_id)
    if user_id == seller:
        return render_template("item_buy_fail.html", cause = "same_id", id = user_id)
    if item_stock < quantity:
        return render_template("item_buy_fail.html", cause = "insufficient_stocks", id = user_id)

    cur.execute("SELECT discount FROM rating_info WHERE rating = '{}'".format(user_rating))
    discount_percent = cur.fetchall()
    print(float(discount_percent[0][0]))

    total_price = item_price * quantity
    discount_price = total_price * (float(discount_percent[0][0]) / 100 )
    final_price = total_price - discount_price
    stock_left = item_stock - quantity

    if user_balance < final_price:
        return render_template("item_buy_fail.html", cause = "insufficient_balance", id = user_id)
    return render_template('item_trade.html', buyer = user_id, seller = seller, balance = user_balance, rating = user_rating, t_price = total_price, 
                            dc_price = discount_price, f_price = final_price, stock= item_stock, quantity = quantity, code = item_code, name = item_name)

@app.route('/item_trade', methods=['post'])
def item_trade():
    send = request.form["send"]
    buyer_id = request.form["buyer"]
    seller_id = request.form["seller"]
    buy_price = request.form["buy_price"].split('.')[0]
    sell_price = request.form["sell_price"].split('.')[0]
    item_code = request.form["item_code"]
    item_name = request.form["item_name"] 
    stock = int(request.form["stock"])
    quantity = int(request.form["quantity"])
    item_price = int(sell_price) // quantity
    stock_left = stock - quantity
    
    if send == "confirm":
        cur.execute("BEGIN;")    
        #balance
        cur.execute("UPDATE account SET balance = balance - '{}' WHERE id ='{}';".format(buy_price, buyer_id))
        cur.execute("UPDATE account SET balance = balance + '{}' WHERE id ='{}';".format(sell_price, seller_id))
        connect.commit()

        #rating
        cur.execute("SELECT balance FROM account WHERE id = '{}';".format(buyer_id))
        buyer_balance = cur.fetchall()
        cur.execute("SELECT rating FROM rating_info WHERE condition <= '{}'".format(buyer_balance[0][0]))
        buyer_rating = cur.fetchall()
        cur.execute("UPDATE account SET rating = '{}' WHERE id = '{}'".format(buyer_rating[0][0], buyer_id))
        connect.commit()

        cur.execute("SELECT balance FROM account WHERE id = '{}';".format(seller_id))
        seller_balance = cur.fetchall()
        cur.execute("SELECT rating FROM rating_info WHERE condition <= '{}'".format(seller_balance[0][0]))
        seller_rating = cur.fetchall()
        cur.execute("UPDATE account SET rating = '{}' WHERE id = '{}'".format(seller_rating[0][0], seller_id))
        connect.commit()

        #trade
        cur.execute("INSERT INTO trade VALUES('{}', '{}', '{}', '{}');".format(buyer_id, seller_id, item_code ,sell_price))
        connect.commit()
        #items(stock)
        if stock_left ==0:
            #delete from items
            cur.execute("DELETE FROM items WHERE code = '{}' AND name = '{}' AND price = '{}' AND seller = '{}';".format(item_code, item_name, item_price ,seller_id))
        else:
            #update stock number
            cur.execute("UPDATE items SET stock = '{}' \ WHERE code ='{}' AND name = '{}' AND price = '{}' AND seller = '{}';"
                        .format(stock_left,item_code, item_name, item_price ,seller_id))
        connect.commit()

    return redirect(url_for('login_action', user_id = buyer_id))   

@app.route('/item_return', methods=['post'])
def item_return():
    user_id = request.form["user"]
    cur.execute("SELECT * FROM category;")
    category = cur.fetchall() 
    return render_template('item_add.html', category_list = category, id = user_id)

if __name__ == '__main__':
    app.run()