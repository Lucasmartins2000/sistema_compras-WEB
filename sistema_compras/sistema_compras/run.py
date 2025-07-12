from app import create_app
import webbrowser
import threading
import os

app = create_app()

def abrir_navegador():
    """
    Abre o navegador padrão apontando para http://127.0.0.1:5310
    Apenas usado no ambiente local.
    """
    try:
        webbrowser.open_new("http://127.0.0.1:5310/")
    except Exception as e:
        print(f"Erro ao abrir o navegador: {e}")

if __name__ == '__main__':
    # Define a porta com variável de ambiente ou usa 5310 como padrão
    porta = int(os.environ.get("PORTA_APP", 5310))

    # Se porta 5310 e processo principal (sem o recarregador do debug), abre o navegador (opcional)
    if porta == 5310 and os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Thread(target=abrir_navegador).start()

    # Define debug=True somente se você estiver local (ex: 5310 no dev)
    debug_mode = (porta == 5310)

    app.run(host="0.0.0.0", port=porta, debug=debug_mode)
