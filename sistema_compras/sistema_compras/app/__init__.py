import os
from flask import Flask

def create_app():
    """
    Factory function para criar e configurar a aplicação Flask.
    """
    app = Flask(__name__)

    # 🔑 Chave secreta para sessões (usar variável de ambiente em produção)
    app.secret_key = os.environ.get("SECRET_KEY", "chave-secreta-segura-para-sessao-123")

    # 📦 Importação dos Blueprints
    from app.routes.main import main_bp
    from app.routes.fornecedor import fornecedor_bp
    from app.routes.produto import produto_bp
    from app.routes.ordemcompra import ordemcompra_bp
    from app.routes.item_ordcomp import item_ordcomp_bp
    from app.routes.cotacao import cotacao_bp
    from app.routes.pessoa import pessoa_bp
    from app.routes.unidade_medida import unidade_bp
    from app.routes.vincular_produto import vincular_bp
    from app.routes.solicitacao import solicitacao_bp
    from app.routes.itemsolic import itemsolic_bp  # ✅ novo blueprint

    # 🔗 Registro dos Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(fornecedor_bp, url_prefix='/fornecedor')
    app.register_blueprint(produto_bp, url_prefix='/produto')
    app.register_blueprint(ordemcompra_bp, url_prefix='/ordemcompra')
    app.register_blueprint(item_ordcomp_bp, url_prefix='/item_ordcomp')
    app.register_blueprint(cotacao_bp, url_prefix='/cotacao')
    app.register_blueprint(pessoa_bp, url_prefix='/pessoa')
    app.register_blueprint(unidade_bp)
    app.register_blueprint(vincular_bp)
    app.register_blueprint(solicitacao_bp, url_prefix='/solicitacao')
    app.register_blueprint(itemsolic_bp, url_prefix='/itemsolic')  # ✅ novo

    return app
