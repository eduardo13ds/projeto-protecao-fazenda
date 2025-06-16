from flask import Blueprint, render_template, abort, make_response, current_app, url_for, request
from flask_login import login_required, current_user
from app.models import Usuario, Fazenda, Sensor, Atuador, NivelAcesso, TipoSensor, TipoAtuador, Alerta, RegistroLeitura, RegistroComandoAtuador, DocumentoVerificacao
from app.extensions import db
import hashlib
import uuid
import qrcode
from io import BytesIO
from datetime import datetime
import os
import pandas as pd
from sqlalchemy import or_

# Dependências para PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Mapa que conecta a string da URL ao nosso modelo SQLAlchemy.
MODEL_MAP = {
    'usuarios': Usuario,
    'fazendas': Fazenda,
    'sensores': Sensor,
    'atuadores': Atuador,
    'niveis_acesso': NivelAcesso,
    'tipos_sensor': TipoSensor,
    'tipos_atuador': TipoAtuador,
    'alertas': Alerta,
    'registro_leituras': RegistroLeitura,
    'registro_comandos': RegistroComandoAtuador
}

# Mapa para nomes de exibição amigáveis e ícones.
DISPLAY_CONFIG = {
    'usuarios': {'display': 'Usuários', 'icon': 'fas fa-users'},
    'fazendas': {'display': 'Fazendas', 'icon': 'fas fa-tractor'},
    'sensores': {'display': 'Sensores', 'icon': 'fas fa-microchip'},
    'atuadores': {'display': 'Atuadores', 'icon': 'fas fa-robot'},
    'niveis_acesso': {'display': 'Níveis de Acesso', 'icon': 'fas fa-key'},
    'tipos_sensor': {'display': 'Tipos de Sensor', 'icon': 'fas fa-tags'},
    'tipos_atuador': {'display': 'Tipos de Atuador', 'icon': 'fas fa-cogs'},
    'alertas': {'display': 'Alertas', 'icon': 'fas fa-eye', 'readonly': True},
    'registro_leituras': {'display': 'Registros de Leituras', 'icon': 'fas fa-eye', 'readonly': True},
    'registro_comandos': {'display': 'Registros de Comandos', 'icon': 'fas fa-eye', 'readonly': True},
}

# Mapeamento manual de atributos Python para cada modelo
# Isso garante que usemos os nomes corretos dos atributos Python
ATTRIBUTE_MAP = {
    'usuarios': ['id_usuario', 'nome_usuario', 'senha_hash', 'nome_completo', 'email', 'status_conta', 'data_criacao', 'ultimo_login'],
    'fazendas': ['id_fazenda', 'nome_fazenda', 'localizacao_latitude', 'localizacao_longitude', 'area_total_hectares', 'descricao'],
    'sensores': ['id_sensor', 'nome_sensor', 'id_tipo_sensor', 'id_fazenda', 'status', 'ultima_leitura', 'limite_minimo_alerta', 'limite_maximo_alerta', 'endereco_logico', 'fabricante_modelo'],
    'atuadores': ['id_atuador', 'nome_atuador', 'id_tipo_atuador', 'id_fazenda', 'status_atual', 'ultimo_comando_timestamp', 'parametros_operacao', 'endereco_logico', 'fabricante_modelo'],
    'niveis_acesso': ['id_nivel_acesso', 'nome_nivel', 'descricao'],
    'tipos_sensor': ['id_tipo_sensor', 'nome_tipo', 'unidade_medida'],
    'tipos_atuador': ['id_tipo_atuador', 'nome_tipo'],
    'alertas': ['id_alerta', 'id_fazenda', 'timestamp_emissao', 'tipo_alerta', 'intensidade', 'probabilidade', 'mensagem', 'status', 'timestamp_reconhecimento', 'id_usuario_reconheceu'],
    'registro_leituras': ['id_leitura', 'id_sensor', 'valor_leitura', 'timestamp_leitura', 'qualidade'],
    'registro_comandos': ['id_registro_comando', 'id_atuador', 'id_usuario_executor', 'comando_executado', 'parametros_comando', 'timestamp_comando', 'status_execucao', 'mensagem_retorno']
}

def get_table_data(table_name):
    if table_name not in MODEL_MAP:
        return None, None, None
    Model = MODEL_MAP[table_name]
    headers = ATTRIBUTE_MAP.get(table_name, [c.key for c in Model.__table__.columns])
    query_items = Model.query.all()
    
    items_as_dicts = []
    for item in query_items:
        item_dict = {}
        for header in headers:
            value = getattr(item, header, None)
            if hasattr(value, 'strftime'):
                item_dict[header] = value.strftime('%Y-%m-%d %H:%M:%S')
            elif value is not None:
                item_dict[header] = str(value)
            else:
                item_dict[header] = ""
        items_as_dicts.append(item_dict)
        
    return headers, items_as_dicts, table_name


