from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, BooleanField, TextAreaField, DecimalField, DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional



# Importe seu modelo de usuário para validar se o usuário já existe
# from app.models import Usuario
class LoginForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembrar-me')
    submit = SubmitField('Entrar')


class CadastrarDispositivoForm(FlaskForm):
    """Formulário para cadastrar um novo dispositivo."""
    identificador_unico = StringField('Identificador Único (ex: sensor-area-sul-01)', validators=[DataRequired(), Length(min=5, max=80)])
    nome_amigavel = StringField('Nome Amigável (ex: Sensor da Estufa 2)', validators=[DataRequired(), Length(max=100)])
    area = StringField('Área de Instalação', validators=[DataRequired(), Length(max=50)])
    id_fazenda = SelectField('Fazenda', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Cadastrar Dispositivo')

class AssociarSensorForm(FlaskForm):
    """Formulário para associar um tipo de sensor a um dispositivo."""
    # O id do dispositivo virá da URL, então não é necessário no form.
    id_tipo_sensor = SelectField('Tipo de Sensor a Adicionar', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Associar Sensor')


class BaseDynamicForm(FlaskForm):
    """Formulário base para criação dinâmica de formulários."""
    pass


def create_dynamic_form_class(model_class, headers, exclude_fields=None):
    """
    Cria uma classe de formulário dinâmica baseada no modelo SQLAlchemy.

    Args:
        model_class: Classe do modelo SQLAlchemy
        headers: Lista de nomes dos campos a incluir
        exclude_fields: Lista de campos a excluir (ex: IDs, timestamps automáticos)

    Returns:
        Classe de formulário WTForms
    """
    if exclude_fields is None:
        exclude_fields = []

    class DynamicForm(BaseDynamicForm):
        submit = SubmitField('Salvar')

    for header in headers:
        if header in exclude_fields:
            continue

        # Pular campos que terminam com _id ou são 'id'
        if header.lower().endswith('_id') or header.lower() == 'id':
            continue

        column = getattr(model_class, header, None)
        if column is None:
            continue

        field_type = str(column.type)
        field_kwargs = {
            'label': header.replace('_', ' ').title(),
            'render_kw': {'class': 'form-control-edit'}
        }

        # Definir validadores baseados nas propriedades da coluna
        validators_list = []
        if not column.nullable and not column.default:
            validators_list.append(DataRequired())
        else:
            validators_list.append(Optional())

        field_kwargs['validators'] = validators_list

        # Determinar tipo de campo baseado no tipo da coluna
        if 'VARCHAR' in field_type or 'CHAR' in field_type:
            if hasattr(column.type, 'length') and column.type.length and column.type.length > 255:
                field = TextAreaField(**field_kwargs)
            else:
                field = StringField(**field_kwargs)
        elif 'TEXT' in field_type:
            field = TextAreaField(**field_kwargs)
        elif 'INTEGER' in field_type or 'BIGINT' in field_type:
            field = IntegerField(**field_kwargs)
        elif 'DECIMAL' in field_type or 'FLOAT' in field_type or 'NUMERIC' in field_type:
            field = DecimalField(**field_kwargs)
        elif 'TIMESTAMP' in field_type or 'DATETIME' in field_type:
            field_kwargs['format'] = '%Y-%m-%d %H:%M:%S'
            field_kwargs['render_kw']['placeholder'] = 'AAAA-MM-DD HH:MM:SS'
            field = DateTimeField(**field_kwargs)
        elif 'ENUM' in field_type:
            # Para campos ENUM, criar um SelectField
            choices = [('', 'Selecione...')]
            if hasattr(column.type, 'enums'):
                choices.extend([(val, val) for val in column.type.enums])
            field_kwargs['choices'] = choices
            field_kwargs['render_kw']['class'] = 'form-select-edit'
            field = SelectField(**field_kwargs)
        elif 'BOOLEAN' in field_type:
            field_kwargs['render_kw']['class'] = 'form-check-input'
            field = BooleanField(**field_kwargs)
        else:
            # Fallback para StringField
            field = StringField(**field_kwargs)

        setattr(DynamicForm, header, field)

    return DynamicForm
