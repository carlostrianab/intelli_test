from flask import Flask, render_template, jsonify, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import os

#Creates the flask application
app = Flask(__name__, template_folder='../frontend/templates')




#Connect to the MySQL database using 'pymysql' module 

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/facturas' #Connect the app with the database 
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS'] = False # Avoids alerts or warnings if the connection with the database is failing
app.config['SECRET_KEY'] = 'Carlos_123'


SECRET_KEY = os.urandom(32)
#Initializing SQLAlchemy, Marshmallow and Bycript

db = SQLAlchemy(app)
ma = Marshmallow(app)
bcrypt = Bcrypt(app)

#Initializing the login capabilities of the 'flask_login' module 

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#Login Manger initialization 

@login_manager.user_loader
def load_user(cliente_id):
    return Cliente.query.get(int(cliente_id))

#Database Model (Creates the database table)
class Cliente(db.Model, UserMixin):
    cliente_id = db.Column(db.Integer, primary_key=True, nullable=False)
    cliente_nombre = db.Column(db.String(100), nullable=False)
    cliente_identificacion = db.Column(db.Integer, nullable=False, unique=True)
    cliente_fecha_creacion = db.Column(db.DateTime, nullable=False)
    ofertas = db.relationship('Oferta', backref='cliente')

    def __init__(self, cliente_id, cliente_nombre, cliente_identificacion, cliente_fecha_creacion):
        self.cliente_id = cliente_id
        self.cliente_nombre = cliente_nombre
        self.cliente_identificacion = cliente_identificacion
        self.cliente_fecha_creacion = cliente_fecha_creacion

class Oferta(db.Model):
    oferta_id = db.Column(db.Integer, primary_key=True, nullable=False)
    oferta_cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.cliente_id'), nullable=False)
    oferta_valor = db.Column(db.Float, nullable=False)
    oferta_numero_producto = db.Column(db.Integer)
    oferta_fecha_creacion = db.Column(db.DateTime, nullable=False)
    oferta_dias_mora = db.Column(db.Integer, nullable=False)
    acuerdos = db.relationship('Acuerdo', backref='oferta')

    def __init__(self, oferta_id, oferta_cliente_id, oferta_valor, oferta_numero_producto, oferta_fecha_creacion, oferta_dias_mora):
        self.oferta_id = oferta_id
        self.oferta_cliente_id = oferta_cliente_id
        self.oferta_valor = oferta_valor
        self.oferta_numero_producto = oferta_numero_producto
        self.oferta_fecha_creacion = oferta_fecha_creacion
        self.oferta_dias_mora = oferta_dias_mora

class Acuerdo(db.Model):
    acuerdo_id = db.Column(db.Integer, primary_key=True, nullable=False)
    acuerdo_oferta_id = db.Column(db.Integer, db.ForeignKey('oferta.oferta_id'))
    acuerdo_fecha_creacion = db.Column(db.DateTime, nullable=False)
    acuerdo_valor = db.Column(db.Float)
    acuerdo_fecha_pago = db.Column(db.DateTime, nullable=False)
    acuerdo_estado = db.Column(db.Boolean)

    def __init__(self, acuerdo_id, acuerdo_oferta_id, acuerdo_fecha_creacion, acuerdo_valor, acuerdo_fecha_pago, acuerdo_estado):
        self.acuerdo_id = acuerdo_id
        self.acuerdo_oferta_id = acuerdo_oferta_id
        self.acuerdo_fecha_creacion = acuerdo_fecha_creacion
        self.acuerdo_valor = acuerdo_valor
        self.acuerdo_fecha_pago = acuerdo_fecha_pago
        self.acuerdo_estado = acuerdo_estado

app.app_context().push() 

db.create_all()


#Create the database Schemas 
class ClienteSchema(ma.Schema):
    class Meta:
        fields = ('cliente_id', 'cliente_nombre','cliente_identificacion', 'cliente_fecha_creacion')

cliente_schema = ClienteSchema()
clientes_schema = ClienteSchema(many=True)

class OfertaSchema(ma.Schema):
    class Meta:
        fields = ('oferta_id', 'oferta_cliente_id','oferta_valor', 'oferta_numero_producto', 'oferta_fecha_creacion', 'oferta_dias_mora')

oferta_schema = OfertaSchema()
ofertas_schema = OfertaSchema(many=True)

#Form class 

class LogInForm(FlaskForm):
    identificacion = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder":"Identificacion"})
    submit = SubmitField("Signup")

#Login route

@app.route('/', methods=['GET', 'POST'])
def login_page():
    form = LogInForm()
    if form.validate_on_submit():

        cliente_logged = Cliente.query.filter_by(cliente_identificacion = form.identificacion.data).first()
        cliente_info = cliente_schema.dump(cliente_logged)
        
        return redirect(url_for('factura_page', id = cliente_info["cliente_id"]))
    
    return render_template('login.html', form = form )

#User route

@app.route('/factura/<id>', methods=['GET', 'POST'])
def factura_page(id):
    #Getting user information 
    print(id)
    get_cliente = Cliente.query.get(id)
    cliente_info = cliente_schema.dump(get_cliente)

    #Getting individual user invoices 
    get_facturas = Oferta.query.all()
    facturas_all_clientes = ofertas_schema.dump(get_facturas)

    facturas_cliente = []

    for factura in facturas_all_clientes:
        if(factura['oferta_cliente_id'] == int(id)):
            facturas_cliente.append(factura)

    valor_total = 0

    for factura in facturas_cliente:
        valor_total += factura['oferta_valor']

   
    return render_template('index.html', facturas_cliente = facturas_cliente, cliente = cliente_info, total = valor_total)


#Initiates the app 
if __name__ == "__main__":
    app.run(debug=True)