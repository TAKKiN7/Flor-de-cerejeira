import sys
import os

# Adicionar diretório raiz ao sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import setup_theme
from views.janela_principal import JanelaFlorDeCerejeira

def main():
    # Inicializa tema e configurações do CustomTkinter
    setup_theme()
    
    # Instancia e executa a aplicação
    app = JanelaFlorDeCerejeira()
    app.mainloop()

if __name__ == "__main__":
    main()