@admin_bp.route('/')
@admin_bp.route('/<string:table_name>')
@login_required
def manage_table(table_name='usuarios'):
    if table_name not in MODEL_MAP:
        abort(404)

    Model = MODEL_MAP[table_name]
    headers = ATTRIBUTE_MAP[table_name]

    # --- MELHORIA 1: Paginação ---
    # Pega o número da página da URL, ex: /admin/usuarios?page=2. Padrão é 1.
    page = request.args.get('page', 1, type=int)
    per_page = 25  # Quantos itens por página você quer mostrar

    # --- MELHORIA 2: Pesquisa no Servidor ---
    # Pega o termo de pesquisa da URL, ex: /admin/usuarios?q=joao
    search_term = request.args.get('q', '').strip()

    # --- MELHORIA 3: Ordenação no Servidor ---
    # Pega os parâmetros de ordenação da URL
    sort_by = request.args.get('sort_by', headers[0]) # Padrão: ordenar pela primeira coluna
    sort_order = request.args.get('sort_order', 'asc') # Padrão: ascendente

    # Constrói a query base
    query = Model.query

    # Aplica o filtro de pesquisa, se houver
    if search_term:
        search_filters = []
        for header in headers:
            column = getattr(Model, header, None)
            if column and hasattr(column, 'ilike'): # Verifica se a coluna suporta busca de texto
                search_filters.append(column.ilike(f'%{search_term}%'))
        if search_filters:
            query = query.filter(or_(*search_filters))

    # Aplica a ordenação
    if sort_by in headers:
        sort_column = getattr(Model, sort_by)
        if sort_order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

    # Executa a query com paginação
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    query_items = pagination.items

    # A conversão para dicionário continua a mesma
    items_as_dicts = []
    for item in query_items:
        item_dict = {}
        for header in headers:
            value = getattr(item, header, None)
            if value is None:
                item_dict[header] = ""
            elif hasattr(value, 'strftime'):
                item_dict[header] = value.strftime('%Y-%m-%d %H:%M:%S')
            else:
                item_dict[header] = str(value)
        items_as_dicts.append(item_dict)

    # O contexto agora inclui o objeto de paginação
    context = {
        "current_table_name": table_name,
        "display_name": DISPLAY_CONFIG[table_name]['display'],
        "sidebar_items": DISPLAY_CONFIG, # Você usou DISPLAY_CONFIG, o que é perfeito
        "headers": headers,
        "items": items_as_dicts,
        "is_readonly": DISPLAY_CONFIG.get(table_name, {}).get('readonly', False),
        "pagination": pagination, # <<< NOVO: Passando o objeto de paginação
        "search_term": search_term, # Para manter o valor no campo de busca
        "sort_by": sort_by,         # Para saber qual coluna está ordenada
        "sort_order": sort_order    # Para saber a direção da ordenação
    }

    return render_template('area_administrador.html', **context)

@admin_bp.route('/<table_name>/export/excel')
@login_required
def export_excel(table_name):
    headers, items, _ = get_table_data(table_name)
    if headers is None:
        abort(404)

    # Cria um DataFrame do Pandas com os dados
    df = pd.DataFrame(items, columns=headers)
    
    # Cria um buffer de bytes na memória para salvar o arquivo Excel
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Export_Data')
    writer.close()
    output.seek(0)

    # Prepara o nome do arquivo e a resposta para o navegador
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"export_{table_name}_{timestamp}.xlsx"
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return response

