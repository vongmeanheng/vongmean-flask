from flask import Flask, render_template, jsonify, request
import requests
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Telegram
token = "8428704156:AAGUxLpmmLrQnoD6GMXOwmMv3ce6cLVgTDw"
chatId = "5861393275"
url = f"https://api.telegram.org/bot{token}/sendMessage"

# email
port = 465
smtp_server = "smtp.gmail.com"
sender_email = "meanhengv@gmail.com"
password = "dgtl ycav ruby msnq"


@app.get("/")
@app.get("/home")
def home():
    product_list = []
    api_url = 'https://fakestoreapi.com/products'
    r = requests.get(api_url)
    if r.status_code == 200:
        product_list = r.json()
    return render_template('home.html', product_list=product_list)


@app.get("/product-detail/<int:pro_id>")
def product_detail(pro_id):
    product = []
    api_url = f"https://fakestoreapi.com/products/{pro_id}"
    r = requests.get(api_url)
    if r.status_code == 200:
        product = r.json()
    print(product)

    return render_template('product_detail.html', product=product)


@app.get('/cart')
def cart():
    return render_template('cart.html')


@app.get('/checkout')
def checkout():
    return render_template('checkout.html')


@app.get('/about')
def about():
    return render_template('about.html')


@app.get('/contact')
def contact():
    return render_template('contact.html')


@app.get('/api/products')
def products():
    product = [
        {
            'id': 1,
            'name': 'coca',
            'category': 'drink',
            'cost': '0.25',
            'price': '0.5',
            'image': '/static/coca.jpeg',
        }
    ]
    return jsonify(product)

@app.post("/order")
def create_order():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    name = f"{data.get('customer', {}).get('firstName', '')} {data.get('customer', {}).get('lastName', '')}"
    street = data.get("address", {}).get("street", "")
    city = data.get("address", {}).get("city", "")
    email = data.get("customer", {}).get("email", "")
    phone = data.get("customer", {}).get("phone", "")
    payment = data.get("payment", {}).get("method", "")
    items = data.get("items", [])

    # Telegram message
    message = (
        f"<b>🛒 ទទួលបានការបញ្ជាទិញថ្មី</b>\n"
        f"<b>ឈ្មោះ៖</b> {name}\n"
        f"<b>អាស័យដ្ឋាន៖</b> {street} {city}\n"
        f"<b>អ៊ីមែល៖</b> {email}\n"
        f"<b>លេខទូរស័ព្ទ៖</b> <code>{phone}</code>\n"
        f"<b>បង់តាមរយះ៖</b> {payment}\n"
        f"<b>==================================</b>\n"
    )

    total_price = 0
    if items:
        message += "<b>📦 ទំនិញ:</b>\n"
        for item in items:
            qty = item.get('qty', 1)
            price = item.get('price', 0)
            subtotal = qty * price
            total_price += subtotal
            message += (
                f"<b>ឈ្មោះទំនិញ៖</b> {item.get('title', '')} x{qty}\n"
                f"<b>តម្លៃ៖</b> {price}$\n"
                f"<b>តម្លៃសរុប៖</b> {subtotal}$\n\n"
            )
        message += f"<b>💰 តម្លៃសរុបទាំងអស់៖</b> {total_price}$\n"

    payload = {
        "chat_id": chatId,
        "text": message,
        "parse_mode": "HTML"
    }
    telegram_res = requests.post(url, json=payload)

    email_message = f"""
    <b>🛍️ វិកាយប័ត្រការបញ្ជាទិញ</b><br>
    <hr>
    <table>
    <tr><td><b>👤 ឈ្មោះ:</b></td><td>{name}</td></tr>
    <tr><td><b>🏠 អាស័យដ្ឋាន:</b></td><td>{street} {city}</td></tr>
    <tr><td><b>📧 អ៊ីមែល:</b></td><td>{email}</td></tr>
    <tr><td><b>📞 លេខទូរស័ព្ទ:</b></td><td>{phone}</td></tr>
    <tr><td><b>💳 បង់តាមរយៈ:</b></td><td>{payment}</td></tr>
    </table>
    <hr>
    <b>📦 ទំនិញដែលបានបញ្ជាទិញ:</b><br>
    <table border="1" cellpadding="5" cellspacing="0">
    <tr>
        <th>ឈ្មោះទំនិញ</th>
        <th>ចំនួន</th>
        <th>តម្លៃ</th>
        <th>តម្លៃសរុប</th>
    </tr>
    """

    for item in items:
        qty = item.get('qty', 1)
        price = item.get('price', 0)
        subtotal = qty * price
        email_message += f"<tr><td>{item.get('title', '')}</td><td>{qty}</td><td>{price}$</td><td>{subtotal}$</td></tr>"

    email_message += f"""
    <tr>
        <td colspan="3" align="right"><b>💰 តម្លៃសរុបទាំងអស់:</b></td>
        <td><b>{total_price}$</b></td>
    </tr>
    </table>
    <hr>
    <b>🙏 អរគុណសម្រាប់ការបញ្ជាទិញ!</b>
    """

   

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "វិកាយប័ត្រការបញ្ជាទិញ"
    msg["From"] = sender_email
    msg["To"] = email
    msg.attach(MIMEText(email_message, "html", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, email, msg.as_string())

    if telegram_res.status_code == 200:
        return jsonify({"status": "success", "message": "Order sent to Telegram"})
    else:
        return jsonify({"status": "error", "message": "Failed"}), 500


