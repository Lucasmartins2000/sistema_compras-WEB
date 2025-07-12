from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.db import get_connection

itemsolic_bp = Blueprint('itemsolic', __name__, url_prefix='/itemsolic')

@itemsolic_bp.route('/novo', methods=['GET', 'POST'])
def novo_itemsolic():
    conn = get_connection()
    cursor = conn.cursor()

    # Buscar REGSOLIC e PRODUTO para preencher os selects
    cursor.execute("SELECT IDREGSOLIC FROM REGSOLIC ORDER BY IDREGSOLIC DESC")
    regsolics = cursor.fetchall()

    cursor.execute("SELECT IDPRODUTO, DESCRICAO FROM PRODUTO ORDER BY DESCRICAO")
    produtos = cursor.fetchall()

    if request.method == 'POST':
        id_regsolic = request.form.get('ID_REGSOLIC')
        id_produto = request.form.get('ID_PRODUTO')
        qntd = request.form.get('QNTD')

        if not all([id_regsolic, id_produto, qntd]):
            flash("Preencha todos os campos.")
            return render_template('itemsolic_form.html', regsolics=regsolics, produtos=produtos)

        try:
            qntd = int(qntd)
        except ValueError:
            flash("Quantidade inválida.")
            return render_template('itemsolic_form.html', regsolics=regsolics, produtos=produtos)

        try:
            cursor.execute("""
                INSERT INTO ITEMSOLIC (ID_REGSOLIC, ID_PRODUTO, QNTD)
                VALUES (%s, %s, %s)
            """, (id_regsolic, id_produto, qntd))
            conn.commit()
            flash("Item cadastrado com sucesso!")
            return redirect(url_for('itemsolic.listar_itemsolic'))
        except Exception as e:
            flash(f"Erro ao salvar: {e}")
            conn.rollback()

    cursor.close()
    conn.close()
    return render_template('itemsolic_form.html', regsolics=regsolics, produtos=produtos)

@itemsolic_bp.route('/listar')
def listar_itemsolic():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT I.IDITEMSOLIC, I.ID_REGSOLIC, I.QNTD, P.DESCRICAO
        FROM ITEMSOLIC I
        JOIN PRODUTO P ON I.ID_PRODUTO = P.IDPRODUTO
        ORDER BY I.IDITEMSOLIC DESC
    """)
    itens = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('itemsolic_list.html', itens=itens)
