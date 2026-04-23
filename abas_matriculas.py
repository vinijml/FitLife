import tkinter as tk
from tema import COR, FONTE, STATUS_MATRICULA
from widgets import (make_button, make_label_secao, make_separador,
                     make_label_erro, make_badge, ScrollFrame,
                     status_cores, _rebuild_menu)


class AbaMatriculas(tk.Frame):
    def __init__(self, parent, banco):
        super().__init__(parent, bg=COR["card"])
        self.banco = banco
        self._aluno_map = {}
        self._plano_map = {}   # nome -> {id, duracao, valor}
        self._prof_map  = {}
        self._construir()

    def _construir(self):
        form = tk.Frame(self, bg=COR["card"], pady=10, padx=14)
        form.pack(fill="x")

        tk.Label(form, text="NOVA MATRÍCULA", font=FONTE["secao"],
                 bg=COR["card"], fg=COR["acento_claro"]).grid(
            row=0, column=0, columnspan=5, sticky="w", pady=(0, 6))

        def dd(hint, c, width=16):
            ct = tk.Frame(form, bg=COR["card"])
            ct.grid(row=1, column=c, padx=(0, 8), sticky="ew")
            tk.Label(ct, text=hint, font=FONTE["pequeno"],
                     bg=COR["card"], fg=COR["muted"]).pack(anchor="w")
            var = tk.StringVar(value="")
            om = tk.OptionMenu(ct, var, "")
            om.config(font=FONTE["corpo"], bg=COR["campo"], fg=COR["texto"],
                      activebackground=COR["borda"], activeforeground=COR["texto"],
                      highlightthickness=0, relief="flat", width=width)
            om["menu"].config(bg=COR["campo"], fg=COR["texto"], font=FONTE["corpo"],
                              activebackground=COR["acento"], activeforeground=COR["texto"])
            om.pack(fill="x")
            return var, om

        self.var_aluno, self.om_aluno = dd("Aluno",     0, 22)
        self.var_plano, self.om_plano = dd("Plano",     1, 18)
        self.var_prof,  self.om_prof  = dd("Professor", 2, 16)

        # Info do plano selecionado (preenchida automaticamente)
        ct_info = tk.Frame(form, bg=COR["card"])
        ct_info.grid(row=1, column=3, padx=(0, 8), sticky="ew")
        tk.Label(ct_info, text="Duração / Valor", font=FONTE["pequeno"],
                 bg=COR["card"], fg=COR["muted"]).pack(anchor="w")
        self.lbl_plano_info = tk.Label(
            ct_info, text="—", font=FONTE["corpo"],
            bg=COR["campo"], fg=COR["acento_claro"],
            padx=8, pady=5, anchor="w")
        self.lbl_plano_info.pack(fill="x")

        # Atualiza info quando plano muda
        self.var_plano.trace_add("write", self._on_plano_change)

        # Status
        ct_st = tk.Frame(form, bg=COR["card"])
        ct_st.grid(row=1, column=4, padx=(0, 8), sticky="ew")
        tk.Label(ct_st, text="Status", font=FONTE["pequeno"],
                 bg=COR["card"], fg=COR["muted"]).pack(anchor="w")
        self.var_status = tk.StringVar(value="Ativa")
        om_st = tk.OptionMenu(ct_st, self.var_status, *STATUS_MATRICULA)
        om_st.config(font=FONTE["corpo"], bg=COR["campo"], fg=COR["texto"],
                     activebackground=COR["borda"], activeforeground=COR["texto"],
                     highlightthickness=0, relief="flat", width=10)
        om_st["menu"].config(bg=COR["campo"], fg=COR["texto"], font=FONTE["corpo"],
                             activebackground=COR["acento"], activeforeground=COR["texto"])
        om_st.pack(fill="x")

        make_button(form, "+ Matricular", comando=self._adicionar).grid(
            row=1, column=5, sticky="s", padx=(8, 0))

        self.lbl_erro = make_label_erro(self)
        self.lbl_erro.pack(fill="x", padx=14)
        make_separador(self).pack(fill="x", pady=4)

        sf = ScrollFrame(self)
        sf.pack(fill="both", expand=True)
        self.lista = sf.interior
        self.atualizar()

    def _on_plano_change(self, *_):
        """Atualiza o label de duração/valor ao trocar o plano."""
        info = self._plano_map.get(self.var_plano.get())
        if info:
            dur = f"{info['duracao']} dias" if info["duracao"] else "—"
            val = f"R$ {info['valor']:.2f}".replace(".", ",") if info["valor"] else "—"
            self.lbl_plano_info.config(text=f"{dur}   |   {val}")
        else:
            self.lbl_plano_info.config(text="—")

    def atualizar(self):
        alunos = self.banco.listar_alunos()
        planos = self.banco.listar_planos()
        profs  = self.banco.listar_professores()
        self._aluno_map = {a["Nome"]: a["ID_Aluno"] for a in alunos}
        self._plano_map = {
            p["Nome"]: {
                "id":      p["ID_Plano"],
                "duracao": p["Duracao"],
                "valor":   p["Valor"],
            }
            for p in planos
        }
        self._prof_map = {p["Nome"]: p["ID_Professor"] for p in profs}
        _rebuild_menu(self.om_aluno, self.var_aluno, list(self._aluno_map.keys()))
        _rebuild_menu(self.om_plano, self.var_plano, list(self._plano_map.keys()))
        _rebuild_menu(self.om_prof,  self.var_prof,  list(self._prof_map.keys()))
        self._on_plano_change()   # atualiza info do plano atual
        self._carregar()

    def _carregar(self):
        for w in self.lista.winfo_children():
            w.destroy()
        mats = self.banco.listar_matriculas()
        make_label_secao(self.lista, f"Matrículas ({len(mats)})").pack(
            anchor="w", padx=16, pady=(10, 4))
        make_separador(self.lista).pack(fill="x", padx=16, pady=(0, 6))
        if not mats:
            tk.Label(self.lista, text="Nenhuma matrícula cadastrada.",
                     font=FONTE["corpo"], bg=COR["fundo"], fg=COR["muted"]).pack(padx=16, pady=8)
            return
        for m in mats:
            row = tk.Frame(self.lista, bg=COR["card2"], padx=14, pady=10,
                           highlightbackground=COR["borda"], highlightthickness=1)
            row.pack(fill="x", padx=16, pady=3)

            info = tk.Frame(row, bg=COR["card2"])
            info.pack(side="left", fill="x", expand=True)

            lin1 = tk.Frame(info, bg=COR["card2"])
            lin1.pack(anchor="w", fill="x")
            tk.Label(lin1, text=m["Aluno"], font=FONTE["subtitulo"],
                     bg=COR["card2"], fg=COR["texto"]).pack(side="left")
            fg, bg = status_cores(m["Status"])
            make_badge(lin1, m["Status"], fg, bg).pack(side="left", padx=(8, 0))

            tk.Label(info, text=f"Plano: {m['Plano']}   |   Prof.: {m['Professor'] or '—'}",
                     font=FONTE["pequeno"], bg=COR["card2"], fg=COR["muted"]).pack(anchor="w")
            tk.Label(info, text=f"Início: {m['Data_inicio']}   |   Venc.: {m['Data_fim']}",
                     font=FONTE["pequeno"], bg=COR["card2"], fg=COR["acento_claro"]).pack(anchor="w")

            make_button(row, "Remover", cor_bg=COR["vermelho"],
                        comando=lambda mid=m["ID_Matricula"]: self._deletar(mid)
                        ).pack(side="right")

    def _adicionar(self):
        a       = self._aluno_map.get(self.var_aluno.get())
        p_info  = self._plano_map.get(self.var_plano.get())
        pr      = self._prof_map.get(self.var_prof.get())
        if not a or not p_info:
            self.lbl_erro.config(text="Selecione aluno e plano.")
            return
        dur = p_info["duracao"] or 30
        self.lbl_erro.config(text="")
        self.banco.adicionar_matricula(a, p_info["id"], pr, dur, self.var_status.get())
        self._carregar()

    def _deletar(self, mid):
        self.banco.deletar_matricula(mid)
        self._carregar()


