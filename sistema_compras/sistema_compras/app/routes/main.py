from flask import Blueprint, render_template

# Blueprint principal do sistema
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Rota principal (dashboard) do sistema.
    Renderiza o template index.html.
    """
    return render_template('index.html')
