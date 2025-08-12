from flask import Flask, render_template, jsonify, request
import requests
app = Flask(__name__)

token = "8420874385:AAG89KOYSxNNtLQCqrT3Uwtc3U6IxKhikoQ"
chatId = "1084261917"
url = f"https://api.telegram.org/bot{token}/sendMessage"


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

    name = f"{data.get("customer", {}).get("firstName", "")} {data.get("customer", {}).get("lastName", "")}"
    street = data.get("address", {}).get("street","")
    city = data.get("address", {}).get("city","")
    email = data.get("customer", {}).get("email", "")
    phone =  data.get("customer", {}).get("phone", "")
    payment =  data.get("payment", {}).get("method", "")
    items = data.get("items", [])

    message = (
        f"<b>🛒 ទទួលបានការបញ្ជាទិញថ្មី</b>\n"
        f"<b>ឈ្មោះ៖</b> {name}\n"
        f"<b>អាស័យដ្ឋាន៖</b> {street} {city}\n"
        f"<b>អ៊ីមែល៖</b> {email}\n"
        f"<b>លេខទូរស័ព្ទ៖</b> <code>{phone}</code>\n"
        f"<b>បង់តាមរយះ៖</b> {payment}\n"
        f"<b>==================================</b>\n"


    )

    if items:
        message += "<b>📦 ទំនិញ:</b>\n"
        for item in items:
            message += (
                f"<b>ឈ្មោះទំនិញ៖</b> {item.get('title', '')} x{item.get('qty', 1)}\n"
                f"<b>តម្លៃ៖</b> {item.get('price', 0)}$\n\n"
            )

            

    payload = {
        "chat_id": chatId,
        "text": message,
        "parse_mode": "HTML"
    }
    telegram_res = requests.post(url, json=payload)

    if telegram_res.status_code == 200:
        return jsonify({"status": "success", "message": "Order sent to Telegram"})
    else:
        return jsonify({"status": "error", "message": "Failed"}), 500