# ─── Aba Acompanhamento ──────────────────────────────────────────────
class AbaAcompanhamento(tk.Frame):
    def __init__(self, parent, banco):
        super().__init__(parent, bg=COR["card"])
        self.banco = banco
        self._prof_map  = {}
        self._aluno_map = {}
        self._construir()

    def _construir(self):
        form = tk.Frame(self, bg=COR["card"], pady=10, padx=14)
        form.pack(fill="x")

        tk.Label(form, text="VINCULAR PROFESSOR / ALUNO", font=FONTE["secao"],
                 bg=COR["card"], fg=COR["acento_claro"]).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))

        def dd(hint, c):
            ct = tk.Frame(form, bg=COR["card"])
            ct.grid(row=1, column=c, padx=(0, 10), sticky="ew")
            tk.Label(ct, text=hint, font=FONTE["pequeno"],
                     bg=COR["card"], fg=COR["muted"]).pack(anchor="w")
            var = tk.StringVar(value="")
            om = tk.OptionMenu(ct, var, "")
            om.config(font=FONTE["corpo"], bg=COR["campo"], fg=COR["texto"],
                      activebackground=COR["borda"], activeforeground=COR["texto"],
                      highlightthickness=0, relief="flat", width=22)
            om["menu"].config(bg=COR["campo"], fg=COR["texto"], font=FONTE["corpo"],
                              activebackground=COR["acento"], activeforeground=COR["texto"])
            om.pack(fill="x")
            return var, om

        self.var_prof,  self.om_prof  = dd("Professor", 0)
        self.var_aluno, self.om_aluno = dd("Aluno",     1)
        make_button(form, "Vincular", comando=self._adicionar).grid(
            row=1, column=2, sticky="s", padx=(8, 0))

        self.lbl_erro = make_label_erro(self)
        self.lbl_erro.pack(fill="x", padx=14)
        make_separador(self).pack(fill="x", pady=4)

        sf = ScrollFrame(self)
        sf.pack(fill="both", expand=True)
        self.lista = sf.interior
        self.atualizar()

    def atualizar(self):
        profs  = self.banco.listar_professores()
        alunos = self.banco.listar_alunos()
        self._prof_map  = {p["Nome"]: p["ID_Professor"] for p in profs}
        self._aluno_map = {a["Nome"]: a["ID_Aluno"]     for a in alunos}
        _rebuild_menu(self.om_prof,  self.var_prof,  list(self._prof_map.keys()))
        _rebuild_menu(self.om_aluno, self.var_aluno, list(self._aluno_map.keys()))
        self._carregar()

    def _carregar(self):
        for w in self.lista.winfo_children():
            w.destroy()
        acs = self.banco.listar_acompanhamentos()
        por_prof = {}
        for ac in acs:
            por_prof.setdefault(ac["Professor"], []).append(ac)
        if not acs:
            make_label_secao(self.lista, "Acompanhamentos").pack(
                anchor="w", padx=16, pady=(10, 4))
            tk.Label(self.lista, text="Nenhum vínculo cadastrado.",
                     font=FONTE["corpo"], bg=COR["fundo"], fg=COR["muted"]).pack(padx=16, pady=8)
            return
        for prof, lista in sorted(por_prof.items()):
            make_label_secao(self.lista, prof).pack(
                anchor="w", padx=16, pady=(12, 2))
            make_separador(self.lista).pack(fill="x", padx=16, pady=(0, 4))
            for ac in lista:
                row = tk.Frame(self.lista, bg=COR["card2"], padx=14, pady=6,
                               highlightbackground=COR["borda"], highlightthickness=1)
                row.pack(fill="x", padx=24, pady=2)
                tk.Label(row, text=f"Aluno: {ac['Aluno']}",
                         font=FONTE["corpo"], bg=COR["card2"], fg=COR["texto"]).pack(side="left")
                make_button(row, "Desvincular", cor_bg=COR["vermelho"],
                            comando=lambda ip=ac["ID_Professor"], ia=ac["ID_Aluno"]:
                            self._deletar(ip, ia)).pack(side="right")

    def _adicionar(self):
        ip = self._prof_map.get(self.var_prof.get())
        ia = self._aluno_map.get(self.var_aluno.get())
        if not ip or not ia:
            self.lbl_erro.config(text="Selecione professor e aluno.")
            return
        ok = self.banco.adicionar_acompanhamento(ip, ia)
        self.lbl_erro.config(text="" if ok else "Vínculo já existe.")
        self._carregar()

    def _deletar(self, ip, ia):
        self.banco.deletar_acompanhamento(ip, ia)
        self._carregar()
