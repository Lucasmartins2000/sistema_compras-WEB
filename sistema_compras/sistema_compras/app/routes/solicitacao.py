# rotas/solicitacao.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.db import get_connection
import datetime

solicitacao_bp = Blueprint('solicitacao', __name__)

@solicitacao_bp.route('/novo', methods=['GET', 'POST'])  # ✅ corrigido
def nova_solicitacao():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Carrega os setores
        cursor.execute("SELECT IDSETOR, NOMESETOR FROM SETOR")
        setores = cursor.fetchall()

        # Carrega todos os profissionais
        cursor.execute("""
            SELECT prof.IDPROFISSIO, pf.NOMEPESSOA
            FROM PROFISSIONAL prof
            JOIN PESSOAFIS pf ON prof.ID_PESSOAFIS = pf.ID_PESSOA
        """)
        profissionais = cursor.fetchall()

        if request.method == 'POST':
            id_setor = request.form.get('ID_SETOR')
            id_profissio = request.form.get('ID_PROFISSIO')
            datasolic_str = request.form.get('DATASOLIC')

            if not id_setor or not id_profissio or not datasolic_str:
                flash("Todos os campos são obrigatórios.")
                return render_template('solicitacao_form.html', setores=setores, profissionais=profissionais)

            try:
                datasolic = datetime.datetime.strptime(datasolic_str, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                flash("Data da solicitação inválida.")
                return render_template('solicitacao_form.html', setores=setores, profissionais=profissionais)

            try:
                cursor.execute("""
                    INSERT INTO REGSOLIC (ID_PROFISSIO, DATASOLIC, ID_SETOR)
                    VALUES (%s, %s, %s)
                """, (id_profissio, datasolic, id_setor))
                conn.commit()
                flash("Solicitação registrada com sucesso.")
                return redirect(url_for('cotacao.novo'))
            except Exception as e:
                flash(f"Erro ao salvar solicitação: {e}")
                return render_template('solicitacao_form.html', setores=setores, profissionais=profissionais)

        return render_template('solicitacao_form.html', setores=setores, profissionais=profissionais)

    finally:
        cursor.close()
        conn.close()
