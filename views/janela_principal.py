import sys
import os
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from config.settings import PALETTE, get_base_dir, get_assets_dir
from components.sidebar_button import SidebarButton
from views.boas_vindas_view import BoasVindasView
from views.generic_module_view import GenericModuleView
from views.pedidos_view import PedidosView
from views.clientes_view import ClientesView
from views.agenda_view import AgendaView
from views.estoque_view import EstoqueView
from views.financeiro_view import FinanceiroView
from views.orcamento_view import OrcamentoView

class JanelaFlorDeCerejeira(ctk.CTk):
    """Janela Principal da aplicação Flor de Cerejeira Creative Atelier."""
    def __init__(self):
        super().__init__()
        
        self.title("Flor de cerejeira - Creative Atelier")
        self.geometry("1120x740")
        self.minsize(980, 640)
        self.configure(fg_color=PALETTE["main_bg"])
        
        # Abrir em tela cheia (Fullscreen) por padrão e permitir alternar via F11 / ESC
        self.attributes("-fullscreen", True)
        self.bind("<F11>", self.alternar_fullscreen)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        
        # Diretório base do projeto (raiz ou diretório do .exe se congelado)
        self.base_dir = get_base_dir()
        
        # Garantir assets
        self.carregar_assets()
        
        # Layout Principal (Grid: Sidebar na col 0, Conteúdo na col 1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Dicionários de navegação
        self.nav_buttons = {}
        self.views = {}
        self.current_view_key = None
        
        # Construção da Interface
        self.criar_sidebar()
        self.criar_area_conteudo()
        
        # Selecionar a aba de boas-vindas por padrão
        self.selecionar_aba("boas_vindas")

    def carregar_assets(self):
        """Carrega e prepara todas as imagens e ícones para o CustomTkinter."""
        assets_dir = get_assets_dir(self.base_dir)
        icons_dir = os.path.join(assets_dir, "icons")
        
        # Se os assets não existirem, gerar via script
        if not os.path.exists(os.path.join(assets_dir, "hanna_mascot.png")):
            try:
                from build_assets import generate_all_assets
                generate_all_assets(self.base_dir)
            except Exception:
                pass
            
        # Carregar logo da loja
        logo_path = os.path.join(assets_dir, "logo_palette.png")
        if os.path.exists(logo_path):
            img_logo = Image.open(logo_path)
            self.img_logo = ctk.CTkImage(light_image=img_logo, dark_image=img_logo, size=(64, 64))
        else:
            self.img_logo = None
            
        # Carregar mascote Hanna
        mascot_path = os.path.join(assets_dir, "hanna_mascot.png")
        if os.path.exists(mascot_path):
            img_mascot = Image.open(mascot_path)
            self.img_mascot = ctk.CTkImage(light_image=img_mascot, dark_image=img_mascot, size=(300, 300))
        else:
            self.img_mascot = None
            
        # Carregar ícones do menu
        self.icons = {}
        items = ["boas_vindas", "orcamento", "pedidos", "clientes", "agenda", "estoque", "financeiro", "configuracoes", "suporte"]
        for item in items:
            norm_p = os.path.join(icons_dir, f"{item}_normal.png")
            act_p = os.path.join(icons_dir, f"{item}_active.png")
            
            img_norm = Image.open(norm_p) if os.path.exists(norm_p) else None
            img_act = Image.open(act_p) if os.path.exists(act_p) else None
            
            self.icons[item] = {
                "normal": ctk.CTkImage(light_image=img_norm, dark_image=img_norm, size=(22, 22)) if img_norm else None,
                "active": ctk.CTkImage(light_image=img_act, dark_image=img_act, size=(22, 22)) if img_act else None
            }

    def criar_sidebar(self):
        """Cria o menu lateral completo conforme a referência."""
        sidebar = ctk.CTkFrame(
            self,
            width=240,
            fg_color=PALETTE["sidebar_bg"],
            border_color=PALETTE["sidebar_border"],
            border_width=1,
            corner_radius=0
        )
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_columnconfigure(0, weight=1)
        sidebar.grid_rowconfigure(2, weight=1)  # Espaçador entre menus principais e inferiores
        
        # --- Topo: Logotipo e Marca ---
        brand_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=20, pady=(32, 35), sticky="ew")
        brand_frame.grid_columnconfigure(0, weight=1)
        
        if self.img_logo:
            lbl_logo = ctk.CTkLabel(brand_frame, text="", image=self.img_logo)
            lbl_logo.pack(anchor="center", pady=(0, 10))
            
        lbl_brand = ctk.CTkLabel(
            brand_frame,
            text="Flor de cerejeira",
            font=ctk.CTkFont(family="Georgia", size=20, weight="bold"),
            text_color=PALETTE["brand_title"]
        )
        lbl_brand.pack(anchor="center")
        
        lbl_sub = ctk.CTkLabel(
            brand_frame,
            text="Creative Atelier",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=PALETTE["brand_subtitle"]
        )
        lbl_sub.pack(anchor="center", pady=(2, 0))
        
        # --- Seção de Navegação Principal ---
        menu_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        menu_frame.grid(row=1, column=0, padx=16, sticky="ew")
        menu_frame.grid_columnconfigure(0, weight=1)
        
        main_menu_items = [
            ("boas_vindas", "Boas-vindas"),
            ("orcamento", "Orçamento"),
            ("pedidos", "Pedidos"),
            ("clientes", "Clientes"),
            ("agenda", "Agenda"),
            ("estoque", "Estoque"),
            ("financeiro", "Financeiro"),
        ]
        
        for idx, (key, label) in enumerate(main_menu_items):
            btn = SidebarButton(
                menu_frame,
                text=label,
                icon_normal=self.icons[key]["normal"],
                icon_active=self.icons[key]["active"],
                command=lambda k=key: self.selecionar_aba(k)
            )
            btn.pack(fill="x", pady=4)
            self.nav_buttons[key] = btn
            
        # --- Seção Inferior: Switch de Modo Escuro ---
        bottom_menu_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        bottom_menu_frame.grid(row=3, column=0, padx=16, pady=(0, 24), sticky="ew")
        bottom_menu_frame.grid_columnconfigure(0, weight=1)
        
        self.switch_theme = ctk.CTkSwitch(
            bottom_menu_frame,
            text="Modo Escuro",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["inactive_text"],
            progress_color=PALETTE["active_pill"],
            button_color=PALETTE["active_pill"],
            button_hover_color=PALETTE["active_pill_hover"],
            command=self.alternar_modo_escuro
        )
        self.switch_theme.pack(pady=(12, 6), padx=12, anchor="w")
        
        # Botão Sair do Sistema
        self.btn_sair = ctk.CTkButton(
            bottom_menu_frame,
            text="🚪 Sair",
            height=38,
            corner_radius=10,
            fg_color="transparent",
            border_color=PALETTE["sidebar_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.confirmar_saida
        )
        self.btn_sair.pack(fill="x", pady=(4, 8), padx=4)

    def alternar_fullscreen(self, event=None):
        """Alterna a aplicação entre tela cheia e modo janela."""
        is_full = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not is_full)

    def confirmar_saida(self):
        """Pede confirmação e encerra a aplicação."""
        if messagebox.askyesno("Confirmar Saída", "Deseja realmente sair do sistema Flor de Cerejeira?", parent=self):
            self.destroy()

    def alternar_modo_escuro(self):
        """Alterna dinamicamente entre Modo Claro e Modo Escuro."""
        if self.switch_theme.get() == 1:
            ctk.set_appearance_mode("Dark")
            modo = "Dark"
        else:
            ctk.set_appearance_mode("Light")
            modo = "Light"
            
        for view in self.views.values():
            if hasattr(view, "atualizar_estilo_tema"):
                view.atualizar_estilo_tema(modo)

    def criar_area_conteudo(self):
        """Cria os frames das páginas no container central."""
        self.container = ctk.CTkFrame(self, fg_color=PALETTE["main_bg"], corner_radius=0)
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        
        # Instanciar cada view
        self.views["boas_vindas"] = BoasVindasView(self.container, mascot_image=self.img_mascot)
        self.views["orcamento"] = OrcamentoView(self.container, base_dir=self.base_dir)
        self.views["pedidos"] = PedidosView(self.container, base_dir=self.base_dir)
        self.views["clientes"] = ClientesView(self.container, base_dir=self.base_dir)
        self.views["agenda"] = AgendaView(self.container, base_dir=self.base_dir)
        self.views["estoque"] = EstoqueView(self.container, base_dir=self.base_dir)
        self.views["financeiro"] = FinanceiroView(self.container, base_dir=self.base_dir)
        
        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

    def selecionar_aba(self, chave_aba):
        """Alterna a exibição da tela principal e atualiza o estado dos botões da sidebar."""
        if self.current_view_key == chave_aba:
            return
            
        # Atualizar botões
        for key, btn in self.nav_buttons.items():
            btn.set_active(key == chave_aba)
            
        # Elevar view selecionada e recarregar dados atualizados
        if chave_aba in self.views:
            view = self.views[chave_aba]
            if hasattr(view, "atualizar_tabela"):
                view.atualizar_tabela()
            if hasattr(view, "atualizar_tabela_mensal"):
                view.atualizar_tabela_mensal()
            if hasattr(view, "atualizar_calendario"):
                view.atualizar_calendario()
            view.tkraise()
            self.current_view_key = chave_aba
