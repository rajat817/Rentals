from flask import Flask, render_template, url_for, request, flash, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projects.db'
db = SQLAlchemy(app)
app.secret_key = "hello"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)

    def __init__(self,username, password):
        self.username= username
        self.password = password

class tenant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_key = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String, nullable=False)
    phone_no = db.Column(db.Integer, nullable=False)
    elec_bill = db.Column(db.Integer, nullable=False)
    monthly_rental =db.Column(db.Integer, nullable=False)
    total_rent =  db.Column(db.Integer, nullable=False)

    def __init__(self,session_key, username, phone_no, elec_bill, monthly_rental, total_rent):
        self.session_key = session_key
        self.username = username
        self.phone_no = phone_no
        self.elec_bill = elec_bill
        self.monthly_rental = monthly_rental
        self.total_rent = total_rent

     

@app.route("/", methods=["POST", "GET"])
def index():
    if "user" in session:
        users = tenant.query.filter_by(session_key=session["user"]).all()
        return render_template("homepage.html", users=users)
    else:
        return render_template("login.html")

       

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        name = request.form["username"]
        passwor = request.form["password"]

        login = User.query.filter_by(username=name).first()

        if login is None:
            flash("User Not Found")
        else:
            check = str(check_password_hash(login.password , passwor))
            if check == "False":
                flash("Worng Password")
            else:
                session["user"] = login.id
                return redirect("/")

    return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form["username"]
        password = request.form["password"]
        confirm = request.form["confirm"]

        if name == "":
            flash("Field is Required", category="error")
        elif password == "":
            flash("field is required", category="error")
        elif password != confirm:
            flash("password is not same", category="error")
        else:

            hashed_pass = generate_password_hash(password)

            user_id = User.query.filter_by(username = name).first()

            if user_id is not None:
                flash("Username Already Taken")
            else:
                user = User(name, hashed_pass)
                db.session.add(user)
                db.session.commit()
                flash("YOU ARE REGISTERED")
   
    return render_template("register.html")

@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("user", None)
    return render_template("login.html")

@app.route("/new_tenant", methods=["POST", "GET"])
def new_tenant():
    if request.method == "POST":
        username = request.form["new_tenant"]
        phone_no = request.form["Phone_Number"]
        meter_reading = request.form["meter_reading"]
        per_unit = request.form["per_unit"]
        montly_rental = request.form["Monthly_Rental"]

        check = tenant.query.filter_by(session_key=session["user"], username=username, phone_no=phone_no).first()

        if check is not None:
            flash("Tenant already Exist")
        else:
            elec_bill = int(meter_reading) * int(per_unit)
          
            total_rent = int(elec_bill) + int(montly_rental)

            tenant_added = tenant(session_key=session["user"], username=username, phone_no=phone_no, elec_bill=elec_bill, monthly_rental=montly_rental, total_rent=total_rent)
            db.session.add(tenant_added)
            db.session.commit()
            return redirect("/")

    return  render_template("new_tenant.html")

@app.route("/old_tenant", methods=["POST", "GET"])
def old_tenant():
    if request.method == "POST":
        username = request.form["tenant"]
        new_reading = request.form["new_reading"]
        per_unit =  request.form["per_unit"]
        New_rent = request.form["new_Monthly_rent"]
        rent_paid =  request.form["Rent_paid"]
        elec_paid = request.form["Elec_paid"]

        if username == "":
            flash("Teanat not Selected")
        else:
            New_Elec_bill = int(new_reading) * int(per_unit)

            userss = tenant.query.filter_by(session_key=session["user"] , username=username).first()

            bill =  userss.elec_bill + int(New_Elec_bill) - int(elec_paid)
            rent =  userss.monthly_rental + int(New_rent) - int(rent_paid)

            total = userss.total_rent + int(New_Elec_bill) +int(New_rent)

            new_total = total - (int(rent_paid)+int(elec_paid))

            Update = tenant.query.filter_by(session_key=session["user"], username=username).update(dict(elec_bill=bill, monthly_rental=rent, total_rent=new_total))
            db.session.commit()

            users = tenant.query.filter_by(session_key=session["user"]).all()

            return render_template("homepage.html", users=users)
  
    users = tenant.query.filter_by(session_key=session["user"]).all()
    return  render_template("old_tenant.html", users=users)

@app.route("/remove_tenant", methods=["POST", "GET"])
def Remove_tenant():
    if request.method == "POST":
        username = request.form["remove_tenant"]

        user_del =  tenant.query.filter_by(session_key=session["user"], username=username).delete()
        db.session.commit()

        users = tenant.query.filter_by(session_key=session["user"]).all()
        return render_template("homepage.html", users=users)
        

    users = tenant.query.filter_by(session_key=session["user"]).all()
    return render_template("remove_tenant.html", users=users)


if __name__ == "__main__":
    app.app_context().push()
    db.create_all()
    app.run(debug=False,host='0.0.0.0')