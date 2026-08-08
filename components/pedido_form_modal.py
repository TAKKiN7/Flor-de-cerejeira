import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from config.settings import PALETTE, centralizar_janela
from services.estoque_service import EstoqueService
from services.clientes_service import ClientesService
from components.cliente_form_modal import ClienteFormModal

class PedidoFormModal(ctk.CTkToplevel):
    """Janela modal para criação e edição de pedidos integrada com Busca Inteligente de Clientes e Estoque."""
    
    def __init__(self, parent, title="Novo Pedido", pedido_data=None, on_save=None, estoque_service=None, clientes_service=None, base_dir=None, cliente_preselecionado=None):
        super().__init__(parent)
        
        self.on_save = on_save
        self.pedido_data = pedido_data
        self.estoque_service = estoque_service or EstoqueService(base_dir=base_dir)
        self.clientes_service = clientes_service or ClientesService(base_dir=base_dir)
        self.cliente_preselecionado = cliente_preselecionado
        self.todos_clientes = []
        
        # Carregar materiais do estoque
        self.estoque_lista = self.estoque_service.carregar_estoque()
        self.mapa_estoque = {f"{item['nome']} (Estoque: {item['quantidade']} {item['unidade']} | R$ {item['preco_unitario']:.2f})": item for item in self.estoque_lista}
        
        # Carregar materiais já associados ao pedido (se editando)
        self.itens_usados = []
        if pedido_data and "itens_usados" in pedido_data:
            self.itens_usados = [dict(item) for item in pedido_data["itens_usados"]]
            
        self.title(title)
        self.geometry("560x730")
        self.resizable(False, False)
        self.configure(fg_color=PALETTE["main_bg"])
        
        # Centralizar em relação à janela principal
        centralizar_janela(self, 560, 730, parent)
        self.transient(parent)
        self.grab_set()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Cabeçalho da Modal
        header_frame = ctk.CTkFrame(self, fg_color=PALETTE["sidebar_bg"], height=65, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.pack_propagate(False)
        
        lbl_header = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(family="Georgia", size=20, weight="bold"),
            text_color=PALETTE["brand_title"]
        )
        lbl_header.pack(expand=True, pady=14)
        
        # Form Container (Scrollable)
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=PALETTE["active_pill"],
            scrollbar_button_hover_color=PALETTE["active_pill_hover"]
        )
        scroll_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # 1. Data do Pedido e Data de Entrega (Lado a lado)
        row_datas = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        row_datas.pack(fill="x", pady=(0, 12))
        row_datas.grid_columnconfigure((0, 1), weight=1)
        
        # Data do Pedido
        col_ped = ctk.CTkFrame(row_datas, fg_color="transparent")
        col_ped.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(
            col_ped,
            text="Data do Pedido",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        data_ped_inicial = pedido_data.get("data_pedido", data_hoje) if pedido_data else data_hoje
        self.entry_data_pedido = ctk.CTkEntry(col_ped, height=38, corner_radius=10, border_color=PALETTE["card_border"], font=ctk.CTkFont(size=13))
        self.entry_data_pedido.pack(fill="x")
        self.entry_data_pedido.insert(0, data_ped_inicial)
        
        # Data de Entrega
        col_ent = ctk.CTkFrame(row_datas, fg_color="transparent")
        col_ent.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(
            col_ent,
            text="Data de Entrega",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        data_ent_inicial = pedido_data.get("data_entrega", "") if pedido_data else ""
        self.entry_data_entrega = ctk.CTkEntry(col_ent, placeholder_text="Ex: 15/08/2026", height=38, corner_radius=10, border_color=PALETTE["card_border"], font=ctk.CTkFont(size=13))
        self.entry_data_entrega.pack(fill="x")
        if data_ent_inicial:
            self.entry_data_entrega.insert(0, data_ent_inicial)
            
        # 2. Seleção / Busca Inteligente de Cliente do Banco de Dados
        ctk.CTkLabel(
            scroll_frame,
            text="Cliente (Busca Inteligente por nome ou contato)",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        row_cliente = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        row_cliente.pack(fill="x", pady=(0, 12))
        row_cliente.grid_columnconfigure(0, weight=1)
        
        self.combo_cliente = ctk.CTkComboBox(
            row_cliente,
            values=["(Nenhum cliente cadastrado)"],
            height=38,
            corner_radius=10,
            border_color=PALETTE["card_border"],
            fg_color=PALETTE["card_bg"],
            button_color=PALETTE["active_pill"],
            button_hover_color=PALETTE["active_pill_hover"],
            text_color=PALETTE["title_text"],
            font=ctk.CTkFont(size=13),
            dropdown_font=ctk.CTkFont(size=12)
        )
        self.combo_cliente.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.combo_cliente.bind("<KeyRelease>", self.filtrar_clientes_combo)
        
        btn_add_cliente_rapido = ctk.CTkButton(
            row_cliente,
            text="+ Novo Cliente",
            height=38,
            corner_radius=10,
            fg_color="transparent",
            border_color=PALETTE["active_pill"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.cadastrar_cliente_rapido
        )
        btn_add_cliente_rapido.grid(row=0, column=1, sticky="e")

        # Atualizar lista de clientes no dropdown
        self.carregar_opcoes_clientes()

        # 3. Nome do Produto / Encomenda
        ctk.CTkLabel(
            scroll_frame,
            text="Descrição do Produto / Encomenda",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=PALETTE["inactive_text"]
        ).pack(anchor="w", pady=(0, 4))
        
        self.entry_produto = ctk.CTkEntry(scroll_frame, placeholder_text="Ex: Quadro Ilustrado 30x40cm", height=38, corner_radius=10, border_color=PALETTE["card_border"], font=ctk.CTkFont(size=13))
        self.entry_produto.pack(fill="x", pady=(0, 14))
        if pedido_data and "produto" in pedido_data:
            self.entry_produto.insert(0, pedido_data["produto"])
            
        # --- SEÇÃO DE MATERIAIS DO ESTOQUE ---
        ctk.CTkFrame(scroll_frame, height=1, fg_color=PALETTE["card_border"]).pack(fill="x", pady=10)
        
        lbl_mat_sec = ctk.CTkLabel(
            scroll_frame,
            text="📦 Materiais do Estoque Utilizados",
            font=ctk.CTkFont(family="Georgia", size=15, weight="bold"),
            text_color=PALETTE["brand_title"]
        )
        lbl_mat_sec.pack(anchor="w", pady=(0, 8))
        
        # Painel para Adicionar Material
        panel_add_mat = ctk.CTkFrame(scroll_frame, fg_color=PALETTE["card_bg"], border_color=PALETTE["card_border"], border_width=1, corner_radius=12)
        panel_add_mat.pack(fill="x", pady=(0, 12))
        panel_add_mat.grid_columnconfigure(0, weight=1)
        
        # ComboBox com itens do estoque
        opcoes_estoque = list(self.mapa_estoque.keys()) if self.mapa_estoque else ["(Nenhum material no estoque)"]
        
        self.combo_materiais = ctk.CTkOptionMenu(
            panel_add_mat,
            values=opcoes_estoque,
            height=38,
            corner_radius=8,
            fg_color=PALETTE["sidebar_bg"],
            button_color=PALETTE["active_pill"],
            button_hover_color=PALETTE["active_pill_hover"],
            text_color=PALETTE["title_text"],
            font=ctk.CTkFont(size=12)
        )
        self.combo_materiais.pack(fill="x", padx=12, pady=(10, 8))
        if opcoes_estoque:
            self.combo_materiais.set(opcoes_estoque[0])
            
        row_qtd_add = ctk.CTkFrame(panel_add_mat, fg_color="transparent")
        row_qtd_add.pack(fill="x", padx=12, pady=(0, 10))
        row_qtd_add.grid_columnconfigure(0, weight=1)
        
        self.entry_qtd_usada = ctk.CTkEntry(
            row_qtd_add,
            placeholder_text="Qtd. usada (ex: 2)",
            height=36,
            corner_radius=8,
            border_color=PALETTE["card_border"],
            font=ctk.CTkFont(size=12)
        )
        self.entry_qtd_usada.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        btn_add_mat = ctk.CTkButton(
            row_qtd_add,
            text="+ Adicionar Item",
            height=36,
            corner_radius=8,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.adicionar_material_lista
        )
        btn_add_mat.pack(side="right")

        # Container da Lista de Materiais Adicionados
        self.frame_lista_materiais = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        self.frame_lista_materiais.pack(fill="x", pady=(0, 14))
        
        # --- SEÇÃO DO VALOR TOTAL CALCULADO COM MARGEM (Custo / (1 - 25%)) ---
        panel_valor = ctk.CTkFrame(scroll_frame, fg_color=PALETTE["sidebar_bg"], border_color=PALETTE["sidebar_border"], border_width=1, corner_radius=12)
        panel_valor.pack(fill="x", pady=(0, 14))
        
        # Linha 1: Custo dos Materiais
        row_c1 = ctk.CTkFrame(panel_valor, fg_color="transparent")
        row_c1.pack(fill="x", padx=16, pady=(10, 2))
        
        ctk.CTkLabel(
            row_c1,
            text="Custo dos Materiais (Estoque):",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=PALETTE["subtitle_text"]
        ).pack(side="left")
        
        self.lbl_custo_mat_val = ctk.CTkLabel(
            row_c1,
            text="R$ 0,00",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=PALETTE["inactive_text"]
        )
        self.lbl_custo_mat_val.pack(side="right")

        # Linha 2: Fórmula de Margem
        row_c2 = ctk.CTkFrame(panel_valor, fg_color="transparent")
        row_c2.pack(fill="x", padx=16, pady=(0, 4))
        
        ctk.CTkLabel(
            row_c2,
            text="Precificação do Atelier: Custo / (1 - 25%)",
            font=ctk.CTkFont(size=11, slant="italic"),
            text_color=PALETTE["subtitle_text"]
        ).pack(side="left")

        ctk.CTkFrame(panel_valor, height=1, fg_color=PALETTE["card_border"]).pack(fill="x", padx=16, pady=4)

        # Linha 3: Valor Final Calculado
        row_c3 = ctk.CTkFrame(panel_valor, fg_color="transparent")
        row_c3.pack(fill="x", padx=16, pady=(2, 10))
        
        ctk.CTkLabel(
            row_c3,
            text="Valor Final do Pedido:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=PALETTE["title_text"]
        ).pack(side="left")
        
        self.lbl_valor_total_val = ctk.CTkLabel(
            row_c3,
            text="R$ 0,00",
            font=ctk.CTkFont(family="Georgia", size=18, weight="bold"),
            text_color=PALETTE["brand_title"]
        )
        self.lbl_valor_total_val.pack(side="right")
        
        # Renderizar itens atuais e calcular valor total
        self.renderizar_materiais_usados()

        # Botões Inferiores de Ação (Salvar / Cancelar)
        footer_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 16))
        footer_frame.grid_columnconfigure((0, 1), weight=1)
        
        btn_cancel = ctk.CTkButton(
            footer_frame,
            text="Cancelar",
            height=42,
            corner_radius=10,
            fg_color="transparent",
            border_color=PALETTE["sidebar_border"],
            border_width=1,
            text_color=PALETTE["inactive_text"],
            hover_color=PALETTE["inactive_hover"],
            font=ctk.CTkFont(weight="bold"),
            command=self.destroy
        )
        btn_cancel.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        
        btn_save = ctk.CTkButton(
            footer_frame,
            text="Salvar Pedido",
            height=42,
            corner_radius=10,
            fg_color=PALETTE["active_pill"],
            hover_color=PALETTE["active_pill_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(weight="bold"),
            command=self.salvar
        )
        btn_save.grid(row=0, column=1, padx=(8, 0), sticky="ew")

    def carregar_opcoes_clientes(self, selecionar_novo=None):
        """Carrega a lista de clientes cadastrados no ComboBox de busca."""
        self.todos_clientes = self.clientes_service.carregar_clientes()
        if not self.todos_clientes:
            self.combo_cliente.configure(values=["(Nenhum cliente cadastrado)"])
            self.combo_cliente.set("(Nenhum cliente cadastrado)")
            return

        nomes = [c["nome_cliente"] for c in self.todos_clientes]
        self.combo_cliente.configure(values=nomes)

        if selecionar_novo and selecionar_novo in nomes:
            self.combo_cliente.set(selecionar_novo)
        elif self.cliente_preselecionado and self.cliente_preselecionado in nomes:
            self.combo_cliente.set(self.cliente_preselecionado)
        elif self.pedido_data and "nome_cliente" in self.pedido_data and self.pedido_data["nome_cliente"] in nomes:
            self.combo_cliente.set(self.pedido_data["nome_cliente"])
        else:
            self.combo_cliente.set(nomes[0])

    def filtrar_clientes_combo(self, event=None):
        """Filtra dinamicamente as opções do ComboBox à medida que o usuário digita."""
        termo = self.combo_cliente.get().strip().lower()
        if not hasattr(self, "todos_clientes") or not self.todos_clientes:
            return

        if not termo:
            nomes = [c["nome_cliente"] for c in self.todos_clientes]
            self.combo_cliente.configure(values=nomes)
            return

        filtrados = [
            c["nome_cliente"] for c in self.todos_clientes
            if termo in c["nome_cliente"].lower()
            or termo in c.get("contato", "").lower()
            or termo in c.get("id", "").lower()
        ]

        if filtrados:
            self.combo_cliente.configure(values=filtrados)
        else:
            self.combo_cliente.configure(values=["(Nenhum cliente encontrado)"])

    def cadastrar_cliente_rapido(self):
        """Abre a modal de cadastro rápido de cliente e atualiza a seleção."""
        texto_digitado = self.combo_cliente.get().strip()
        if texto_digitado in ["(Nenhum cliente cadastrado)", "(Nenhum cliente encontrado)"]:
            texto_digitado = ""

        def on_cliente_salvo(dados):
            novo_cliente = self.clientes_service.adicionar_cliente(
                nome_cliente=dados["nome_cliente"],
                endereco=dados["endereco"],
                data_ultimo_pedido=dados["data_ultimo_pedido"],
                contato=dados["contato"]
            )
            self.carregar_opcoes_clientes(selecionar_novo=novo_cliente["nome_cliente"])
            messagebox.showinfo("Sucesso", f"Cliente '{novo_cliente['nome_cliente']}' cadastrado e selecionado!", parent=self)

        modal = ClienteFormModal(
            self,
            title="Cadastro Rápido de Cliente",
            on_save=on_cliente_salvo,
            nome_inicial=texto_digitado
        )

    def adicionar_material_lista(self):
        """Adiciona o material selecionado do estoque à lista de itens do pedido."""
        opcao_selecionada = self.combo_materiais.get()
        if opcao_selecionada not in self.mapa_estoque:
            messagebox.showwarning("Seleção Inválida", "Por favor, selecione um material válido do estoque.", parent=self)
            return
            
        item_estoque = self.mapa_estoque[opcao_selecionada]
        qtd_str = self.entry_qtd_usada.get().strip().replace(",", ".")
        
        if not qtd_str:
            messagebox.showwarning("Quantidade Necessária", "Informe a quantidade do material utilizada.", parent=self)
            return
            
        try:
            qtd_usada = float(qtd_str)
            if qtd_usada <= 0:
                raise ValueError("Quantidade deve ser positiva")
        except ValueError:
            messagebox.showerror("Quantidade Inválida", "Digite um valor numérico válido para a quantidade.", parent=self)
            return
            
        qtd_em_estoque = float(item_estoque.get("quantidade", 0))
        if qtd_usada > qtd_em_estoque:
            messagebox.showwarning(
                "Estoque Insuficiente",
                f"A quantidade solicitada ({qtd_usada}) excede a quantidade disponível no estoque ({qtd_em_estoque} {item_estoque.get('unidade', '')}).",
                parent=self
            )
            return

        item_id = item_estoque["id"]
        preco_unit = float(item_estoque["preco_unitario"])
        
        item_existente = next((m for m in self.itens_usados if m["item_id"] == item_id), None)
        if item_existente:
            item_existente["quantidade"] += qtd_usada
            item_existente["subtotal"] = round(item_existente["quantidade"] * item_existente["preco_unitario"], 2)
        else:
            self.itens_usados.append({
                "item_id": item_id,
                "nome": item_estoque["nome"],
                "quantidade": qtd_usada,
                "preco_unitario": preco_unit,
                "subtotal": round(qtd_usada * preco_unit, 2)
            })

        self.entry_qtd_usada.delete(0, "end")
        self.renderizar_materiais_usados()

    def remover_material_lista(self, index):
        """Remove o material selecionado da lista de itens do pedido."""
        if 0 <= index < len(self.itens_usados):
            self.itens_usados.pop(index)
            self.renderizar_materiais_usados()

    def renderizar_materiais_usados(self):
        """Redesenha a lista visual de materiais adicionados e recalcula o valor total."""
        for child in self.frame_lista_materiais.winfo_children():
            child.destroy()

        custo_materiais = 0.0

        if not self.itens_usados:
            lbl_vazio = ctk.CTkLabel(
                self.frame_lista_materiais,
                text="Nenhum material do estoque adicionado ainda.",
                font=ctk.CTkFont(size=12, slant="italic"),
                text_color=PALETTE["subtitle_text"]
            )
            lbl_vazio.pack(anchor="w", pady=4)
        else:
            for idx, item in enumerate(self.itens_usados):
                subtotal = float(item.get("subtotal", item.get("quantidade", 0) * item.get("preco_unitario", 0)))
                custo_materiais += subtotal
                
                row_item = ctk.CTkFrame(
                    self.frame_lista_materiais,
                    fg_color=PALETTE["card_bg"],
                    border_color=PALETTE["card_border"],
                    border_width=1,
                    corner_radius=8
                )
                row_item.pack(fill="x", pady=2)
                row_item.grid_columnconfigure(0, weight=1)
                
                lbl_desc = ctk.CTkLabel(
                    row_item,
                    text=f"• {item['nome']} (x{item['quantidade']})",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=PALETTE["title_text"],
                    anchor="w"
                )
                lbl_desc.pack(side="left", padx=10, pady=6)
                
                lbl_price = ctk.CTkLabel(
                    row_item,
                    text=f"R$ {subtotal:.2f}",
                    font=ctk.CTkFont(size=12),
                    text_color=PALETTE["brand_subtitle"]
                )
                lbl_price.pack(side="left", padx=10, pady=6)
                
                btn_del = ctk.CTkButton(
                    row_item,
                    text="❌",
                    width=28,
                    height=28,
                    fg_color="transparent",
                    hover_color="#FFEBEE",
                    text_color="#C62828",
                    command=lambda i=idx: self.remover_material_lista(i)
                )
                btn_del.pack(side="right", padx=6, pady=4)

        # Cálculo do valor final do pedido aplicando a fórmula: Custo / (1 - 25%)
        if custo_materiais > 0:
            valor_final = custo_materiais / (1.0 - 0.25)
        else:
            valor_final = 0.0

        custo_fmt = f"R$ {custo_materiais:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        valor_fmt = f"R$ {valor_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        self.lbl_custo_mat_val.configure(text=custo_fmt)
        self.lbl_valor_total_val.configure(text=valor_fmt)
        self.valor_total_calculado = round(valor_final, 2)

    def salvar(self):
        """Valida os campos e aciona o callback de salvamento."""
        data_ped = self.entry_data_pedido.get().strip()
        cliente_selecionado = self.combo_cliente.get().strip()
        produto = self.entry_produto.get().strip()
        data_ent = self.entry_data_entrega.get().strip()
        
        if not cliente_selecionado or cliente_selecionado in ["(Nenhum cliente cadastrado)", "(Nenhum cliente encontrado)"]:
            messagebox.showwarning(
                "Cliente Obrigatório",
                "Por favor, selecione um cliente da lista ou clique em '+ Novo Cliente' para cadastrar.",
                parent=self
            )
            return

        # Verificar se o cliente digitado/selecionado existe na base
        nomes_cadastrados = [c["nome_cliente"].lower() for c in self.todos_clientes] if hasattr(self, "todos_clientes") else []
        cliente_encontrado = next((c["nome_cliente"] for c in self.todos_clientes if c["nome_cliente"].lower() == cliente_selecionado.lower()), None)

        if not cliente_encontrado:
            cadastrar_agora = messagebox.askyesno(
                "Cliente Não Encontrado",
                f"O cliente '{cliente_selecionado}' não foi encontrado no cadastro. Deseja cadastrá-lo agora?",
                parent=self
            )
            if cadastrar_agora:
                self.cadastrar_cliente_rapido()
            return
        else:
            # Usar o nome com a grafia exata do cadastro
            cliente_selecionado = cliente_encontrado

        if not produto:
            messagebox.showwarning("Campo Obrigatório", "Por favor, preencha a descrição do produto / encomenda.", parent=self)
            return
            
        if not self.itens_usados:
            confirmar_sem_estoque = messagebox.askyesno(
                "Sem Materiais do Estoque",
                "Nenhum material do estoque foi adicionado a este pedido (Valor R$ 0,00). Deseja continuar assim mesmo?",
                parent=self
            )
            if not confirmar_sem_estoque:
                return

        valor_fmt = f"{self.valor_total_calculado:.2f}"

        dados = {
            "data_pedido": data_ped if data_ped else datetime.now().strftime("%d/%m/%Y"),
            "nome_cliente": cliente_selecionado,
            "produto": produto,
            "valor_produto": valor_fmt,
            "data_entrega": data_ent if data_ent else "-",
            "itens_usados": self.itens_usados
        }
        
        if self.pedido_data and "id" in self.pedido_data:
            dados["id"] = self.pedido_data["id"]

        if self.on_save:
            self.on_save(dados)
            
        self.destroy()
