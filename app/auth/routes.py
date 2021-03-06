from app.auth import bp
from werkzeug.urls import url_parse
from flask import url_for, redirect, flash, request, render_template, session
from flask_login import current_user, login_user, logout_user
from app.auth.forms import LoginForm
from app.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user is None or not user.check_password(login_form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        session['timezone'] = login_form.timezone.data
        
        login_user(user, remember=login_form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', login_form=login_form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))