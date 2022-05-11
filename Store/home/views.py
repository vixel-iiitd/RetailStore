from turtle import home
from urllib import request
from django.shortcuts import render, HttpResponse


from dataclasses import dataclass
from django.http import HttpResponse
from django.shortcuts import render

import pymysql.cursors
import pymysql
import json
import io
from django.http import JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib import messages
from PIL import Image

import random

# Create your views here.

# def connection():
#     dataBase = pymysql.connect(
#         host='bcgy7zqwn3xsrqrlzlqc-mysql.services.clever-cloud.com',
#         user='uglv1cpvawucauko',
#         password='Sa1Hnp8Wibs4usc0e4CD',
#         db='bcgy7zqwn3xsrqrlzlqc',
#         autocommit=True
#     )
#     return dataBase
def connection():
    dataBase = pymysql.connect(
        host='localhost',
        user='root',
        password='Abhish@3556',
        db='retail_bazar',
        autocommit=True
    )
    return dataBase



db = connection()


def index(request): 

    if 'type' not in request.session:
        return redirect('login2')

    if request.session['type'] == 'Customer':
        return redirect('customer')

    if request.session['type'] == 'Delivery':
        return redirect('delivery')

    if request.session['type'] == 'Seller':
        return redirect('seller')

    return redirect('handleLogin')






def handleLogout(request):
    try:
        del request.session['email']
        del request.session['type']
    except:
        return redirect('login2')

    return redirect('login2')


def login2(request):

    if request.method=='POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        logCust = request.POST.get('logCust')
        logSell = request.POST.get('logSell')
        logDell = request.POST.get('logDell')

        loginAs = ''

        if(logCust=='on'):
            loginAs='Customer'
        elif(logDell=='on'):
            loginAs='Delivery'
        else:
            loginAs='Seller'

        user = authenticate(username=(
            email+loginAs), password=password, first_name=email, last_name=loginAs)

        if user is not None:
            login(request, user)
            if(logSell == 'on'):
                request.session['email'] = email
                request.session['type'] = loginAs
                return redirect('seller')

            if(logCust == 'on'):
                request.session['email'] = email
                request.session['type'] = loginAs
                return redirect('customer')

            if(logDell== 'on'):
                request.session['email'] = email
                request.session['type'] = loginAs
                return redirect('delivery')
        else:
            messages.error(request, 'Please check Login details')
            return redirect('login2')


    return render(request, "login2.html")


