from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.simulador import itens_ordem, id_itemordcomp_counter

item_ordcomp_bp = Blueprint('item_ordcomp', __name__)

@item_ordcomp_bp.route('/')
def listar():
    return render_template('item_ordcomp_list.html', itens=itens_ordem)

@item_ordcomp_bp.route('/novo', methods=['GET', 'POST'])
def novo():
    global id_itemordcomp_counter

    if request.method == 'POST':
        id_ordcomp = request.form.get('ID_ORDCOMP')
        id_produto = request.form.get('ID_PRODUTO')
        qntd = request.form.get('QNTD')
        valor = request.form.get('VALOR')
        datavenc = request.form.get('DATAVENC')

        # Validação básica
        if not id_ordcomp or not id_produto or not qntd or not valor or not datavenc:
            flash('Por favor, preencha todos os campos obrigatórios.')
            return render_template('item_ordcomp_form.html')

        try:
            qntd = int(qntd)
            valor = float(valor)
        except ValueError:
            flash('Quantidade deve ser número inteiro e valor deve ser número decimal.')
            return render_template('item_ordcomp_form.html')

        novo_item = {
            'IDITEMORD': id_itemordcomp_counter,
            'ID_ORDCOMP': id_ordcomp,
            'ID_PRODUTO': id_produto,
            'QNTD': qntd,
            'VALOR': valor,
            'DATAVENC': datavenc
        }

        itens_ordem.append(novo_item)
        id_itemordcomp_counter += 1

        return redirect(url_for('item_ordcomp.listar'))

    return render_template('item_ordcomp_form.html')
