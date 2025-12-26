from flask import Flask, request, redirect, url_for, flash, render_template_string
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ================= DATABASE MODEL =================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100))
    role = db.Column(db.String(50))

# ================= HTML TEMPLATE =================
base_html = """
<!DOCTYPE html>
<html lang="fa">
<head>
<meta charset="UTF-8">
<title>{{ title }}</title>
<style>
body{
    font-family:sans-serif;
    background:#f2f2f2;
    display:flex;
    justify-content:center;
    margin-top:80px;
}
.card{
    background:white;
    padding:25px;
    width:320px;
    border-radius:10px;
    box-shadow:0 0 10px #ccc;
    text-align:center;
}
input{
    width:90%;
    padding:8px;
    margin:8px 0;
}
button{
    width:100%;
    padding:8px;
    background:#007bff;
    color:white;
    border:none;
    border-radius:5px;
}
a{ text-decoration:none; color:#007bff; }
.msg{ color:red; font-size:14px; }
</style>
</head>
<body>
<div class="card">
<h2>{{ title }}</h2>
{% with messages = get_flashed_messages() %}
{% if messages %}
<div class="msg">{{ messages[0] }}</div>
{% endif %}
{% endwith %}
{{ content | safe }}
</div>
</body>
</html>
"""

# ================= ROUTES =================
@app.route('/')
def login():
    content = """
    <form method="POST" action="/login">
        <input name="username" placeholder="نام کاربری" required>
        <input type="password" name="password" placeholder="رمز عبور" required>
        <button>ورود</button>
    </form>
    <br>
    <a href="/register">ثبت نام</a> |
    <a href="/forgot">فراموشی رمز</a>
    """
    return render_template_string(base_html, title="ورود", content=content)

@app.route('/login', methods=['POST'])
def do_login():
    user = User.query.filter_by(username=request.form['username']).first()
    if user and check_password_hash(user.password, request.form['password']):
        return f"""
        <h2>خوش آمدی {user.username}</h2>
        <p>شهر: {user.city}</p>
        <p>نقش: {user.role}</p>
        """
    flash("اطلاعات ورود اشتباه است")
    return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(username=request.form['username']).first():
            flash("این نام کاربری قبلاً ثبت شده")
            return redirect(url_for('register'))

        user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password']),
            city=request.form['city'],
            role=request.form['role']
        )
        db.session.add(user)
        db.session.commit()
        flash("ثبت نام با موفقیت انجام شد")
        return redirect(url_for('login'))

    content = """
    <form method="POST">
        <input name="username" placeholder="نام کاربری" required>
        <input name="email" placeholder="ایمیل" required>
        <input type="password" name="password" placeholder="رمز عبور" required>
        <input name="city" placeholder="شهر">
        <input name="role" placeholder="نقش (user/admin)">
        <button>ثبت نام</button>
    </form>
    """
    return render_template_string(base_html, title="ثبت نام", content=content)

@app.route('/forgot', methods=['GET','POST'])
def forgot():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            flash("کاربر پیدا شد (در پروژه واقعی ایمیل ارسال می‌شود)")
        else:
            flash("کاربری با این ایمیل وجود ندارد")

    content = """
    <form method="POST">
        <input name="email" placeholder="ایمیل" required>
        <button>بررسی</button>
    </form>
    """
    return render_template_string(base_html, title="فراموشی رمز عبور", content=content)

# ================= RUN =================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