def signup2(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('firstName')
        phone = request.POST.get('phoneNumber')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        logCust = request.POST.get('logCust')
        logSell = request.POST.get('logSell')
        logDell = request.POST.get('logDell')

        signAs=''

        if(logCust=='on'):
            signAs='Customer'
        elif(logDell=='on'):
            signAs='Delivery'
        else:
            signAs='Seller'

        if(len(email) < 4):
            messages.error(request, 'Email length must be 4')
            return redirect('signup2')
        elif(len(name) < 2):

            messages.error(
                request, 'firstName must be greater than 2 characters')

            return redirect('signup2')
        elif (password1 != password2):

            messages.error(request, 'Password dont match')

            return redirect('signup2')
        elif(len(password1) < 5):
            messages.error(request, 'Password must be 5 characters')

            return redirect('signup2')

        db.ping()
        cur = db.cursor()

        if(signAs == "Customer"):
            cur.execute(
                "INSERT INTO customer(customerName,customerNumber,customerEmail) VALUES(%s,%s,%s)", (name, phone, email))

            val = cur.execute("SELECT * FROM customer")
            print(cur.fetchall())
        elif(signAs == "Seller"):
            print("+++++++++++++++++++++++++++++++++++++++++++")
            cur.execute(
                "INSERT INTO seller(sellerEmail,sellerName,sellerNumber,sellerWarehouse) VALUES(%s,%s,%s,%s)", (email, name, phone, 1))
            print("--------------------------------------------")
            val = cur.execute("SELECT * FROM seller")
            print(cur.fetchall())
        elif(signAs == "Delivery"):
            cur.execute(
                "INSERT INTO deliveryPerson(deliveryPersonEmail,deliveryPersonName,phoneNumber,ordersTaken) VALUES(%s,%s,%s,%s)", (email,name, phone, 0))
        else:
            return HttpResponse("<h1>Invalid</h1>")

        usname = email+signAs

        myuser = User.objects.create_user(usname, email, password1)
        myuser.save()
        return redirect('login2')

    return render(request, "signup2.html")


def add_product(request):
    if request.method == 'POST':
        productID = request.POST.get('productID')
        ProductName = request.POST.get('ProductName')
        category = request.POST.get('category')
        Price = request.POST.get('Price')
        Brand = request.POST.get('Brand')
        sellerEmail = request.session['email']
        img = request.FILES.get('filename')
        print(img, type(img))
        bin_img = img.read()
        print(type(img.file), type(bin_img))

        db.ping()
        cur = db.cursor()
        cur.execute("INSERT INTO Product(ProductID,ProductName,Price,Brand,CategoryID,sellerEmail,image) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                    (productID, ProductName, Price, Brand, category, sellerEmail, bin_img))

        return redirect('seller')

    return render(request, 'add_Product.html')


def seller(request):

    sellerEmail = request.session['email']
    if request.method == 'POST' and 'add_product' in request.POST:
        return redirect('add_product')
    if request.method == 'POST' and 'drop_product' in request.POST:
        productID = request.POST['productID1']
        db.ping()
        cur = db.cursor()

        print(productID, "-----------")
        cur.execute("DELETE FROM Product WHERE sellerEmail= %(seller_id)s AND ProductID=%(proId)s", {
                    'seller_id': sellerEmail, 'proId': productID})
        db.commit()
        cur.close()
        return redirect('seller')

    if request.method == 'POST' and 'update_price' in request.POST:
        db.ping()
        cur = db.cursor()
        productID = request.POST.get('productID')
        update_Price = request.POST.get('Update Price')
       #print(productID,"+**************")
        #query=f"UPDATE Product SET Price = {update_Price} WHERE  ProductID = {productID} AND sellerEmail={sellerEmail};"
        cur.execute("UPDATE Product SET Price = %(newprice)s WHERE  ProductID = %(proId)s AND SellerEmail=%(seller_id)s", {
                    'newprice': update_Price, 'seller_id': sellerEmail, 'proId': productID})
        #cur.execute("SELECT Price FROM Product WHERE ProductID = %(proId)s AND SellerEmail=%(seller_id)s", {'seller_id': sellerEmail, 'proId': productID})
        #print(cur.fetchall(),"+++++++++++++++")
        db.commit()
        cur.close()
        
        return redirect('seller')

    db.ping()
    cur = db.cursor()
    # cur.execute("Select * from Customer")
    cur.execute("Select ProductID,ProductName,Price,Brand,CategoryID from Product where sellerEmail=%(seller_id)s", {
                'seller_id': sellerEmail})
    table = cur.fetchall()

    cur = db.cursor()
    # cur.execute("Select * from Customer")
    cur.execute("Select ProductID,OrderID, Quantity from Inventory where sellerEmail=%(seller_id)s", {
                'seller_id': sellerEmail})
    table1 = cur.fetchall()
    return render(request, 'Seller.html', {'table': table, 'table1': table1})


def delivery(request):
    db.ping()
    cur = db.cursor()
    Demail = request.session['email']
    cur.execute("Select P.orderID,P.customerEmail, P.price,P.address,P.zip from orders P,deliveryPerson D where D.deliveryPersonEmail = P.deliveryPersonEmail and P.deliveryPersonEmail = %(Demail)s" , {'Demail' : Demail})
    table1=cur.fetchall()
    db.commit()
    cur.close()
    
    return render(request,'delivery.html',{'table1':table1})


# newly added

def customer(request):
    return render(request, 'customer.html')


def electronics(request):

    db.ping()
    cur = db.cursor()
    cur.execute("select * from Product where categoryID=1")
    output = cur.fetchall()
    print(request.session['email'])


    for i in range(len(output)):
        # binary_data = base64.b64decode(output[0][6])

        if(output[i][6] == None ):
            continue


        image = Image.open(io.BytesIO(output[i][6]))


        image = image.convert('RGB')
        image.save('static/' + str(i) + '_electronics' + '.jpeg')

    output = [output[i] + tuple(['static/logo.png'] if (output[i][6] == None) else ['static/' + str(i) + '_electronics' + '.jpeg' ]) for i in range(len(output))]

    return render(request, 'electronics.html', {'products': output})


def clothing(request):
    db.ping()
    cur = db.cursor()
    cur.execute("select * from Product where categoryID=2")
    output = cur.fetchall()
    for i in range(len(output)):
        # binary_data = base64.b64decode(output[0][6])

        if(output[i][6] == None ):
            continue

        image = Image.open(io.BytesIO(output[i][6]))

        image = image.convert('RGB')
        image.save('static/' + str(i) + '_clothing' + '.jpeg')

    
    output = [output[i] + tuple(['static/logo.png'] if (output[i][6] == None) else ['static/' + str(i) + '_clothing' + '.jpeg' ] ) for i in range(len(output))]


    return render(request, 'clothing.html', {'products': output})


def groceries(request):
    db.ping()
    cur = db.cursor()
    cur.execute("select * from Product where categoryID=3")
    output = cur.fetchall()
    for i in range(len(output)):
        # binary_data = base64.b64decode(output[0][6])

        if(output[i][6] == None ):
            continue


        image = Image.open(io.BytesIO(output[i][6]))


        image = image.convert('RGB')
        image.save('static/' + str(i) + '_grocery' + '.jpeg')

   
    output = [output[i] + tuple(['static/logo.png'] if (output[i][6] == None) else ['static/' + str(i) + '_grocery' + '.jpeg' ]) for i in range(len(output))]


    return render(request, 'groceries.html', {'products': output})


def checkout(request):
    db.ping()
    my_cursor2 = db.cursor()
    Cid = request.session['email']
    my_cursor2.execute(
        "select ProductID,sellerEmail,price,quantity from cart where customerEmail= %(Cid)s", {'Cid': Cid})
    output = my_cursor2.fetchall()

    ProductID = [O[0] for O in output]
    sellerEmail = [O[1] for O in output]
    price = [O[2] for O in output]
    quantity = [O[3] for O in output]

    output = []
    amt = 0
    for i in range(len(ProductID)):
        my_cursor2.execute("Select * from Product Where ProductID =  %(Pro_id)s and sellerEmail = %(Sell_id)s",
                           {'Pro_id': ProductID[i], 'Sell_id': sellerEmail[i]})
        a = my_cursor2.fetchone()
        output.append(a)
        amt = amt+price[i]
    output = [output[i] + tuple([quantity[i]]) for i in range(len(output))]

    return render(request, 'checkout.html', {'products': output, 'amt': amt, 'quantity': quantity, 'len': len(ProductID)})


def update_item(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        Pid, Sid, action = int(body['Pid']), body['Sid'], body['action']
        Cid = request.session['email']

        my_connection = connection()
        my_connection.ping()
        my_cursor = my_connection.cursor()

        quantity = 1

        # Select query
        my_cursor.execute("SELECT Price FROM Product WHERE ProductID = %(Pro_id)s AND sellerEmail = %(Sell_id)s ", {
                          'Pro_id': Pid, 'Sell_id': Sid})
        price = my_cursor.fetchone()[0]

        # Finding Quantity
        query = f'SELECT quantity FROM cart WHERE customerEmail = \'{Cid}\' AND sellerEmail = \'{Sid}\' AND ProductID = {Pid}'
        my_cursor.execute(query)
        output = my_cursor.fetchall()

        if len(output) != 0:
            quantity = output[0][0] + 1
            query = f'UPDATE cart SET quantity = {quantity}, price = {price*quantity} WHERE customerEmail = \'{Cid}\' AND sellerEmail = \'{Sid}\' AND ProductID = {Pid}'
        else:
            query = f'INSERT INTO cart(customerEmail,sellerEmail,ProductID,quantity,price) VALUES(\'{Cid}\',\'{Sid}\',{Pid},{quantity},{price*quantity})'

        my_cursor.execute(query)
        my_connection.commit()

        messages.success(request, "Your item has been added to cart.")

    return JsonResponse('Cart was updated', safe=False)

def create_order(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        email = request.POST.get('email')
        address = request.POST.get('address')
        zip_code = request.POST.get('zip')

        Cid = request.session['email']
        my_connection = connection()
        my_connection.ping()
        my_cursor = my_connection.cursor()

        my_cursor.execute(f'SELECT deliveryPersonEmail FROM deliveryPerson WHERE ordersTaken = (SELECT MIN(ordersTaken) FROM deliveryPerson)')
        deliveryPerson = my_cursor.fetchone()[0]

        my_cursor.execute(f'SELECT MIN(ordersTaken) FROM deliveryPerson')
        orderTaken = my_cursor.fetchone()[0]
        my_cursor.execute(f'SELECT deliveryPersonEmail FROM deliveryPerson where ordersTaken = \'{orderTaken}\'')
        dPerson = my_cursor.fetchone()[0]

        print(orderTaken)
        print(dPerson)
        my_cursor.execute(f'UPDATE deliveryPerson SET ordersTaken = {orderTaken+1} WHERE deliveryPersonEmail=\'{dPerson}\'')

        my_cursor.execute(f'INSERT INTO orders(customerEmail, deliveryPersonEmail, price, address, zip) VALUES (\'{Cid}\', \'{deliveryPerson}\', \
            (SELECT SUM(price) FROM cart WHERE customerEmail = \'{Cid}\'), \'{address}\', {zip_code})')
        my_connection.commit()
        
        my_cursor.execute(f'SELECT MAX(orderID) FROM orders')
        orderID = my_cursor.fetchone()[0]

        my_cursor.execute(f'INSERT INTO Inventory(OrderID, ProductID, sellerEmail, Quantity) \
            SELECT orders.OrderID, cart.ProductID, cart.sellerEmail, cart.quantity FROM \
            orders INNER JOIN cart ON orders.customerEmail = cart.customerEmail WHERE OrderID = {orderID}')
        my_connection.commit() 

        my_cursor.execute(f'DELETE FROM cart WHERE customerEmail = \'{Cid}\'')
        my_connection.commit()
        

        return redirect(customer)

    return redirect(checkout)

def your_orders(request):
    Cid = request.session['email']

    my_connection = connection()
    my_connection.ping()
    my_cursor = my_connection.cursor()

    my_cursor.execute(f'SELECT orderID, price, address, deliveryPersonEmail, zip FROM orders WHERE customerEmail = \'{Cid}\'')
    orders = my_cursor.fetchall()

    return render(request, 'your_orders.html', {'table' : orders})

def order(request, *args, **kwargs):
    my_connection = connection()
    my_connection.ping()
    my_cursor = my_connection.cursor()

    orderID = kwargs['orderID']
    my_cursor.execute(f'SELECT Product.ProductName, Product.sellerEmail, Inventory.Quantity, Inventory.Quantity * Product.Price\
        FROM Product INNER JOIN Inventory ON Product.ProductID = Inventory.ProductID AND Product.sellerEmail = Inventory.sellerEmail\
        WHERE Inventory.OrderID = {orderID}')
    inventory = my_cursor.fetchall()
    print(inventory)

    return render(request, 'order.html', {'table' : inventory, 'orderID' : orderID})
