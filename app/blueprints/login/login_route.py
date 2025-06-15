from flask import Blueprint, redirect, render_template, request, url_for, flash
from flask_login import current_user, login_user, logout_user
from app.forms import LoginForm  # Importe seu formulário de login
from app.models.usuario import Usuario  # Importe o modelo de usuário

# O nome do blueprint é 'login', a variável é 'login_register'
login_register = Blueprint('login', __name__)

# Rota de Login
# A rota será /login porque o prefixo é definido no __init__.py ao registrar o blueprint
@login_register.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # Busca o usuário no banco de dados pelo nome de usuário
        user = Usuario.query.filter_by(nome_usuario=form.username.data).first()

        # Verifica se o usuário existe e se a senha está correta
        # Agora o método user.check_password() existe!
        if user is None or not user.check_password(form.password.data):
            flash('Nome de usuário ou senha inválidos', 'danger')
            # CORREÇÃO: Redireciona para a rota correta ('nome_blueprint.nome_funcao')
            return redirect(url_for('login.login'))

        # Se tudo estiver correto, faz o login do usuário
        login_user(user, remember=form.remember_me.data)
        flash('Login realizado com sucesso!', 'success')

        # Redireciona para a página que o usuário tentou acessar ou para o index
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.index'))

    return render_template('login.html', title='Login', form=form)


# Rota de Logout
@login_register.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
    