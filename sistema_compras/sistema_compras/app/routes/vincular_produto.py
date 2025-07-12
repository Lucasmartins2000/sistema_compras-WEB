from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.db import get_connection

vincular_bp = Blueprint('vincular_produto', __name__)

@vincular_bp.route('/vincular-produto-fornecedor', methods=['GET', 'POST'])
def vincular():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Carrega produtos e fornecedores
        cursor.execute("SELECT IDPRODUTO, NOME FROM PRODUTO")
        produtos = cursor.fetchall()

        cursor.execute("SELECT IDFORNECEDOR, REPRESENT FROM FORNECEDOR")
        fornecedores = cursor.fetchall()

        if request.method == 'POST':
            if not produtos or not fornecedores:
                flash("Cadastre ao menos um produto e um fornecedor antes de vincular.")
                return redirect(url_for('vincular_produto.vincular'))

            id_produto = request.form.get('id_produto')
            id_fornecedor = request.form.get('id_fornecedor')

            if not id_produto or not id_fornecedor:
                flash("Selecione um produto e um fornecedor válidos.")
                return redirect(url_for('vincular_produto.vincular'))

            # Verifica se o vínculo já existe
            cursor.execute("""
                SELECT 1 FROM FORNECPROD 
                WHERE ID_PRODUTO = %s AND ID_FORNECEDOR = %s
            """, (id_produto, id_fornecedor))

            if cursor.fetchone():
                flash("Este produto já está vinculado a este fornecedor.")
            else:
                cursor.execute("""
                    INSERT INTO FORNECPROD (ID_PRODUTO, ID_FORNECEDOR)
                    VALUES (%s, %s)
                """, (id_produto, id_fornecedor))
                conn.commit()
                flash("Produto vinculado com sucesso ao fornecedor!")

            return redirect(url_for('vincular_produto.vincular'))

        # GET: Exibe o formulário
        return render_template('vincular.html', produtos=produtos, fornecedores=fornecedores)

    finally:
        cursor.close()
        conn.close()

@vincular_bp.route('/fornecedores-por-produto/<int:id_produto>')
def fornecedores_por_produto(id_produto):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT f.IDFORNECEDOR, f.REPRESENT
            FROM FORNECPROD fp
            JOIN FORNECEDOR f ON f.IDFORNECEDOR = fp.ID_FORNECEDOR
            WHERE fp.ID_PRODUTO = %s
        """, (id_produto,))
        fornecedores = cursor.fetchall()
        return jsonify(fornecedores)
    finally:
        cursor.close()
        conn.close()

@vincular_bp.route('/vinculos')
def listar_vinculos():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT 
                p.IDPRODUTO, p.NOME AS NOME_PRODUTO,
                f.IDFORNECEDOR, f.REPRESENT AS NOME_FORNECEDOR
            FROM FORNECPROD fp
            JOIN PRODUTO p ON p.IDPRODUTO = fp.ID_PRODUTO
            JOIN FORNECEDOR f ON f.IDFORNECEDOR = fp.ID_FORNECEDOR
            ORDER BY p.NOME, f.REPRESENT
        """)
        vinculos = cursor.fetchall()
        return render_template('vinculos.html', vinculos=vinculos)
    finally:
        cursor.close()
        conn.close()
