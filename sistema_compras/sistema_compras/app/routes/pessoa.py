from flask import Blueprint, render_template
from app.db import get_connection

pessoa_bp = Blueprint('pessoa', __name__)

@pessoa_bp.route('/')
def listar():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT P.IDPESSOA, P.TIPOPESSOA, PF.NOMEPESSOA, PJ.RAZSOCIAL
        FROM PESSOA P
        LEFT JOIN PESSOAFIS PF ON P.IDPESSOA = PF.ID_PESSOA
        LEFT JOIN PESSOAJUR PJ ON P.IDPESSOA = PJ.ID_PESSOA
    """)
    pessoas = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('pessoa_list.html', pessoas=pessoas)
