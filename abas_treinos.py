import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os
import webbrowser
from collections import defaultdict
from tema import COR, FONTE, DIAS_SEMANA, GRUPOS_MUSCULARES
from widgets import (make_button, make_label_secao, make_separador,
                     make_label_erro, make_badge, ScrollFrame, _rebuild_menu)


def _abrir_midia(url_ou_path):
    """Abre vídeo/URL no player nativo do sistema operacional."""
    if not url_ou_path:
        return
    if url_ou_path.startswith("http://") or url_ou_path.startswith("https://"):
        webbrowser.open(url_ou_path)
    elif os.path.isfile(url_ou_path):
        if sys.platform.startswith("win"):
            os.startfile(url_ou_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", url_ou_path])
        else:
            subprocess.Popen(["xdg-open", url_ou_path])
    else:
        messagebox.showwarning("Mídia não encontrada",
                               f"Não foi possível abrir:\n{url_ou_path}")


# ─── Aba Exercícios ──────────────────────────────────────────────────
class AbaExercicios(tk.Frame):
    def __init__(self, parent, banco):
        super().__init__(parent, bg=COR["card"])
        self.banco = banco
        self._construir()

    def _construir(self):
        form = tk.Frame(self, bg=COR["card"], pady=10, padx=14)
        form.pack(fill="x")

        tk.Label(form, text="NOVO EXERCÍCIO", font=FONTE["secao"],
                 bg=COR["card"], fg=COR["acento_claro"]).grid(
            row=0, column=0, columnspan=5, sticky="w", pady=(0, 6))

        def col(hint, width, c):
            ct = tk.Frame(form, bg=COR["card"])
            ct.grid(row=1, column=c, padx=(0, 10), sticky="ew")
            tk.Label(ct, text=hint, font=FONTE["pequeno"],
                     bg=COR["card"], fg=COR["muted"]).pack(anchor="w")
            e = tk.Entry(ct, font=FONTE["corpo"], width=width,
                         bg=COR["campo"], fg=COR["texto"],
                         insertbackground=COR["acento_claro"],
                         relief="flat", bd=5)
            e.pack(fill="x")
            return e

        self.e_nome  = col("Nome *",                       22, 0)

        # Grupo muscular via dropdown
        ct_g = tk.Frame(form, bg=COR["card"])
        ct_g.grid(row=1, column=1, padx=(0, 10), sticky="ew")
        tk.Label(ct_g, text="Grupo muscular", font=FONTE["pequeno"],
                 bg=COR["card"], fg=COR["muted"]).pack(anchor="w")
        self.var_grupo = tk.StringVar(value=GRUPOS_MUSCULARES[0])
        om_g = tk.OptionMenu(ct_g, self.var_grupo, *GRUPOS_MUSCULARES)
        om_g.config(font=FONTE["corpo"], bg=COR["campo"], fg=COR["texto"],
                    activebackground=COR["borda"], activeforeground=COR["texto"],
                    highlightthickness=0, relief="flat", width=16)
        om_g["menu"].config(bg=COR["campo"], fg=COR["texto"], font=FONTE["corpo"],
                            activebackground=COR["acento"], activeforeground=COR["texto"])
        om_g.pack(fill="x")

        self.e_desc  = col("Descrição",                    22, 2)
        self.e_video = col("Link do vídeo (YouTube, TikTok, etc.)", 28, 3)

        make_button(form, "+ Adicionar", comando=self._adicionar).grid(
            row=1, column=4, sticky="s", padx=(8, 0))

        self.lbl_erro = make_label_erro(self)
        self.lbl_erro.pack(fill="x", padx=14)

        # ── Filtros ──
        fb = tk.Frame(self, bg=COR["fundo"], pady=6, padx=14)
        fb.pack(fill="x")
        tk.Label(fb, text="Filtrar:", font=FONTE["pequeno"],
                 bg=COR["fundo"], fg=COR["muted"]).pack(side="left")
        self.e_filtro = tk.Entry(fb, font=FONTE["corpo"], width=24,
                                 bg=COR["campo"], fg=COR["texto"],
                                 insertbackground=COR["acento_claro"],
                                 relief="flat", bd=4)
        self.e_filtro.pack(side="left", padx=(6, 10))
        self.e_filtro.bind("<KeyRelease>", lambda e: self._carregar())

        make_separador(self).pack(fill="x")

        sf = ScrollFrame(self)
        sf.pack(fill="both", expand=True)
        self.lista = sf.interior
        self._carregar()

    def _carregar(self):
        for w in self.lista.winfo_children():
            w.destroy()
        busca = self.e_filtro.get().strip() or None
        exs = self.banco.listar_exercicios(busca=busca)
        grupos = defaultdict(list)
        for e in exs:
            grupos[e["Grupo_muscular"] or "Sem grupo"].append(e)

        if not grupos:
            tk.Label(self.lista, text="Nenhum exercício encontrado.",
                     font=FONTE["corpo"], bg=COR["fundo"], fg=COR["muted"]).pack(padx=16, pady=16)
            return

        for grupo, exs_g in sorted(grupos.items()):
            make_label_secao(self.lista, f"{grupo} ({len(exs_g)})").pack(
                anchor="w", padx=16, pady=(12, 2))
            make_separador(self.lista).pack(fill="x", padx=16, pady=(0, 4))
            for e in exs_g:
                row = tk.Frame(self.lista, bg=COR["card2"], padx=14, pady=8,
                               highlightbackground=COR["borda"], highlightthickness=1)
                row.pack(fill="x", padx=24, pady=2)

                info = tk.Frame(row, bg=COR["card2"])
                info.pack(side="left", fill="x", expand=True)
                tk.Label(info, text=e["Nome"], font=FONTE["subtitulo"],
                         bg=COR["card2"], fg=COR["texto"]).pack(anchor="w")
                tk.Label(info, text=e["Descricao"] or "—",
                         font=FONTE["pequeno"], bg=COR["card2"], fg=COR["muted"]).pack(anchor="w")
                if e["Video"]:
                    tk.Label(info, text=f"Link: {e['Video']}",
                             font=FONTE["tag"], bg=COR["card2"],
                             fg=COR["azul"], cursor="hand2").pack(anchor="w")

                btns = tk.Frame(row, bg=COR["card2"])
                btns.pack(side="right")
                if e["Video"]:
                    make_button(btns, "Ver Video", cor_bg=COR["azul"],
                                comando=lambda v=e["Video"]: _abrir_midia(v)
                                ).pack(side="left", padx=(0, 6))
                make_button(btns, "Remover", cor_bg=COR["vermelho"],
                            comando=lambda eid=e["ID_Exercicio"]: self._deletar(eid)
                            ).pack(side="left")

    def _adicionar(self):
        n = self.e_nome.get().strip()
        if not n:
            self.lbl_erro.config(text="Nome é obrigatório.")
            return
        self.lbl_erro.config(text="")
        self.banco.adicionar_exercicio(
            n, self.var_grupo.get(),
            self.e_desc.get().strip(),
            self.e_video.get().strip()
        )
        self.e_nome.delete(0, "end")
        self.e_desc.delete(0, "end")
        self.e_video.delete(0, "end")
        self._carregar()

    def _deletar(self, eid):
        self.banco.deletar_exercicio(eid)
        self._carregar()

    def atualizar(self):
        self._carregar()



# ─── Aba Ficha ────────────────────────────────────────────────────────
class AbaFicha(tk.Frame):
    """
    Layout de duas colunas:
      Esquerda  — lista de alunos (clicável, com busca)
      Direita   — ficha do aluno selecionado organizada por dia,
                  com formulário inline para adicionar exercício por dia
                  e botão de remover em cada exercício
    """

    def __init__(self, parent, banco):
        super().__init__(parent, bg=COR["fundo"])
        self.banco       = banco
        self._aluno_id   = None
        self._aluno_nome = ""
        self._aluno_map  = {}   # nome -> id
        self._ex_map     = {}   # nome -> id
        self._construir()

    # ─── Layout principal ─────────────────────────────────────────────
    def _construir(self):
        corpo = tk.Frame(self, bg=COR["fundo"])
        corpo.pack(fill="both", expand=True)

        # ── Coluna esquerda: lista de alunos ──────────────────────────
        col_esq = tk.Frame(corpo, bg=COR["card"], width=260)
        col_esq.pack(side="left", fill="y")
        col_esq.pack_propagate(False)

        # Cabeçalho
        cab_esq = tk.Frame(col_esq, bg=COR["card"], padx=12, pady=10)
        cab_esq.pack(fill="x")
        tk.Label(cab_esq, text="ALUNOS", font=FONTE["secao"],
                 bg=COR["card"], fg=COR["acento_claro"]).pack(anchor="w")

        # Busca de aluno
        self.e_busca_aluno = tk.Entry(
            col_esq, font=FONTE["corpo"],
            bg=COR["campo"], fg=COR["texto"],
            insertbackground=COR["acento_claro"],
            relief="flat", bd=5)
        self.e_busca_aluno.pack(fill="x", padx=12, pady=(0, 6))
        self.e_busca_aluno.bind("<KeyRelease>", lambda e: self._renderizar_lista_alunos())

        make_separador(col_esq).pack(fill="x")

        sf_alunos = ScrollFrame(col_esq, bg=COR["card"])
        sf_alunos.pack(fill="both", expand=True)
        self.lista_alunos = sf_alunos.interior

        # Separador vertical
        tk.Frame(corpo, bg=COR["borda"], width=1).pack(side="left", fill="y")

        # ── Coluna direita: ficha do aluno ───────────────────────────
        self.col_dir = tk.Frame(corpo, bg=COR["fundo"])
        self.col_dir.pack(side="left", fill="both", expand=True)

        self._mostrar_placeholder()

    # ─── Lista de alunos ──────────────────────────────────────────────
    def _renderizar_lista_alunos(self):
        for w in self.lista_alunos.winfo_children():
            w.destroy()

        busca = self.e_busca_aluno.get().strip().lower()
        alunos = [
            (nome, aid) for nome, aid in sorted(self._aluno_map.items())
            if busca in nome.lower()
        ]

        if not alunos:
            tk.Label(self.lista_alunos, text="Nenhum aluno.",
                     font=FONTE["pequeno"], bg=COR["card"],
                     fg=COR["muted"]).pack(padx=12, pady=8)
            return

        for nome, aid in alunos:
            selecionado = (aid == self._aluno_id)
            bg = COR["acento"]      if selecionado else COR["card"]
            fg = COR["texto"]       if selecionado else COR["texto"]
            fg_sub = COR["texto"]   if selecionado else COR["muted"]

            btn_frame = tk.Frame(self.lista_alunos, bg=bg,
                                 cursor="hand2", pady=8, padx=12)
            btn_frame.pack(fill="x")

            inicial = nome[0].upper()
            av = tk.Canvas(btn_frame, width=32, height=32,
                           bg=bg, highlightthickness=0)
            av.pack(side="left", padx=(0, 10))
            av_cor = COR["texto"] if selecionado else COR["acento_muted"]
            av.create_oval(1, 1, 31, 31, fill=av_cor, outline="")
            av.create_text(16, 16, text=inicial,
                           font=("Segoe UI", 11, "bold"),
                           fill=COR["acento_claro"] if not selecionado else COR["texto"])

            info = tk.Frame(btn_frame, bg=bg)
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=nome, font=FONTE["corpo"],
                     bg=bg, fg=fg, anchor="w").pack(anchor="w")

            # Contagem de exercícios na ficha
            qtd = self.banco.contagem_ficha_aluno(aid)
            if qtd:
                tk.Label(info, text=f"{qtd} exerc. na ficha",
                         font=FONTE["tag"], bg=bg, fg=fg_sub).pack(anchor="w")

            make_separador(self.lista_alunos, bg=COR["borda"]).pack(fill="x")

            # Bindings para selecionar
            for widget in [btn_frame, av, info] + info.winfo_children():
                try:
                    widget.bind("<Button-1>",
                                lambda e, n=nome, a=aid: self._selecionar_aluno(n, a))
                except Exception:
                    pass

    def _selecionar_aluno(self, nome, aid):
        self._aluno_id   = aid
        self._aluno_nome = nome
        self._renderizar_lista_alunos()
        self._renderizar_ficha()

    # ─── Placeholder ──────────────────────────────────────────────────
    def _mostrar_placeholder(self):
        for w in self.col_dir.winfo_children():
            w.destroy()
        tk.Label(self.col_dir,
                 text="Selecione um aluno na lista ao lado.",
                 font=FONTE["corpo"], bg=COR["fundo"], fg=COR["muted"]).pack(
                     expand=True)

    # ─── Ficha do aluno ───────────────────────────────────────────────
    def _renderizar_ficha(self):
        for w in self.col_dir.winfo_children():
            w.destroy()

        if not self._aluno_id:
            self._mostrar_placeholder()
            return

        # Recarregar mapa de exercícios
        exs = self.banco.listar_exercicios()
        self._ex_map = {e["Nome"]: e["ID_Exercicio"] for e in exs}

        # ── Cabeçalho da ficha ──
        cab = tk.Frame(self.col_dir, bg=COR["card"], padx=16, pady=10)
        cab.pack(fill="x")

        mat = self.banco.buscar_matricula_aluno(self._aluno_id)

        nome_f = tk.Frame(cab, bg=COR["card"])
        nome_f.pack(anchor="w", fill="x")
        tk.Label(nome_f, text=self._aluno_nome, font=FONTE["subtitulo"],
                 bg=COR["card"], fg=COR["texto"]).pack(side="left")
        if mat:
            from widgets import status_cores, make_badge
            fg_s, bg_s = status_cores(mat["Status"])
            make_badge(nome_f, mat["Status"], fg_s, bg_s).pack(
                side="left", padx=(8, 0))

        if mat:
            tk.Label(cab,
                     text=f"Plano: {mat['Plano']}   |   Prof.: {mat['Professor'] or '—'}",
                     font=FONTE["pequeno"], bg=COR["card"],
                     fg=COR["muted"]).pack(anchor="w")

        make_separador(self.col_dir).pack(fill="x")

        # ── Área scrollável com os dias ──
        sf = ScrollFrame(self.col_dir)
        sf.pack(fill="both", expand=True)
        area = sf.interior

        # Buscar todos os exercícios da ficha deste aluno
        todos = self.banco.listar_ficha(self._aluno_id)

        # Agrupar por dia (mantendo a ordem dos dias da semana)
        por_dia = {}
        for d in todos:
            chave = d["Dia"] or "Sem dia definido"
            por_dia.setdefault(chave, []).append(d)

        # Ordenar dias pela ordem de DIAS_SEMANA; dias não reconhecidos vão ao final
        ordem = {d: i for i, d in enumerate(DIAS_SEMANA)}
        dias_ordenados = sorted(
            por_dia.keys(),
            key=lambda x: ordem.get(x, len(DIAS_SEMANA))
        )

        # Renderizar cada dia
        for dia_nome in dias_ordenados:
            self._card_dia(area, dia_nome, por_dia[dia_nome])

        # ── Formulário para adicionar exercício em um novo dia ──
        self._form_adicionar(area)

    # ─── Card de um dia ───────────────────────────────────────────────
    def _card_dia(self, parent, dia_nome, exercicios):
        concluidos = sum(1 for e in exercicios if e["Concluido"])

        card = tk.Frame(parent, bg=COR["card"],
                        highlightbackground=COR["acento_muted"],
                        highlightthickness=1)
        card.pack(fill="x", padx=16, pady=(12, 0))

        # Cabeçalho do dia
        cab = tk.Frame(card, bg=COR["card"], padx=14, pady=8)
        cab.pack(fill="x")

        tk.Label(cab, text=dia_nome, font=FONTE["subtitulo"],
                 bg=COR["card"], fg=COR["acento_claro"]).pack(side="left")

        prog_cor = (COR["verde"]   if concluidos == len(exercicios) and concluidos > 0
                    else COR["amarelo"] if concluidos > 0
                    else COR["muted"])
        tk.Label(cab, text=f"{concluidos}/{len(exercicios)} concluidos",
                 font=FONTE["tag"], bg=COR["card"],
                 fg=prog_cor).pack(side="right")

        make_separador(card, bg=COR["borda"]).pack(fill="x", padx=8)

        # Exercícios do dia
        for idx, d in enumerate(exercicios):
            self._linha_exercicio(card, d, ultimo=(idx == len(exercicios) - 1))

        # Mini-form para adicionar exercício neste dia específico
        self._mini_form_dia(card, dia_nome)

    # ─── Linha de exercício ───────────────────────────────────────────
    def _linha_exercicio(self, parent, d, ultimo=False):
        concluido = bool(d["Concluido"])
        row = tk.Frame(parent, bg=COR["card"], padx=14, pady=7)
        row.pack(fill="x")

        if not ultimo:
            make_separador(row, bg=COR["borda"]).pack(side="bottom", fill="x")

        info = tk.Frame(row, bg=COR["card"])
        info.pack(side="left", fill="x", expand=True)

        # Linha 1: nome + grupo + status
        l1 = tk.Frame(info, bg=COR["card"])
        l1.pack(anchor="w", fill="x")
        cor_nome = COR["muted"] if concluido else COR["texto"]
        tk.Label(l1, text=d["Nome"], font=FONTE["subtitulo"],
                 bg=COR["card"], fg=cor_nome).pack(side="left")
        if d["Grupo_muscular"]:
            tk.Label(l1, text=f"  {d['Grupo_muscular']}",
                     font=FONTE["tag"], bg=COR["card"],
                     fg=COR["acento_muted"]).pack(side="left")
        if concluido:
            tk.Label(l1, text="  Concluido",
                     font=FONTE["tag"], bg=COR["card"],
                     fg=COR["verde"]).pack(side="left")

        # Linha 2: detalhes
        det = f"{d['Series'] or '—'}x{d['Repeticoes'] or '—'}   |   Carga: {d['Carga'] or '—'}"
        if d["Obs"]:
            det += f"   |   {d['Obs']}"
        if concluido and d["Data_conclusao"]:
            det += f"   |   {d['Data_conclusao']}"
        tk.Label(info, text=det, font=FONTE["pequeno"],
                 bg=COR["card"], fg=COR["muted"]).pack(anchor="w")

        # Botões
        btns = tk.Frame(row, bg=COR["card"])
        btns.pack(side="right")

        lbl_tog = "Desmarcar" if concluido else "Concluir"
        cor_tog = COR["desab"] if concluido else COR["verde"]
        make_button(btns, lbl_tog, cor_bg=cor_tog,
                    comando=lambda fid=d["ID_Ficha"], val=not concluido:
                    self._marcar(fid, val)).pack(side="left", padx=(0, 6))

        if d["Video"]:
            make_button(btns, "Ver Video", cor_bg=COR["azul"],
                        comando=lambda v=d["Video"]: _abrir_midia(v)
                        ).pack(side="left", padx=(0, 6))

        make_button(btns, "Remover", cor_bg=COR["vermelho"],
                    comando=lambda fid=d["ID_Ficha"]: self._deletar(fid)
                    ).pack(side="left")

    # ─── Mini-form inline por dia ─────────────────────────────────────
    def _mini_form_dia(self, parent, dia_nome):
        """Formulário colapsável no rodapé de cada card de dia."""

        wrapper = tk.Frame(parent, bg=COR["card2"], padx=14, pady=0)
        wrapper.pack(fill="x")

        # Estado: colapsado por padrão
        estado = {"aberto": False}
        form_frame = tk.Frame(wrapper, bg=COR["card2"])

        def toggle():
            if estado["aberto"]:
                form_frame.pack_forget()
                btn_toggle.config(text="+ Adicionar exercicio a este dia")
            else:
                form_frame.pack(fill="x", pady=(0, 8))
                btn_toggle.config(text="- Cancelar")
            estado["aberto"] = not estado["aberto"]

        btn_toggle = tk.Button(
            wrapper, text="+ Adicionar exercicio a este dia",
            font=FONTE["tag"],
            bg=COR["card2"], fg=COR["acento_claro"],
            activebackground=COR["card2"], activeforeground=COR["acento"],
            relief="flat", cursor="hand2", pady=6,
            command=toggle)
        btn_toggle.pack(anchor="w")

        # Conteúdo do form
        linha = tk.Frame(form_frame, bg=COR["card2"])
        linha.pack(fill="x")

        def field(hint, width):
            f = tk.Frame(linha, bg=COR["card2"])
            f.pack(side="left", padx=(0, 8))
            tk.Label(f, text=hint, font=FONTE["tag"],
                     bg=COR["card2"], fg=COR["muted"]).pack(anchor="w")
            e = tk.Entry(f, font=FONTE["corpo"], width=width,
                         bg=COR["campo"], fg=COR["texto"],
                         insertbackground=COR["acento_claro"],
                         relief="flat", bd=4)
            e.pack()
            return e

        # Dropdown de exercício
        ex_f = tk.Frame(linha, bg=COR["card2"])
        ex_f.pack(side="left", padx=(0, 8))
        tk.Label(ex_f, text="Exercicio", font=FONTE["tag"],
                 bg=COR["card2"], fg=COR["muted"]).pack(anchor="w")
        var_ex = tk.StringVar(value=list(self._ex_map.keys())[0] if self._ex_map else "")
        om = tk.OptionMenu(ex_f, var_ex, *self._ex_map.keys() if self._ex_map else [""])
        om.config(font=FONTE["pequeno"], bg=COR["campo"], fg=COR["texto"],
                  activebackground=COR["borda"], activeforeground=COR["texto"],
                  highlightthickness=0, relief="flat", width=18)
        om["menu"].config(bg=COR["campo"], fg=COR["texto"], font=FONTE["pequeno"],
                          activebackground=COR["acento"], activeforeground=COR["texto"])
        om.pack()

        e_series = field("Series", 5)
        e_reps   = field("Reps",   5)
        e_carga  = field("Carga",  6)
        e_obs    = field("Obs",    10)

        lbl_err = tk.Label(form_frame, text="", font=FONTE["tag"],
                           bg=COR["card2"], fg=COR["vermelho"])
        lbl_err.pack(anchor="w")

        def salvar():
            eid = self._ex_map.get(var_ex.get())
            if not eid:
                lbl_err.config(text="Selecione um exercicio.")
                return
            lbl_err.config(text="")
            self.banco.adicionar_ficha(
                self._aluno_id, eid, dia_nome,
                e_series.get().strip(),
                e_reps.get().strip(),
                e_carga.get().strip(),
                e_obs.get().strip(),
            )
            self._renderizar_ficha()

        make_button(linha, "Salvar", comando=salvar).pack(
            side="left", padx=(4, 0))

    # ─── Formulário para adicionar em um novo dia ─────────────────────
    def _form_adicionar(self, parent):
        """Formulário para adicionar exercício em um dia ainda não existente na ficha."""
        sep_frame = tk.Frame(parent, bg=COR["fundo"], pady=10)
        sep_frame.pack(fill="x", padx=16)
        make_separador(sep_frame).pack(fill="x")
        tk.Label(sep_frame, text="ADICIONAR EM NOVO DIA",
                 font=FONTE["secao"], bg=COR["fundo"],
                 fg=COR["acento_claro"]).pack(anchor="w", pady=(8, 0))

        form = tk.Frame(parent, bg=COR["card"], padx=14, pady=12,
                        highlightbackground=COR["borda"], highlightthickness=1)
        form.pack(fill="x", padx=16, pady=(4, 16))

        linha1 = tk.Frame(form, bg=COR["card"])
        linha1.pack(fill="x", pady=(0, 6))

        def field(hint, width, parent_f):
            f = tk.Frame(parent_f, bg=COR["card"])
            f.pack(side="left", padx=(0, 10))
            tk.Label(f, text=hint, font=FONTE["pequeno"],
                     bg=COR["card"], fg=COR["muted"]).pack(anchor="w")
            e = tk.Entry(f, font=FONTE["corpo"], width=width,
                         bg=COR["campo"], fg=COR["texto"],
                         insertbackground=COR["acento_claro"],
                         relief="flat", bd=5)
            e.pack()
            return e

        # Exercício
        ex_f = tk.Frame(linha1, bg=COR["card"])
        ex_f.pack(side="left", padx=(0, 10))
        tk.Label(ex_f, text="Exercicio *", font=FONTE["pequeno"],
                 bg=COR["card"], fg=COR["muted"]).pack(anchor="w")
        self.var_ex_novo = tk.StringVar(
            value=list(self._ex_map.keys())[0] if self._ex_map else "")
        self.om_ex_novo = tk.OptionMenu(ex_f, self.var_ex_novo, *self._ex_map.keys()
                                        if self._ex_map else [""])
        self.om_ex_novo.config(font=FONTE["corpo"], bg=COR["campo"], fg=COR["texto"],
                               activebackground=COR["borda"], activeforeground=COR["texto"],
                               highlightthickness=0, relief="flat", width=20)
        self.om_ex_novo["menu"].config(bg=COR["campo"], fg=COR["texto"], font=FONTE["corpo"],
                                       activebackground=COR["acento"],
                                       activeforeground=COR["texto"])
        self.om_ex_novo.pack()

        # Dia
        dia_f = tk.Frame(linha1, bg=COR["card"])
        dia_f.pack(side="left", padx=(0, 10))
        tk.Label(dia_f, text="Dia *", font=FONTE["pequeno"],
                 bg=COR["card"], fg=COR["muted"]).pack(anchor="w")
        self.var_dia_novo = tk.StringVar(value=DIAS_SEMANA[0])
        om_dia = tk.OptionMenu(dia_f, self.var_dia_novo, *DIAS_SEMANA)
        om_dia.config(font=FONTE["corpo"], bg=COR["campo"], fg=COR["texto"],
                      activebackground=COR["borda"], activeforeground=COR["texto"],
                      highlightthickness=0, relief="flat", width=16)
        om_dia["menu"].config(bg=COR["campo"], fg=COR["texto"], font=FONTE["corpo"],
                              activebackground=COR["acento"], activeforeground=COR["texto"])
        om_dia.pack()

        linha2 = tk.Frame(form, bg=COR["card"])
        linha2.pack(fill="x")

        self.e_series_novo = field("Series",   6, linha2)
        self.e_reps_novo   = field("Reps",     6, linha2)
        self.e_carga_novo  = field("Carga",    8, linha2)
        self.e_obs_novo    = field("Obs",     14, linha2)

        self.lbl_erro_novo = tk.Label(form, text="", font=FONTE["pequeno"],
                                      bg=COR["card"], fg=COR["vermelho"])
        self.lbl_erro_novo.pack(anchor="w", pady=(4, 0))

        make_button(form, "+ Adicionar", comando=self._adicionar_novo
                    ).pack(anchor="w", pady=(6, 0))

    def _adicionar_novo(self):
        eid = self._ex_map.get(self.var_ex_novo.get())
        if not eid:
            self.lbl_erro_novo.config(text="Selecione um exercicio.")
            return
        self.lbl_erro_novo.config(text="")
        self.banco.adicionar_ficha(
            self._aluno_id, eid,
            self.var_dia_novo.get(),
            self.e_series_novo.get().strip(),
            self.e_reps_novo.get().strip(),
            self.e_carga_novo.get().strip(),
            self.e_obs_novo.get().strip(),
        )
        self._renderizar_ficha()

    # ─── Ações ────────────────────────────────────────────────────────
    def _marcar(self, fid, valor):
        self.banco.marcar_concluido_ficha(fid, valor)
        self._renderizar_ficha()

    def _deletar(self, fid):
        self.banco.deletar_ficha(fid)
        self._renderizar_ficha()

    # ─── Atualização geral ────────────────────────────────────────────
    def atualizar(self):
        alunos = self.banco.listar_alunos()
        self._aluno_map = {a["Nome"]: a["ID_Aluno"] for a in alunos}

        # Valida aluno ainda existe
        if self._aluno_nome and self._aluno_nome not in self._aluno_map:
            self._aluno_id   = None
            self._aluno_nome = ""

        self._renderizar_lista_alunos()

        if self._aluno_id:
            self._renderizar_ficha()
        else:
            self._mostrar_placeholder()
