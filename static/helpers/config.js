
const { createApp } = Vue
createApp({
     delimiters: ['[[', ']]'],
     mounted() {
          let cart = JSON.parse(localStorage.getItem('cart_list') ?? '[]')
          this.cart_list = cart
     },
     data() {
          return {
               message: 'Hello World!',
               counter: 0,
               cart_list: [],
               grand_total: 0,
               shipping_fee: 1.5,

               customer: {
                    firstName: '',
                    lastName: '',
                    email: '',
                    phone: ''
               },
               address: {
                    street: '',
                    apartment: '',
                    city: '',
                    state: '',

               },
               payment: {
                    method: 'Bakong',

               },
               specialInstructions: '',
               tax_rate: 0.08
          }
     },
     methods: {
          handleSetItem(value) {
               console.log(value);
               localStorage.setItem('cart_list', JSON.stringify(value))
          },
          addToCart(product) {
               const existingProduct = this.cart_list.find(item => item.id === product.id)
               if (existingProduct) {
                    existingProduct.qty += 1
               } else {
                    const newProduct = { ...product, qty: 1 }
                    this.cart_list.push(newProduct)
               }
               this.handleSetItem(this.cart_list)
          },
          calGrandTotal() {
               this.grand_total = 0
               this.cart_list.forEach(item => {
                    let total = parseFloat(item.qty) * parseFloat(item.price)
                    this.grand_total += total
               })
               return this.grand_total
          },
          removeCart(index) {
               this.cart_list.splice(index, 1);
               this.handleSetItem(this.cart_list);
          },
          handleIncreaseCart(id) {
               const updatedCart = this.cart_list.map(item => {
                    if (item.id === id) {
                         return { ...item, qty: item.qty + 1 };
                    }
                    return item;
               });

               this.cart_list = updatedCart;
               this.handleSetItem(this.cart_list)
          },

          handleDecreaseCart(id) {
               const updatedCart = this.cart_list
                    .map(item => {
                         if (item.id === id && item.qty > 1) {
                              return { ...item, qty: item.qty - 1 };
                         } else if (item.id === id && item.qty <= 1) {
                              return null;
                         }
                         return item;
                    })
                    .filter(item => item !== null);

               this.cart_list = updatedCart;
               this.handleSetItem(this.cart_list)
          },
          handleAlertSuccess({ title = "Good job!", description = "You clicked the button!" } = {}) {
              return Swal.fire({
                    title: title,
                    text: description,
                    icon: "success"
               });
          },


          // order bro
          calTax() {
               return (this.calGrandTotal() * this.tax_rate).toFixed(2);
          },
          calOrderTotal() {
               return (parseFloat(this.calGrandTotal()) + parseFloat(this.shipping_fee) + parseFloat(this.calTax())).toFixed(2);
          },
          reqPostOrder: async (payload) => {
               const orderEndpoint = "http://127.0.0.1:5000/order"
               return await axios
                    .post(orderEndpoint, payload).then((res) => {
                         return Promise.resolve(res.data);
                    }).catch((err) => {
                         return Promise.reject(err)
                    })
          },
          submitOrder() {
               if (!this.customer.firstName || !this.customer.lastName || !this.customer.email || !this.customer.phone) {
                    alert('Please fill in all required contact information.');
                    return;
               }

               // if (!this.address.street || !this.address.city || !this.address.state) {
               //      alert('Please fill in all required address information.');
               //      return;
               // }


               const orderData = {
                    customer: this.customer,
                    address: this.address,
                    payment: this.payment,
                    items: this.cart_list,
                    specialInstructions: this.specialInstructions,
                    totals: {
                         subtotal: this.calGrandTotal(),
                         shipping: this.shipping_fee,
                         tax: this.calTax(),
                         total: this.calOrderTotal()
                    }
               };
               this.reqPostOrder(orderData)
               this.handleAlertSuccess({title: "ការបញ្ជារទិញទទួលបានជោគជ័យ🙏", description:"សូមអរគុណ!!!"}).then(()=>{
                    this.handleSetItem([])
                    window.location.href = "/"
               })
               

               // console.log('sab order:', orderData);
          },
          handlePlaceOrder() {
               this.cart_list.length === 0 ? (window.location.href = "/") : this.submitOrder()
          }

     }

}).mount('#app')