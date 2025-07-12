from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from app.db import get_connection
import mysql.connector
import datetime

cotacao_bp = Blueprint('cotacao', __name__)

@cotacao_bp.route('/')
def listar():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT C.IDCOTACAO, C.ID_ITEMSOLIC, C.ID_REGSOLIC, C.ID_FORNECEDOR, C.VALORCOT,
               C.OBSERVACAO, C.STATUSCOT, C.MOTNEG,
               P.DESCRICAO AS NOME_PRODUTO,
               COALESCE(PF.NOMEPESSOA, PJ.RAZSOCIAL) AS NOME_FORNECEDOR
        FROM COTACAO C
        LEFT JOIN ITEMSOLIC I ON C.ID_ITEMSOLIC = I.IDITEMSOLIC
        LEFT JOIN PRODUTO P ON I.ID_PRODUTO = P.IDPRODUTO
        LEFT JOIN FORNECEDOR F ON C.ID_FORNECEDOR = F.IDFORNECEDOR
        LEFT JOIN PESSOAFIS PF ON F.ID_PESSOA = PF.ID_PESSOA
        LEFT JOIN PESSOAJUR PJ ON F.ID_PESSOA = PJ.ID_PESSOA
    """)
    cotacoes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('cotacao_list.html', cotacoes=cotacoes)

@cotacao_bp.route('/profissionais-por-setor/<int:id_setor>')
def profissionais_por_setor(id_setor):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT prof.IDPROFISSIO, pf.NOMEPESSOA
        FROM SETOR s
        JOIN PROFISSIONAL prof ON s.ID_PROFISSIO = prof.IDPROFISSIO
        JOIN PESSOAFIS pf ON prof.ID_PESSOAFIS = pf.ID_PESSOA
        WHERE s.IDSETOR = %s
    """, (id_setor,))
    profissionais = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(profissionais)

@cotacao_bp.route('/produto-por-itemsolic/<int:id_itemsolic>')
def produto_por_itemsolic(id_itemsolic):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ID_PRODUTO FROM ITEMSOLIC WHERE IDITEMSOLIC = %s", (id_itemsolic,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify({'id_produto': row[0] if row else None})

@cotacao_bp.route('/aprovar/<int:id>')
def aprovar(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE COTACAO SET STATUSCOT = 'APROVADO' WHERE IDCOTACAO = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Cotação aprovada com sucesso!")
    return redirect(url_for('cotacao.listar'))

@cotacao_bp.route('/negado_form/<int:id>', methods=['GET', 'POST'])
def negado_form(id):
    if request.method == 'POST':
        motivo = request.form.get('MOTNEG')
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE COTACAO SET STATUSCOT = 'NEGADO', MOTNEG = %s
            WHERE IDCOTACAO = %s
        """, (motivo, id))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Cotação negada com sucesso!")
        return redirect(url_for('cotacao.listar'))

    return render_template('cotacao_negado_form.html', id_cotacao=id)

@cotacao_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT I.IDITEMSOLIC, P.DESCRICAO, R.IDREGSOLIC
        FROM ITEMSOLIC I
        JOIN PRODUTO P ON I.ID_PRODUTO = P.IDPRODUTO
        JOIN REGSOLIC R ON I.ID_REGSOLIC = R.IDREGSOLIC
        ORDER BY I.IDITEMSOLIC DESC
    """)
    itens_solic = cursor.fetchall()

    cursor.execute("SELECT IDSETOR, NOMESETOR FROM SETOR")
    setores = cursor.fetchall()

    cursor.execute("""
        SELECT R.IDREGSOLIC, PF.NOMEPESSOA, S.NOMESETOR, R.DATASOLIC
        FROM REGSOLIC R
        JOIN PROFISSIONAL P ON R.ID_PROFISSIO = P.IDPROFISSIO
        JOIN PESSOAFIS PF ON P.ID_PESSOAFIS = PF.ID_PESSOA
        JOIN SETOR S ON R.ID_SETOR = S.IDSETOR
        ORDER BY R.IDREGSOLIC DESC
    """)
    solicitacoes = cursor.fetchall()

    if request.method == 'POST':
        id_itemsolic = request.form.get('ID_ITEMSOLIC')
        id_fornecedor = request.form.get('ID_FORNECEDOR')
        id_regsolic = request.form.get('ID_REGSOLIC')
        valorcot_input = request.form.get('VALORCOT')
        observacao = request.form.get('OBSERVACAO')

        try:
            valorcot = float(valorcot_input.replace(",", "."))
        except (ValueError, AttributeError):
            flash("Valor da cotação inválido.")
            return render_template('cotacao_form.html', cotacao=None, itens_solic=itens_solic, setores=setores, solicitacoes=solicitacoes)

        if not all([id_itemsolic, id_fornecedor, id_regsolic]):
            flash('Preencha todos os campos obrigatórios.')
            return render_template('cotacao_form.html', cotacao=None, itens_solic=itens_solic, setores=setores, solicitacoes=solicitacoes)

        cursor.execute("SELECT ID_PRODUTO FROM ITEMSOLIC WHERE IDITEMSOLIC = %s", (id_itemsolic,))
        resultado = cursor.fetchone()
        if not resultado:
            flash("Item de solicitação inválido.")
            return render_template('cotacao_form.html', cotacao=None, itens_solic=itens_solic, setores=setores, solicitacoes=solicitacoes)
        id_produto = resultado[0]

        cursor.execute("""
            SELECT 1 FROM FORNECPROD
            WHERE ID_PRODUTO = %s AND ID_FORNECEDOR = %s
        """, (id_produto, id_fornecedor))
        if not cursor.fetchone():
            flash("Fornecedor não vinculado ao produto.")
            return render_template('cotacao_form.html', cotacao=None, itens_solic=itens_solic, setores=setores, solicitacoes=solicitacoes)

        try:
            cursor.execute("""
                INSERT INTO COTACAO (ID_ITEMSOLIC, ID_REGSOLIC, ID_FORNECEDOR, VALORCOT, OBSERVACAO, STATUSCOT)
                VALUES (%s, %s, %s, %s, %s, 'PENDENTE')
            """, (id_itemsolic, id_regsolic, id_fornecedor, valorcot, observacao))
            conn.commit()
            flash("Cotação registrada com sucesso!")
        except mysql.connector.IntegrityError as err:
            flash(f"Erro ao salvar cotação: {err}")
            return render_template('cotacao_form.html', cotacao=None, itens_solic=itens_solic, setores=setores, solicitacoes=solicitacoes)

        cursor.close()
        conn.close()
        return redirect(url_for('cotacao.listar'))

    cursor.close()
    conn.close()
    return render_template('cotacao_form.html', cotacao=None, itens_solic=itens_solic, setores=setores, solicitacoes=solicitacoes)
