import calendar
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox
from config.settings import PALETTE
from services.agenda_service import AgendaService
from components.nota_form_modal import NotaFormModal

class AgendaView(ctk.CTkFrame):
    """Módulo de Agenda e Calendário interativo com notas e entregas automáticas de pedidos."""
    
    def __init__(self, master, base_dir=None, **kwargs):
        super().__init__(master, fg_color=PALETTE["main_bg"], corner_radius=0, **kwargs)
        
        self.service = AgendaService(base_dir=base_dir)
        
        # Data atualmente visualizada
        hoje = datetime.now()
        self.ano_atual = hoje.year
        self.mes_atual = hoje.month
        self.data_selecionada_str = hoje.strftime("%d/%m/%Y")
        
        # Mapeamento de meses em português
        self.nome_meses = [
            "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        
        self.grid_columnconfigure(0, weight=3) # Calendário
        self.grid_columnconfigure(1, weight=2) # Painel de Eventos do Dia
        self.grid_rowconfigure(1, weight=1)
        
        # 1. Cabeçalho e Controles de Navegação
        self.criar_cabecalho_controles()
        
        # 2. Container Principal (Grade do Mês na esquerda, Painel de Detalhes na direita)
        self.criar_grade_calendario()
        self.criar_painel_detalhes_dia()
        
        # Carregar calendário e eventos iniciais
        self.atualizar_calendario()

    def criar_cabecalho_controles(self):
        """Cria o cabeçalho superior com título e botões de navegação de mês."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=36, pady=(24, 12))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Título e Subtítulo
        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")
        
        lbl_title = ctk.CTkLabel(
            title_box,
            text="Agenda & Calendário",
            font=ctk.CTkFont(family="Georgia", size=28, weight="bold"),
            text_color=PALETTE["title_text"],
            anchor="w"
        )
        lbl_title.pack(anchor="w")
        
        lbl_sub = ctk.CTkLabel(
            title_box,
            text="Acompanhe compromissos e entregas automáticas de pedidos do atelier.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=PALETTE["subtitle_text"],
            anchor="w"
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))
        
        # Controls de Navegação (Mês Anterior / Mês / Próximo Mês / Botão Nova Nota)
        nav_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        nav_box.grid(row=0, column=1, sticky="e")
        
        btn_prev = ctk.CTkButton(
            nav_box,
            text="◀",
            width=38,
            height=38,
            corner_radius=10,
            fg_color="transparent",
            border_color=PALETTE["card_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.mes_anterior
        )
        btn_prev.pack(side="left", padx=3)
        
        self.lbl_mes_ano = ctk.CTkLabel(
            nav_box,
            text="",
            width=180,
            font=ctk.CTkFont(family="Georgia", size=20, weight="bold"),
            text_color=PALETTE["brand_title"]
        )
        self.lbl_mes_ano.pack(side="left", padx=6)
        
        btn_next = ctk.CTkButton(
            nav_box,
            text="▶",
            width=38,
            height=38,
            corner_radius=10,
            fg_color="transparent",
            border_color=PALETTE["card_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.proximo_mes
        )
        btn_next.pack(side="left", padx=3)
        
        btn_hoje = ctk.CTkButton(
            nav_box,
            text="Hoje",
            height=38,
            corner_radius=10,
            fg_color="transparent",
            border_color=PALETTE["card_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.ir_para_hoje
        )
        btn_hoje.pack(side="left", padx=(10, 6))
        
        btn_nova_nota = ctk.CTkButton(
            nav_box,
            text="+ Nova Nota",
            height=38,
            corner_radius=10,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self.acao_adicionar_nota
        )
        btn_nova_nota.pack(side="left", padx=(4, 0))

    def criar_grade_calendario(self):
        """Cria o container para a grade de dias do mês."""
        self.cal_container = ctk.CTkFrame(
            self,
            fg_color=PALETTE["card_bg"],
            border_color=PALETTE["card_border"],
            border_width=1,
            corner_radius=16
        )
        self.cal_container.grid(row=1, column=0, sticky="nsew", padx=(36, 12), pady=(0, 24))
        self.cal_container.grid_columnconfigure(list(range(7)), weight=1)
        self.cal_container.grid_rowconfigure(list(range(7)), weight=1)
        
        # Cabeçalho dos Dias da Semana (Dom, Seg, Ter, Qua, Qui, Sex, Sáb)
        dias_semana = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for col, dia_nome in enumerate(dias_semana):
            lbl_d = ctk.CTkLabel(
                self.cal_container,
                text=dia_nome,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=PALETTE["brand_subtitle"]
            )
            lbl_d.grid(row=0, column=col, pady=(12, 6))

    def criar_painel_detalhes_dia(self):
        """Cria o painel lateral direito para exibir todos os eventos da data selecionada."""
        self.panel_container = ctk.CTkFrame(
            self,
            fg_color=PALETTE["card_bg"],
            border_color=PALETTE["card_border"],
            border_width=1,
            corner_radius=16
        )
        self.panel_container.grid(row=1, column=1, sticky="nsew", padx=(12, 36), pady=(0, 24))
        self.panel_container.grid_columnconfigure(0, weight=1)
        self.panel_container.grid_rowconfigure(1, weight=1)
        
        # Título do Painel
        self.lbl_data_painel = ctk.CTkLabel(
            self.panel_container,
            text="",
            font=ctk.CTkFont(family="Georgia", size=18, weight="bold"),
            text_color=PALETTE["brand_title"]
        )
        self.lbl_data_painel.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))
        
        # Container com rolagem para as notas e entregas (Barra de rolagem rosa)
        self.events_scroll = ctk.CTkScrollableFrame(
            self.panel_container,
            fg_color="transparent",
            scrollbar_button_color=PALETTE["active_pill"],
            scrollbar_button_hover_color=PALETTE["active_pill_hover"]
        )
        self.events_scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.events_scroll.grid_columnconfigure(0, weight=1)

    def atualizar_calendario(self):
        """Redesenha os dias do mês na grade e atualiza o painel de detalhes."""
        # Atualizar título do mês e ano
        self.lbl_mes_ano.configure(text=f"{self.nome_meses[self.mes_atual]} {self.ano_atual}")
        
        # Limpar botões antigos da grade (rows 1 a 6)
        for widget in self.cal_container.winfo_children():
            info = widget.grid_info()
            if int(info.get("row", 0)) > 0:
                widget.destroy()

        # Obter dados de eventos do mês
        resumo_mes = self.service.obter_resumo_mes(self.ano_atual, self.mes_atual)
        
        # Calcular dias do mês
        cal = calendar.Calendar(firstweekday=6) # 0 = Domingo
        dias_matriz = cal.monthdayscalendar(self.ano_atual, self.mes_atual)
        
        hoje_dt = datetime.now()
        hoje_str = hoje_dt.strftime("%d/%m/%Y")
        
        for r_idx, semana in enumerate(dias_matriz):
            for c_idx, dia_num in enumerate(semana):
                if dia_num == 0:
                    continue
                    
                data_str = f"{dia_num:02d}/{self.mes_atual:02d}/{self.ano_atual}"
                is_hoje = (data_str == hoje_str)
                is_selecionado = (data_str == self.data_selecionada_str)
                
                info_dia = resumo_mes.get(data_str, {"tem_entrega": False, "tem_nota": False, "qtd": 0})
                
                # Montar o card de dia na grade
                self.criar_celula_dia(
                    row=r_idx + 1,
                    col=c_idx,
                    dia_num=dia_num,
                    data_str=data_str,
                    is_hoje=is_hoje,
                    is_selecionado=is_selecionado,
                    info_dia=info_dia
                )
                
        # Atualizar o painel lateral com a data selecionada
        self.atualizar_painel_eventos()

    def criar_celula_dia(self, row, col, dia_num, data_str, is_hoje, is_selecionado, info_dia):
        """Cria o botão de dia individual com bordas mais grossas e destaque especial para dias com eventos/notas."""
        tem_eventos = info_dia["qtd"] > 0

        # Estilização conforme estados (selecionado, com eventos, hoje, normal)
        if is_selecionado:
            bg_col = PALETTE["active_pill"]
            txt_col = "#FFFFFF"
            border_c = PALETTE["active_pill"]
            border_w = 3
        elif tem_eventos:
            # Destaque especial em rosa suave com borda marcante para dias com notas ou entregas
            bg_col = ("#FDE8EB", "#2E1F22")
            txt_col = PALETTE["brand_title"]
            border_c = PALETTE["active_pill"]
            border_w = 3
        elif is_hoje:
            bg_col = PALETTE["inactive_hover"]
            txt_col = PALETTE["brand_title"]
            border_c = PALETTE["active_pill"]
            border_w = 3
        else:
            bg_col = "transparent"
            txt_col = PALETTE["title_text"]
            border_c = PALETTE["card_border"]
            border_w = 2

        day_frame = ctk.CTkFrame(
            self.cal_container,
            fg_color=bg_col,
            border_color=border_c,
            border_width=border_w,
            corner_radius=12
        )
        day_frame.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
        day_frame.grid_columnconfigure(0, weight=1)
        day_frame.grid_rowconfigure(0, weight=1)
        
        # Botão transparente para acionar clique no dia inteiro
        btn_click = ctk.CTkButton(
            day_frame,
            text=str(dia_num),
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=txt_col,
            fg_color="transparent",
            hover_color=PALETTE["inactive_hover"],
            corner_radius=12,
            command=lambda d=data_str: self.selecionar_dia(d)
        )
        btn_click.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Badges de entregas ou notas na parte inferior do dia (tamanho ampliado)
        if tem_eventos:
            badges_box = ctk.CTkFrame(day_frame, fg_color="transparent")
            badges_box.place(relx=0.5, rely=0.76, anchor="center")
            
            if info_dia["tem_entrega"]:
                b_ent = ctk.CTkLabel(
                    badges_box,
                    text="📦",
                    font=ctk.CTkFont(size=17)
                )
                b_ent.pack(side="left", padx=2)
                
            if info_dia["tem_nota"]:
                b_not = ctk.CTkLabel(
                    badges_box,
                    text="📝",
                    font=ctk.CTkFont(size=17)
                )
                b_not.pack(side="left", padx=2)

    def selecionar_dia(self, data_str):
        """Seleciona um dia na agenda e recarrega os eventos no painel lateral."""
        self.data_selecionada_str = data_str
        self.atualizar_calendario()

    def mes_anterior(self):
        """Navega para o mês anterior."""
        if self.mes_atual == 1:
            self.mes_atual = 12
            self.ano_atual -= 1
        else:
            self.mes_atual -= 1
        self.atualizar_calendario()

    def proximo_mes(self):
        """Navega para o próximo mês."""
        if self.mes_atual == 12:
            self.mes_atual = 1
            self.ano_atual += 1
        else:
            self.mes_atual += 1
        self.atualizar_calendario()

    def ir_para_hoje(self):
        """Volta para a data atual."""
        hoje = datetime.now()
        self.ano_atual = hoje.year
        self.mes_atual = hoje.month
        self.data_selecionada_str = hoje.strftime("%d/%m/%Y")
        self.atualizar_calendario()

    def atualizar_painel_eventos(self):
        """Atualiza a lista de eventos para a data atualmente selecionada."""
        self.lbl_data_painel.configure(text=f"Eventos em {self.data_selecionada_str}")
        
        # Limpar widgets anteriores do scrollable frame
        for child in self.events_scroll.winfo_children():
            child.destroy()
            
        eventos = self.service.obter_eventos_por_data(self.data_selecionada_str)
        
        if not eventos:
            lbl_empty = ctk.CTkLabel(
                self.events_scroll,
                text="Nenhum compromisso ou entrega agendada para este dia.",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=PALETTE["subtitle_text"],
                wraplength=220
            )
            lbl_empty.pack(pady=40, anchor="center")
            return

        for ev in eventos:
            is_entrega = (ev.get("tipo") == "entrega")
            
            card = ctk.CTkFrame(
                self.events_scroll,
                fg_color=PALETTE["sidebar_bg"] if is_entrega else PALETTE["card_bg"],
                border_color=PALETTE["active_pill"] if is_entrega else PALETTE["card_border"],
                border_width=1,
                corner_radius=12
            )
            card.pack(fill="x", pady=6, padx=4)
            card.grid_columnconfigure(0, weight=1)
            
            # Badge de Tipo (Entrega Automática ou Nota)
            top_box = ctk.CTkFrame(card, fg_color="transparent")
            top_box.pack(fill="x", padx=12, pady=(10, 2))
            
            tag_text = "ENTREGA DE PEDIDO" if is_entrega else "LEMBRETE PESSOAL"
            tag_color = PALETTE["brand_title"] if is_entrega else PALETTE["brand_subtitle"]
            
            ctk.CTkLabel(
                top_box,
                text=tag_text,
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                text_color=tag_color
            ).pack(side="left")
            
            ctk.CTkLabel(
                top_box,
                text=ev.get("horario", ""),
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color=PALETTE["subtitle_text"]
            ).pack(side="right")
            
            # Título do evento
            lbl_ev_title = ctk.CTkLabel(
                card,
                text=ev.get("titulo", ""),
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=PALETTE["title_text"],
                anchor="w",
                justify="left",
                wraplength=220
            )
            lbl_ev_title.pack(fill="x", padx=12, pady=(2, 8))
            
            # Se for nota pessoal, permite excluir
            if not is_entrega:
                btn_del = ctk.CTkButton(
                    card,
                    text="🗑️ Excluir Nota",
                    height=28,
                    corner_radius=8,
                    fg_color="transparent",
                    text_color="#C62828",
                    hover_color="#FFEBEE",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    command=lambda nid=ev["id"]: self.acao_excluir_nota(nid)
                )
                btn_del.pack(anchor="e", padx=10, pady=(0, 8))

    def acao_adicionar_nota(self):
        """Abre a modal para adicionar uma nova nota para a data selecionada."""
        def on_save(data_str, titulo, horario):
            self.service.adicionar_nota(data_str, titulo, horario)
            self.data_selecionada_str = data_str
            self.atualizar_calendario()
            messagebox.showinfo("Sucesso", "Nota adicionada à agenda!", parent=self)

        modal = NotaFormModal(self, data_padrao=self.data_selecionada_str, on_save=on_save)

    def acao_excluir_nota(self, nota_id):
        """Exclui a nota pessoal selecionada."""
        if self.service.remover_nota(nota_id):
            self.atualizar_calendario()
            messagebox.showinfo("Sucesso", "Nota removida da agenda!", parent=self)
