from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.db import get_connection

fornecedor_bp = Blueprint('fornecedor', __name__)

# Dicionário para controle de status em memória
status_memoria = {}

@fornecedor_bp.route('/')
def listar():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT F.IDFORNECEDOR, F.ID_PESSOA, F.REPRESENT, F.CONTREPRE, F.DECRICAO,
               PF.NOMEPESSOA, PJ.RAZSOCIAL
        FROM FORNECEDOR F
        LEFT JOIN PESSOAFIS PF ON F.ID_PESSOA = PF.ID_PESSOA
        LEFT JOIN PESSOAJUR PJ ON F.ID_PESSOA = PJ.ID_PESSOA
    """)
    fornecedores = cursor.fetchall()

    for f in fornecedores:
        f['STATUS'] = status_memoria.get(f['IDFORNECEDOR'], 'ATIVO')

    cursor.close()
    conn.close()
    return render_template('fornecedor_list.html', fornecedores=fornecedores)

@fornecedor_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        tipopessoa = request.form.get('TIPOPESSOA')
        represent = request.form.get('REPRESENT')
        contrepre = request.form.get('CONTREPRE')
        decricao = request.form.get('DECRICAO')

        if not tipopessoa or not represent or not contrepre:
            flash('Por favor, preencha todos os campos obrigatórios.')
            cursor.close()
            conn.close()
            return render_template('fornecedor_form.html', fornecedor=None)

        cursor.execute("INSERT INTO PESSOA (TIPOPESSOA) VALUES (%s)", (tipopessoa,))
        id_pessoa = cursor.lastrowid

        if tipopessoa == 'F':
            cpf = request.form.get('CPFPESSOA')
            nome = request.form.get('NOMEPESSOA')
            datanas = request.form.get('DATANASCPES')
            sexo = request.form.get('SEXOPESSOA')

            cursor.execute("""
                INSERT INTO PESSOAFIS (ID_PESSOA, CPFPESSOA, NOMEPESSOA, DATANASCPES, SEXOPESSOA)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_pessoa, cpf, nome, datanas, sexo))

        elif tipopessoa == 'J':
            cnpj = request.form.get('CNPJ')
            razsocial = request.form.get('RAZSOCIAL')
            nomefan = request.form.get('NOMEFAN')
            cnae = request.form.get('CNAE')

            cursor.execute("""
                INSERT INTO PESSOAJUR (ID_PESSOA, CNPJ, RAZSOCIAL, NOMEFAN, CNAE)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_pessoa, cnpj, razsocial, nomefan, cnae))

        else:
            flash('Tipo de pessoa inválido.')
            cursor.close()
            conn.close()
            return render_template('fornecedor_form.html', fornecedor=None)

        cursor.execute("""
            INSERT INTO FORNECEDOR (ID_PESSOA, REPRESENT, CONTREPRE, DECRICAO)
            VALUES (%s, %s, %s, %s)
        """, (id_pessoa, represent, contrepre, decricao))

        conn.commit()
        new_id = cursor.lastrowid
        status_memoria[new_id] = 'ATIVO'

        cursor.close()
        conn.close()
        return redirect(url_for('fornecedor.listar'))

    cursor.close()
    conn.close()
    return render_template('fornecedor_form.html', fornecedor=None)

@fornecedor_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        represent = request.form.get('REPRESENT')
        contrepre = request.form.get('CONTREPRE')
        decricao = request.form.get('DECRICAO')

        if not represent or not contrepre:
            flash('Por favor, preencha todos os campos obrigatórios.')
            cursor.execute("SELECT * FROM FORNECEDOR WHERE IDFORNECEDOR = %s", (id,))
            fornecedor = cursor.fetchone()
            cursor.close()
            conn.close()
            return render_template('fornecedor_form.html', fornecedor=fornecedor)

        cursor.execute("""
            UPDATE FORNECEDOR
            SET REPRESENT = %s, CONTREPRE = %s, DECRICAO = %s
            WHERE IDFORNECEDOR = %s
        """, (represent, contrepre, decricao, id))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for('fornecedor.listar'))

    cursor.execute("SELECT * FROM FORNECEDOR WHERE IDFORNECEDOR = %s", (id,))
    fornecedor = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template('fornecedor_form.html', fornecedor=fornecedor)

@fornecedor_bp.route('/inativar/<int:id>')
def inativar(id):
    status_memoria[id] = 'INATIVO'
    return redirect(url_for('fornecedor.listar'))

@fornecedor_bp.route('/ativar/<int:id>')
def ativar(id):
    status_memoria[id] = 'ATIVO'
    return redirect(url_for('fornecedor.listar'))
