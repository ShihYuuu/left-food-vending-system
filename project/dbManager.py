from asyncio.windows_events import NULL
import mysql.connector
from sqlalchemy import null

class DataBase():

    def __init__(self):
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        self.role_list = self.create_role_list()
        self.buyer = self.account_name('Buyer')
        self.seller = self.account_name('Seller')
        self.manager = self.account_name('Manager')

    def connect(self):
        mydb = mysql.connector.connect(
            host = "serverIP",
            user = "username",
            password = "password",
            database = "dbname",
            port = portnumber
        )
        return mydb
   
    def create_role_list(self):

        role = {'Seller': None,
                'Buyer': None,
                'Manager': None
                }

        for i in role:
            query = 'select account from ' + i
            self.cursor.execute(query)

            account = []
            for item in self.cursor.fetchall():
                account.append(item[0])
            role[i] = account

        return role

    def account_name(self, role):
        aname = {}
        for i in self.role_list[role]:
            query = f'select name from {role} where account="{i}"'
            self.cursor.execute(query)
            name = self.cursor.fetchall()[0][0]
            aname[i] = name
        # print(aname)
        return aname

    def get_result(self):

        result = {}
        sql_result = self.cursor.fetchall()
        for i, col in enumerate(self.cursor.column_names):
            data = []
            for j in sql_result:
                data.append(j[i])

            result[col] = data

        return result

    def role_type(self, account):

        for i in self.role_list:
            if account in self.role_list[i]:
                return i
        return None

    def user_info(self, account):

        role = self.role_type(account)
        query = 'select * from ' + role + ' where Account = "' + account + '"'
        self.cursor.execute(query)
        result = self.get_result()

        return result

    def check_password(self, account, password):
        
        role = self.role_type(account)
        query = 'select Password from ' + role + ' where Account = "' + account + '"'
        self.cursor.execute(query)
        pw = self.cursor.fetchall()[0][0]

        return True if pw == password else False
    
    def create_user(self, account, password, name, phone, role):
        
        query = f'insert into {role} values ("{account}", "{name}", "{phone}", "{password}", "pending")'
        self.cursor.execute(query)
        self.conn.commit()
        
        self.role_list = self.create_role_list()
        if role == 'Buyer':
            self.buyer = self.account_name('Buyer')
        elif role == 'Seller':
            self.seller = self.account_name('Seller')

        return

    def revise_user(self, account, password, name, phone, role):
        
        query = f'update {role} set Name="{name}", Phone="{phone}", Password="{password}" where Account="{account}"'
        
        self.cursor.execute(query)
        self.conn.commit()

        if role == 'Buyer':
            self.buyer[account] = name
        elif role == 'Seller':
            self.seller[account] = name
        elif role == 'Manager':
            self.manager[account] = name

        return

    def food_today(self, seller, date):

        if seller == '*':
            query = f'select * from Food where Date = "{date}"'
        else:
            query = f'select * from Food where Seller = "{seller}" and Date = "{date}"'
        
        self.cursor.execute(query)
        result = self.get_result()

        return result
        
    def add_food(self, food, price, discount, quantity, seller, date):

        query = f'insert into Food values (null,"{food}", "{price}", "{discount}", "{quantity}", "{seller}", "{date}")'
        self.cursor.execute(query)
        self.conn.commit()

        return

    def delete_food(self, food_id):

        query = f'delete from Food where id={food_id}'
        self.cursor.execute(query)
        self.conn.commit()

        return
    
    def get_pending_list(self):

        pending = {}
        query = f'select * from Seller where Status="pending"'
        self.cursor.execute(query)
        pending['seller'] = self.get_result()

        query = f'select * from Buyer where Status="pending"'
        self.cursor.execute(query)
        pending['buyer'] = self.get_result()

        return pending
    
    def approve_account(self, manager, account):

        role = self.role_type(account)

        query = f'update {role} set Status="approve" where Account="{account}"'

        self.cursor.execute(query)
        self.conn.commit()

        query = f'insert into Approve values(null, "{manager}", "{account}", "{role}")'
        self.cursor.execute(query)
        self.conn.commit()

        return 
    
    def reject_account(self, account):

        role = self.role_type(account)
        query = f'update {role} set Status="reject" where Account="{account}"'
        self.cursor.execute(query)
        self.conn.commit()

        return

    def get_role_info(self, role):

        query = f'select * from {role}'
        self.cursor.execute(query)

        return self.get_result()

    def seller_account(self, name):
        query = f'select ACcount from Seller where Name="{name}"'
        self.cursor.execute(query)
        return self.cursor.fetchall()[0][0]

    def search(self, store, food, date):

        query = f'select * from Food where Date="{date}" '

        if store != '':

            saccount = self.seller_account(store)
            query += f'and Seller="{saccount}" '

        if food != '':
            query += f'and FoodItem="{food}"'
        print(query)
        self.cursor.execute(query)
        

        return self.get_result()
    
    def get_food_by_id(self, id):

        query = f'select * from Food where ID = "{id}"'
        self.cursor.execute(query)

        return self.cursor.fetchall()[0]

    def add_order(self, date, buyer):

        query = f'insert into `Order` values (null, "{date}", "{buyer}", null)'
        self.cursor.execute(query)
        self.conn.commit()

        query = f'select max(ID) from `Order`'
        self.cursor.execute(query)

        return self.cursor.fetchall()[0][0]
    
    def update_amount(self, id, price):

        query = f'update `Order` set Price={price} where ID={id}'
        self.cursor.execute(query)
        self.conn.commit()

        return

    def add_food_item(self, oid, food,	quantity, seller):

        query = f'insert into Include values (null, {oid}, "{food}", {quantity}, "{seller}")'
        # print(query)
        self.cursor.execute(query)
        self.conn.commit()

        return

    def update_food_quantity(self, id, quantity):

        query = f'update Food set Quantity={quantity} where ID={id}'
        self.cursor.execute(query)
        self.conn.commit()

        return
    
    def order_today(self, seller, date):

        query = f'select Buyer, FoodItem, Quantity \
            FROM Include I left join `Order` O on I.OID=O.ID \
                where  I.Seller="{seller}" and O.Date="{date}"'

        self.cursor.execute(query)

        return self.get_result()

    def order_record(self, role, name):

        if role == 'Buyer':
            query = f'select Date, Seller, FoodItem, Quantity\
                    FROM Include I left join `Order` O on I.OID=O.ID \
                    where O.Buyer="{name}"'

        elif role == 'Seller':
            query = f'select Date, Buyer, FoodItem, Quantity \
                FROM Include I left join `Order` O on I.OID=O.ID \
                    where I.Seller="{name}"'

        self.cursor.execute(query)

        return self.get_result()
# db = DataBase()
# db.check_password('account', '111')
# print(db.check_password('account', '111'))

