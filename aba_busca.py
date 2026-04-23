import tkinter as tk
from tema import COR, FONTE
from widgets import make_button, make_label_secao, make_separador, ScrollFrame

HINT = "Buscar por nome, CPF, grupo muscular, dia, plano..."


class AbaBusca(tk.Frame):
    def __init__(self, parent, banco):
        super().__init__(parent, bg=COR["card"])
        self.banco = banco
        self._timer = None
        self._construir()

    def _construir(self):
        barra = tk.Frame(self, bg=COR["card"], pady=10, padx=14)
        barra.pack(fill="x")

        tk.Label(barra, text="BUSCA GLOBAL", font=FONTE["secao"],
                 bg=COR["card"], fg=COR["acento_claro"]).pack(anchor="w", pady=(0, 6))

        linha = tk.Frame(barra, bg=COR["card"])
        linha.pack(fill="x")

        self.e_busca = tk.Entry(linha, font=FONTE["corpo"],
                                bg=COR["campo"], fg=COR["texto"],
                                insertbackground=COR["acento_claro"],
                                relief="flat", bd=6)
        self.e_busca.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.e_busca.bind("<KeyRelease>", self._buscar_live)
        self.e_busca.insert(0, HINT)
        self.e_busca.config(fg=COR["muted"])
        self.e_busca.bind("<FocusIn>",  self._clear_hint)
        self.e_busca.bind("<FocusOut>", self._restore_hint)

        make_button(linha, "Limpar", cor_bg=COR["borda"], cor_fg=COR["muted"],
                    comando=self._limpar).pack(side="left")

        self.lbl_status = tk.Label(self, text="Digite para buscar em todo o banco de dados.",
                                    font=FONTE["pequeno"], bg=COR["card"], fg=COR["muted"])
        self.lbl_status.pack(anchor="w", padx=14, pady=(0, 4))

        tk.Frame(self, bg=COR["borda"], height=1).pack(fill="x")

        sf = ScrollFrame(self)
        sf.pack(fill="both", expand=True)
        self.lista = sf.interior

    def _clear_hint(self, _):
        if self.e_busca.get() == HINT:
            self.e_busca.delete(0, "end")
            self.e_busca.config(fg=COR["texto"])

    def _restore_hint(self, _):
        if not self.e_busca.get().strip():
            self.e_busca.insert(0, HINT)
            self.e_busca.config(fg=COR["muted"])

    def _buscar_live(self, _):
        if self._timer:
            self.after_cancel(self._timer)
        self._timer = self.after(300, lambda: self._executar(self.e_busca.get()))

    def _executar(self, termo):
        for w in self.lista.winfo_children():
            w.destroy()
        t = termo.strip()
        if not t or t == HINT:
            self.lbl_status.config(text="Digite para buscar em todo o banco de dados.")
            return

        res   = self.banco.buscar_global(t)
        total = sum(len(v) for v in res.values())
        self.lbl_status.config(text=f'{total} resultado(s) para "{t}"')

        if total == 0:
            tk.Label(self.lista, text="Nenhum resultado encontrado.",
                     font=FONTE["corpo"], bg=COR["fundo"], fg=COR["muted"]).pack(padx=16, pady=20)
            return

        for cat, itens in res.items():
            if not itens:
                continue
            make_label_secao(self.lista, f"{cat}  ({len(itens)})").pack(
                anchor="w", padx=16, pady=(12, 2))
            make_separador(self.lista).pack(fill="x", padx=16, pady=(0, 4))
            for item in itens:
                row = tk.Frame(self.lista, bg=COR["card2"], padx=14, pady=8,
                               highlightbackground=COR["borda"], highlightthickness=1)
                row.pack(fill="x", padx=24, pady=2)
                tk.Label(row, text=item["principal"], font=FONTE["subtitulo"],
                         bg=COR["card2"], fg=COR["texto"]).pack(anchor="w")
                tk.Label(row, text=item["detalhe"], font=FONTE["pequeno"],
                         bg=COR["card2"], fg=COR["muted"]).pack(anchor="w")

    def _limpar(self):
        self.e_busca.delete(0, "end")
        self._restore_hint(None)
        for w in self.lista.winfo_children():
            w.destroy()
        self.lbl_status.config(text="Digite para buscar em todo o banco de dados.")

    def atualizar(self):
        pass
