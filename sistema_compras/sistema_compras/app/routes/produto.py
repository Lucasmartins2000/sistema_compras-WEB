from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.db import get_connection

produto_bp = Blueprint('produto', __name__)

# Controle de status em memória
status_memoria_produto = {}

@produto_bp.route('/')
def listar():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT IDPRODUTO, NOME, DESCRICAO, ID_UNMEDI, STQMAX, STQMIN, PNTPEDIDO
        FROM PRODUTO
    """)
    produtos = cursor.fetchall()

    for p in produtos:
        p['STATUS'] = status_memoria_produto.get(p['IDPRODUTO'], 'ATIVO')

    cursor.close()
    conn.close()
    return render_template('produto_list.html', produtos=produtos)

@produto_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT IDUNMEDI, UNIABREV, DESCRICAO FROM UNIMEDIDA")
    unidades = cursor.fetchall()
    print("DEBUG UNIDADES:", unidades)

    if request.method == 'POST':
        nome = request.form.get('NOME')
        descricao = request.form.get('DESCRICAO')
        id_unmedi = request.form.get('ID_UNMEDI')
        stqmax = request.form.get('STQMAX')
        stqmin = request.form.get('STQMIN')
        pntpedido = request.form.get('PNTPEDIDO')

        if not nome or not descricao or not id_unmedi or not stqmax or not stqmin or not pntpedido:
            flash('Por favor, preencha todos os campos obrigatórios.')
            cursor.close()
            conn.close()
            return render_template('produto_form.html', produto=None, unidades=unidades)

        cursor.execute("""
            INSERT INTO PRODUTO (NOME, DESCRICAO, ID_UNMEDI, STQMAX, STQMIN, PNTPEDIDO)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, descricao, id_unmedi, stqmax, stqmin, pntpedido))
        conn.commit()

        new_id = cursor.lastrowid
        status_memoria_produto[new_id] = 'ATIVO'

        cursor.close()
        conn.close()
        return redirect(url_for('produto.listar'))

    cursor.close()
    conn.close()
    return render_template('produto_form.html', produto=None, unidades=unidades)

@produto_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT IDUNMEDI, UNIABREV, DESCRICAO FROM UNIMEDIDA")
    unidades = cursor.fetchall()
    print("DEBUG UNIDADES:", unidades)

    if request.method == 'POST':
        nome = request.form.get('NOME')
        descricao = request.form.get('DESCRICAO')
        id_unmedi = request.form.get('ID_UNMEDI')
        stqmax = request.form.get('STQMAX')
        stqmin = request.form.get('STQMIN')
        pntpedido = request.form.get('PNTPEDIDO')

        if not nome or not descricao or not id_unmedi or not stqmax or not stqmin or not pntpedido:
            flash('Por favor, preencha todos os campos obrigatórios.')
            cursor.execute("SELECT * FROM PRODUTO WHERE IDPRODUTO = %s", (id,))
            produto = cursor.fetchone()
            cursor.close()
            conn.close()
            return render_template('produto_form.html', produto=produto, unidades=unidades)

        cursor.execute("""
            UPDATE PRODUTO
            SET NOME = %s, DESCRICAO = %s, ID_UNMEDI = %s, STQMAX = %s, STQMIN = %s, PNTPEDIDO = %s
            WHERE IDPRODUTO = %s
        """, (nome, descricao, id_unmedi, stqmax, stqmin, pntpedido, id))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for('produto.listar'))

    cursor.execute("SELECT * FROM PRODUTO WHERE IDPRODUTO = %s", (id,))
    produto = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template('produto_form.html', produto=produto, unidades=unidades)

@produto_bp.route('/inativar/<int:id>')
def inativar(id):
    status_memoria_produto[id] = 'INATIVO'
    return redirect(url_for('produto.listar'))

@produto_bp.route('/ativar/<int:id>')
def ativar(id):
    status_memoria_produto[id] = 'ATIVO'
    return redirect(url_for('produto.listar'))
