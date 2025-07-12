from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db import get_connection

unidade_bp = Blueprint('unidade_medida', __name__)

@unidade_bp.route('/unidade_medida/novo', methods=['GET', 'POST'])
def novo():
    if request.method == 'POST':
        descricao = request.form.get('DESCRICAO')
        uniabrev = request.form.get('UNIABREV')

        if not descricao or not uniabrev:
            flash('Preencha todos os campos!')
            return render_template('unidade_form.html')

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            INSERT INTO UNIMEDIDA (DESCRICAO, UNIABREV)
            VALUES (%s, %s)
        """, (descricao, uniabrev))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for('produto.novo'))

    return render_template('unidade_form.html')
