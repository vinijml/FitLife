import tkinter as tk
from tkinter import filedialog, messagebox
import sqlite3
import os
from tema import COR, FONTE

try:
    from PIL import Image, ImageTk
    _PIL_OK = True
except ImportError:
    _PIL_OK = False
from widgets import (make_field, make_button, make_label_secao,
                     make_separador, make_label_erro, make_badge,
                     AvatarLabel, ScrollFrame, validar_cpf, formatar_cpf,
                     status_cores, _rebuild_menu)


# ─── Aba Professores ─────────────────────────────────────────────────
class AbaProfessores(tk.Frame):
    def __init__(self, parent, banco):
        super().__init__(parent, bg=COR["card"])
        self.banco = banco
        self._construir()

    def _construir(self):
        form = tk.Frame(self, bg=COR["card"], pady=10, padx=14)
        form.pack(fill="x")

        tk.Label(form, text="NOVO PROFESSOR", font=FONTE["secao"],
                 bg=COR["card"], fg=COR["acento_claro"]).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))

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

        self.e_nome = col("Nome *",        28, 0)
        self.e_esp  = col("Especialidade", 22, 1)
        self.e_tel  = col("Telefone",      16, 2)
        make_button(form, "+ Adicionar", comando=self._adicionar).grid(
            row=1, column=3, sticky="s", padx=(8, 0))

        self.lbl_erro = make_label_erro(self)
        self.lbl_erro.pack(fill="x", padx=14)
        make_separador(self).pack(fill="x", pady=4)

        sf = ScrollFrame(self)
        sf.pack(fill="both", expand=True)
        self.lista = sf.interior
        self._carregar()

    def _carregar(self):
        for w in self.lista.winfo_children():
            w.destroy()
        make_label_secao(self.lista, "Professores Cadastrados").pack(
            anchor="w", padx=16, pady=(10, 4))
        make_separador(self.lista).pack(fill="x", padx=16, pady=(0, 6))
        profs = self.banco.listar_professores()
        if not profs:
            tk.Label(self.lista, text="Nenhum professor cadastrado.",
                     font=FONTE["corpo"], bg=COR["fundo"], fg=COR["muted"]).pack(padx=16, pady=8)
            return
        for p in profs:
            row = tk.Frame(self.lista, bg=COR["card2"], padx=14, pady=10,
                           highlightbackground=COR["borda"], highlightthickness=1)
            row.pack(fill="x", padx=16, pady=3)

            av = AvatarLabel(row, nome=p["Nome"], size=38)
            av.pack(side="left", padx=(0, 12))

            info = tk.Frame(row, bg=COR["card2"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=p["Nome"], font=FONTE["subtitulo"],
                     bg=COR["card2"], fg=COR["texto"]).pack(anchor="w")
            tk.Label(info,
                     text=f"{p['Especialidade'] or '—'}   |   {p['Telefone'] or '—'}",
                     font=FONTE["pequeno"], bg=COR["card2"], fg=COR["muted"]).pack(anchor="w")

            make_button(row, "Remover", cor_bg=COR["vermelho"],
                        comando=lambda pid=p["ID_Professor"]: self._deletar(pid)
                        ).pack(side="right")

    def _adicionar(self):
        n = self.e_nome.get().strip()
        if not n:
            self.lbl_erro.config(text="Nome é obrigatório.")
            return
        self.lbl_erro.config(text="")
        self.banco.adicionar_professor(n, self.e_esp.get().strip(), self.e_tel.get().strip())
        for e in (self.e_nome, self.e_esp, self.e_tel):
            e.delete(0, "end")
        self._carregar()

    def _deletar(self, pid):
        self.banco.deletar_professor(pid)
        self._carregar()

    def atualizar(self):
        self._carregar()


# ─── Aba Alunos ──────────────────────────────────────────────────────
class AbaAlunos(tk.Frame):
    def __init__(self, parent, banco):
        super().__init__(parent, bg=COR["card"])
        self.banco = banco
        self._foto_tk = {}      # cache de PhotoImage por ID_Aluno
        self._construir()

    def _construir(self):
        # ── Formulário ──
        form = tk.Frame(self, bg=COR["card"], pady=10, padx=14)
        form.pack(fill="x")

        tk.Label(form, text="NOVO ALUNO", font=FONTE["secao"],
                 bg=COR["card"], fg=COR["acento_claro"]).grid(
            row=0, column=0, columnspan=7, sticky="w", pady=(0, 6))

        def col(hint, width, c):
            ct = tk.Frame(form, bg=COR["card"])
            ct.grid(row=1, column=c, padx=(0, 8), sticky="ew")
            tk.Label(ct, text=hint, font=FONTE["pequeno"],
                     bg=COR["card"], fg=COR["muted"]).pack(anchor="w")
            e = tk.Entry(ct, font=FONTE["corpo"], width=width,
                         bg=COR["campo"], fg=COR["texto"],
                         insertbackground=COR["acento_claro"],
                         relief="flat", bd=5)
            e.pack(fill="x")
            return e

        self.e_nome  = col("Nome *",          22, 0)
        self.e_cpf   = col("CPF *",           14, 1)
        self.e_tel   = col("Telefone",        13, 2)
        self.e_email = col("Email",           20, 3)
        self.e_nasc  = col("Nascimento",      11, 4)

        # Indicador de CPF
        self.lbl_cpf_ok = tk.Label(form, text="", font=FONTE["tag"],
                                   bg=COR["card"], fg=COR["verde"])
        self.lbl_cpf_ok.grid(row=2, column=1, sticky="w")

        self.e_cpf.bind("<KeyRelease>", self._checar_cpf)

        make_button(form, "+ Adicionar", comando=self._adicionar).grid(
            row=1, column=5, sticky="s", padx=(8, 0))

        self.lbl_erro = make_label_erro(self)
        self.lbl_erro.pack(fill="x", padx=14)
        make_separador(self).pack(fill="x", pady=4)

        # ── Barra de busca ──
        bb = tk.Frame(self, bg=COR["fundo"], pady=6, padx=14)
        bb.pack(fill="x")
        tk.Label(bb, text="Buscar:", font=FONTE["pequeno"],
                 bg=COR["fundo"], fg=COR["muted"]).pack(side="left")
        self.e_busca = tk.Entry(bb, font=FONTE["corpo"], width=28,
                                bg=COR["campo"], fg=COR["texto"],
                                insertbackground=COR["acento_claro"],
                                relief="flat", bd=4)
        self.e_busca.pack(side="left", padx=(6, 0))
        self.e_busca.bind("<KeyRelease>", lambda e: self._carregar())

        make_separador(self).pack(fill="x")

        sf = ScrollFrame(self)
        sf.pack(fill="both", expand=True)
        self.lista = sf.interior
        self._carregar()

    def _checar_cpf(self, event=None):
        txt = self.e_cpf.get()
        digits = "".join(c for c in txt if c.isdigit())
        if len(digits) == 11:
            if validar_cpf(txt):
                self.lbl_cpf_ok.config(text="CPF valido", fg=COR["verde"])
            else:
                self.lbl_cpf_ok.config(text="CPF invalido", fg=COR["vermelho"])
        else:
            self.lbl_cpf_ok.config(text="")

    def _carregar(self):
        for w in self.lista.winfo_children():
            w.destroy()

        busca = self.e_busca.get().strip()
        alunos = self.banco.listar_alunos()
        if busca:
            bl = busca.lower()
            alunos = [a for a in alunos
                      if bl in (a["Nome"] or "").lower()
                      or bl in (a["CPF"] or "").lower()
                      or bl in (a["Email"] or "").lower()]

        make_label_secao(self.lista, f"Alunos Cadastrados ({len(alunos)})").pack(
            anchor="w", padx=16, pady=(10, 4))
        make_separador(self.lista).pack(fill="x", padx=16, pady=(0, 6))

        if not alunos:
            tk.Label(self.lista, text="Nenhum aluno encontrado.",
                     font=FONTE["corpo"], bg=COR["fundo"], fg=COR["muted"]).pack(padx=16, pady=8)
            return

        for a in alunos:
            self._card_aluno(a)

    def _card_aluno(self, a):
        row = tk.Frame(self.lista, bg=COR["card2"], padx=14, pady=10,
                       highlightbackground=COR["borda"], highlightthickness=1)
        row.pack(fill="x", padx=16, pady=3)

        # Foto ou avatar
        foto_path = a["Foto"]
        if _PIL_OK and foto_path and os.path.isfile(foto_path):
            try:
                img = Image.open(foto_path).resize((48, 48))
                tk_img = ImageTk.PhotoImage(img)
                self._foto_tk[a["ID_Aluno"]] = tk_img
                lbl_foto = tk.Label(row, image=tk_img, bg=COR["card2"],
                                    cursor="hand2")
                lbl_foto.pack(side="left", padx=(0, 12))
                lbl_foto.bind("<Button-1>",
                              lambda e, aid=a["ID_Aluno"]: self._trocar_foto(aid))
            except Exception:
                self._avatar_clicavel(row, a)
        else:
            self._avatar_clicavel(row, a)

        # Informações
        info = tk.Frame(row, bg=COR["card2"])
        info.pack(side="left", fill="x", expand=True)

        linha1 = tk.Frame(info, bg=COR["card2"])
        linha1.pack(anchor="w", fill="x")
        tk.Label(linha1, text=a["Nome"], font=FONTE["subtitulo"],
                 bg=COR["card2"], fg=COR["texto"]).pack(side="left")

        # Badge de status de matrícula
        mat = self.banco.buscar_matricula_aluno(a["ID_Aluno"])
        if mat:
            fg, bg = status_cores(mat["Status"])
            make_badge(linha1, mat["Status"], fg, bg).pack(side="left", padx=(8, 0))

        tk.Label(info,
                 text=f"CPF: {a['CPF'] or '—'}   |   {a['Email'] or '—'}   |   {a['Telefone'] or '—'}",
                 font=FONTE["pequeno"], bg=COR["card2"], fg=COR["muted"]).pack(anchor="w")

        if mat:
            tk.Label(info,
                     text=f"Plano: {mat['Plano']}   |   Venc.: {_iso_para_br_str(mat['Vencimento'])}   |   Prof.: {mat['Professor'] or '—'}",
                     font=FONTE["pequeno"], bg=COR["card2"], fg=COR["acento_claro"]).pack(anchor="w")

        # Ações
        btns = tk.Frame(row, bg=COR["card2"])
        btns.pack(side="right")

        qtd = self.banco.contagem_ficha_aluno(a["ID_Aluno"])
        if qtd:
            tk.Label(btns, text=f"{qtd} exerc.",
                     font=FONTE["tag"], bg=COR["card2"], fg=COR["muted"]).pack(side="left", padx=(0, 8))

        make_button(btns, "Remover", cor_bg=COR["vermelho"],
                    comando=lambda aid=a["ID_Aluno"]: self._deletar(aid)
                    ).pack(side="left")

    def _avatar_clicavel(self, row, a):
        av = AvatarLabel(row, nome=a["Nome"], size=48)
        av.pack(side="left", padx=(0, 12))
        av.config(cursor="hand2")
        av.bind("<Button-1>",
                lambda e, aid=a["ID_Aluno"]: self._trocar_foto(aid))
        tk.Label(row, text="Clique para\nadicionar foto",
                 font=FONTE["tag"], bg=COR["card2"],
                 fg=COR["desab"]).pack(side="left", padx=(0, 8))

    def _trocar_foto(self, aid):
        if not _PIL_OK:
            msg = "Para exibir fotos instale o Pillow no seu venv:\n  pip install pillow\nO caminho sera salvo mesmo assim."
            messagebox.showinfo("Pillow nao instalado", msg)
        path = filedialog.askopenfilename(
            title="Selecionar foto do aluno",
            filetypes=[("Imagens", "*.jpg *.jpeg *.png *.webp *.bmp"), ("Todos", "*.*")]
        )
        if path:
            self.banco.atualizar_foto_aluno(aid, path)
            self._carregar()


    def _adicionar(self):
        n = self.e_nome.get().strip()
        cpf = self.e_cpf.get().strip()
        if not n:
            self.lbl_erro.config(text="Nome é obrigatório.")
            return
        if cpf:
            if not validar_cpf(cpf):
                self.lbl_erro.config(text="CPF inválido. Verifique os dígitos.")
                return
        try:
            self.banco.adicionar_aluno(
                n, cpf or None,
                self.e_tel.get().strip(),
                self.e_email.get().strip(),
                nascimento=self.e_nasc.get().strip()
            )
            self.lbl_erro.config(text="")
            self.lbl_cpf_ok.config(text="")
            for e in (self.e_nome, self.e_cpf, self.e_tel, self.e_email, self.e_nasc):
                e.delete(0, "end")
            self._carregar()
        except sqlite3.IntegrityError:
            self.lbl_erro.config(text="CPF já cadastrado.")

    def _deletar(self, aid):
        self.banco.deletar_aluno(aid)
        self._carregar()

    def atualizar(self):
        self._carregar()


def _iso_para_br_str(d):
    if not d:
        return "—"
    try:
        from datetime import datetime
        return datetime.strptime(d.strip(), "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return d


# ─── Aba Planos ──────────────────────────────────────────────────────
class AbaPlanos(tk.Frame):
    def __init__(self, parent, banco):
        super().__init__(parent, bg=COR["card"])
        self.banco = banco
        self._construir()

    def _construir(self):
        form = tk.Frame(self, bg=COR["card"], pady=10, padx=14)
        form.pack(fill="x")

        tk.Label(form, text="NOVO PLANO", font=FONTE["secao"],
                 bg=COR["card"], fg=COR["acento_claro"]).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))

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

        self.e_nome = col("Nome do plano *", 28, 0)
        self.e_dur  = col("Duração (dias)",  13, 1)
        self.e_val  = col("Valor (R$)",      12, 2)
        make_button(form, "+ Adicionar", comando=self._adicionar).grid(
            row=1, column=3, sticky="s", padx=(8, 0))

        self.lbl_erro = make_label_erro(self)
        self.lbl_erro.pack(fill="x", padx=14)
        make_separador(self).pack(fill="x", pady=4)

        sf = ScrollFrame(self)
        sf.pack(fill="both", expand=True)
        self.lista = sf.interior
        self._carregar()

    def _carregar(self):
        for w in self.lista.winfo_children():
            w.destroy()
        make_label_secao(self.lista, "Planos Disponíveis").pack(
            anchor="w", padx=16, pady=(10, 4))
        make_separador(self.lista).pack(fill="x", padx=16, pady=(0, 6))
        planos = self.banco.listar_planos()
        if not planos:
            tk.Label(self.lista, text="Nenhum plano cadastrado.",
                     font=FONTE["corpo"], bg=COR["fundo"], fg=COR["muted"]).pack(padx=16, pady=8)
            return
        for p in planos:
            row = tk.Frame(self.lista, bg=COR["card2"], padx=14, pady=10,
                           highlightbackground=COR["borda"], highlightthickness=1)
            row.pack(fill="x", padx=16, pady=3)

            info = tk.Frame(row, bg=COR["card2"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=p["Nome"], font=FONTE["subtitulo"],
                     bg=COR["card2"], fg=COR["texto"]).pack(anchor="w")
            dur = f"{p['Duracao']} dias" if p["Duracao"] else "—"
            val = f"R$ {p['Valor']:.2f}".replace(".", ",") if p["Valor"] else "—"
            tk.Label(info, text=f"Duração: {dur}   |   Valor: {val}",
                     font=FONTE["pequeno"], bg=COR["card2"], fg=COR["muted"]).pack(anchor="w")

            make_button(row, "Remover", cor_bg=COR["vermelho"],
                        comando=lambda pid=p["ID_Plano"]: self._deletar(pid)
                        ).pack(side="right")

    def _adicionar(self):
        n = self.e_nome.get().strip()
        if not n:
            self.lbl_erro.config(text="Nome é obrigatório.")
            return
        try:
            val = float(self.e_val.get().strip().replace(",", "."))
        except ValueError:
            val = 0.0
        self.lbl_erro.config(text="")
        self.banco.adicionar_plano(n, self.e_dur.get().strip(), val)
        for e in (self.e_nome, self.e_dur, self.e_val):
            e.delete(0, "end")
        self._carregar()

    def _deletar(self, pid):
        self.banco.deletar_plano(pid)
        self._carregar()

    def atualizar(self):
        self._carregar()
