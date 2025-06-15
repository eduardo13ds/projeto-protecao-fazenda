from flask import Blueprint, render_template, request, redirect, url_for, flash, g, abort
from app.extensions import db
from app.models import Fazenda

fazendas_bp = Blueprint('fazendas', __name__, url_prefix='/fazendas')

# READ (Listar)
# URL final será: /fazendas/ ou /fazendas
@fazendas_bp.route('/')
def listar():
    # A lógica de segurança para pegar apenas as fazendas do usuário logado (g.user)
    # deve ser aplicada aqui, geralmente em um @before_request ou diretamente.
    # Assumindo que g.user já foi definido:
    if not hasattr(g, 'user'):
        abort(401) # Não autorizado se não houver usuário logado

    fazendas_do_usuario = g.user.fazendas
    return render_template('fazendas/fazendas_lista.html', fazendas=fazendas_do_usuario)
    

# CREATE (Formulário para Criar)
# URL final: /fazendas/nova
@fazendas_bp.route('/nova', methods=['GET', 'POST'])
def criar():
    if request.method == 'POST':
        nome = request.form.get('nome_fazenda')
        descricao = request.form.get('descricao')

        if not nome:
            flash('O nome da fazenda é obrigatório!', 'danger')
            return render_template('fazendas/fazenda_form.html')

        nova_fazenda = Fazenda(nome_fazenda=nome, descricao=descricao)

        # IMPORTANTE: Associa a nova fazenda ao usuário que a criou
        # e também a um nível de acesso padrão (ex: Gerente)
        nova_fazenda.usuarios.append(g.user)
        # Aqui você adicionaria a lógica para definir o nível de acesso na tabela de associação

        db.session.add(nova_fazenda)
        db.session.commit()

        flash('Fazenda criada com sucesso!', 'success')
        # Note o '.' no url_for: 'nome_do_blueprint.nome_da_funcao'
        return redirect(url_for('fazendas.listar'))

    return render_template('fazendas/fazenda_form.html')


