from flask import Blueprint, request, render_template, redirect, url_for, flash
from app.db import get_connection

ordemcompra_bp = Blueprint('ordemcompra', __name__)

@ordemcompra_bp.route('/set_status/<int:id>/<status>')
def set_status(id, status):
    if status not in ['PEND', 'ANDA', 'CONC']:
        flash('Status inválido.')
        return redirect(url_for('ordemcompra.listar'))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            UPDATE ORDEMCOMPRA
            SET STATUSORD = %s
            WHERE IDORDCOMP = %s
        """, (status, id))
        conn.commit()
        flash(f'Status da ordem {id} alterado para {status}.')
    except Exception as e:
        flash(f'Erro ao atualizar status: {e}')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('ordemcompra.listar'))


@ordemcompra_bp.route('/')
def listar():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Buscar ordens de compra
        cursor.execute("""
            SELECT *
            FROM ORDEMCOMPRA
            ORDER BY IDORDCOMP DESC
        """)
        ordens = cursor.fetchall()

        ordens_itens = []
        for ordem in ordens:
            cursor.execute("""
                SELECT I.IDITEMORD, I.QNTD, I.VALOR, I.DATAVENC,
                       C.IDCOTACAO, C.VALORCOT,
                       P.NOME AS NOME_PRODUTO
                FROM ITEM_ORDCOMP I
                JOIN COTACAO C ON I.ID_PRODUTO = C.ID_ITEMSOLIC AND C.STATUSCOT = 'APROVADO'
                JOIN PRODUTO P ON I.ID_PRODUTO = P.IDPRODUTO
                WHERE I.ID_ORDCOMP = %s
            """, (ordem['IDORDCOMP'],))
            itens = cursor.fetchall()

            ordens_itens.append({
                'ordem': ordem,
                'itens': itens
            })

        return render_template('ordemcompra_list.html', ordens_itens=ordens_itens)

    except Exception as e:
        flash(f'Erro ao buscar ordens: {e}')
        return render_template('ordemcompra_list.html', ordens_itens=[])
    finally:
        cursor.close()
        conn.close()