# --- ROTA PARA EXPORTAR PARA PDF (ATUALIZADA) ---
@admin_bp.route('/<table_name>/export/pdf')
@login_required
def export_pdf(table_name):
    # (A função get_table_data permanece a mesma)
    headers, items, _ = get_table_data(table_name)
    if headers is None:
        abort(404)

    # --- LÓGICA DE ASSINATURA ---
    # 1. Gera o PDF em um buffer inicial para calcular o hash
    buffer_inicial = BytesIO()
    doc_id = str(uuid.uuid4())
    
    # Geramos o PDF uma primeira vez SÓ para ter o conteúdo binário
    gerar_conteudo_pdf(buffer_inicial, headers, items, table_name, doc_id)
    pdf_content = buffer_inicial.getvalue()
    
    # 2. Calcula o hash SHA-256 do conteúdo do PDF
    content_hash = hashlib.sha256(pdf_content).hexdigest()
    
    # 3. Salva as informações de verificação no banco de dados
    novo_documento = DocumentoVerificacao(
        id=doc_id,
        tabela_origem=table_name,
        hash_conteudo=content_hash,
        id_usuario_emissor=current_user.id_usuario
    )
    db.session.add(novo_documento)
    db.session.commit()
    
    # 4. Gera o QR Code com a URL de verificação
    verification_url = url_for('admin.verificar_documento', doc_id=doc_id, _external=True)
    qr_img = qrcode.make(verification_url)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    
    # --- GERAÇÃO FINAL DO PDF COM ASSINATURA E QR CODE ---
    buffer_final = BytesIO()
    # Passamos o buffer do QR Code para a função de geração
    gerar_conteudo_pdf(buffer_final, headers, items, table_name, doc_id, content_hash, qr_buffer)

    # --- Prepara a resposta para o navegador ---
    buffer_final.seek(0)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"stormguard_relatorio_{table_name}_{timestamp}.pdf"
    
    response = make_response(buffer_final.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response


def gerar_conteudo_pdf(buffer, headers, items, table_name, doc_id, content_hash=None, qr_buffer=None):
    """Função auxiliar para construir o PDF, agora reutilizável."""
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=60,
        title=f"Relatório StormGuard - {DISPLAY_CONFIG[table_name]['display']}"
    )
    
    # Configurar estilos
    styles = getSampleStyleSheet()

    font_path = os.path.join(
    current_app.root_path,  # Pega o diretório raiz da aplicação
    'static', 
    'fonts', 
    'Syne-Regular.ttf'  # Nome do arquivo da fonte
)
    
    # Registrar fonte Syne (se disponível)
    try:
        pdfmetrics.registerFont(TTFont('Syne', font_path))
        syne_available = True
    except:
        syne_available = False
        current_app.logger.warning("Fonte Syne não encontrada, usando Helvetica como fallback")
    
    # Criar estilos personalizados
    styles.add(ParagraphStyle(
        name='StormGuardLogo',
        fontName='Syne' if syne_available else 'Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor("#043504"),
        spaceAfter=0,
        alignment=1,
        leading=24
    ))
    
    styles.add(ParagraphStyle(
        name='StormGuardTitle',
        fontName='Syne' if syne_available else 'Helvetica-Bold',
        fontSize=14,
        textColor=colors.black,
        spaceAfter=12,
        alignment=1
    ))
    
    elements = []
    
    # Adicionar logo textual
    logo = Paragraph("<b>StormGuard</b>", styles['StormGuardLogo'])
    elements.append(logo)
    
    # Adicionar título do relatório
    title = Paragraph(DISPLAY_CONFIG[table_name]['display'], styles['StormGuardTitle'])
    elements.append(title)
    
    # Linha divisória
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1e3a8a')))
    elements.append(Spacer(1, 12))
    
    # Informações de exportação
    date_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    export_info = Paragraph(
        f"<font size=9><b>Exportado em:</b> {date_str} | <b>Registros:</b> {len(items)}</font>", 
        styles['Normal']
    )
    elements.append(export_info)
    
    elements.append(Spacer(1, 16))
    
    # Preparar dados da tabela com quebra de texto
    table_data = [headers]
    for item in items:
        table_data.append([str(item.get(h, "")) for h in headers])
    
    # Calcular larguras das colunas
    col_widths = [doc.width / len(headers) * 0.95 for _ in headers]
    
    # Criar tabela com auto-ajuste de altura
    table = Table(
        table_data,
        colWidths=col_widths,
        repeatRows=1,
        style=[
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f3f4f6')])
        ],
        hAlign='CENTER'
    )
    elements.append(table)
    elements.append(Spacer(1, 24))
    
    # --- RODAPÉ COM INFORMAÇÕES DE VERIFICAÇÃO ---
    if content_hash and qr_buffer:
        elements.append(Spacer(1, 24))
        
        qr_image = Image(qr_buffer, width=60, height=60)
        qr_image.hAlign = 'LEFT'
        
        info_text = f"""
        <font size=7>
        <b>Documento ID:</b> {doc_id}<br/>
        <b>Hash de Verificação (SHA-256):</b> {content_hash[:32]}...<br/>
        <b>Data de Emissão:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br/>
        <b>Emitido por:</b> {current_user.nome_completo}<br/>
        <i>Verifique a autenticidade deste documento escaneando o QR Code.</i>
        </font>
        """
        
        info_paragraph = Paragraph(info_text, styles['Normal'])
        
        verification_table = Table([[qr_image, info_paragraph]], colWidths=[70, doc.width - 70])
        verification_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ]))
        
        elements.append(verification_table)

    doc.build(elements)

@admin_bp.route('/verificar/<string:doc_id>')  # Mudamos para string
def verificar_documento(doc_id):
    """Página pública para verificar a autenticidade de um documento."""
    try:
        # Validação manual do UUID
        uuid_obj = uuid.UUID(doc_id)
        documento = db.session.get(DocumentoVerificacao, str(uuid_obj))
        if not documento:
            return render_template('errors/404_verificacao_documento.html'), 404
        
        return render_template('verificacao_documento.html', doc=documento)
    except ValueError:  # UUID inválido
        return render_template('errors/404_verificacao_documento.html'), 404