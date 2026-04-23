import tkinter as tk
from database import BancoDeDados
from tema import COR, FONTE
from aba_busca import AbaBusca
from abas_basicas import AbaProfessores, AbaAlunos, AbaPlanos
from abas_matriculas import AbaMatriculas, AbaAcompanhamento
from abas_treinos import AbaExercicios, AbaFicha


class FitLifeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.banco = BancoDeDados()
        self._configurar_janela()
        self._construir()
        self.protocol("WM_DELETE_WINDOW", self._ao_fechar)

    def _configurar_janela(self):
        self.title("FitLife — Gestão de Academia")
        self.geometry("1400x860")
        self.minsize(1100, 680)
        self.configure(bg=COR["fundo"])

    def _construir(self):
        # ── Cabeçalho com logo ──────────────────────────────────────
        cab = tk.Frame(self, bg=COR["card"], pady=0)
        cab.pack(fill="x")

        logo_frame = tk.Frame(cab, bg=COR["card"])
        logo_frame.pack(side="left", padx=16, pady=6)
        self._desenhar_logo(logo_frame)

        # Separador vertical
        tk.Frame(cab, bg=COR["borda"], width=1).pack(side="left", fill="y", pady=8, padx=8)

        info_frame = tk.Frame(cab, bg=COR["card"])
        info_frame.pack(side="left", pady=10)
        tk.Label(info_frame, text="Gestão completa de alunos, planos, treinos e fichas",
                 font=FONTE["pequeno"], bg=COR["card"], fg=COR["muted"]).pack(anchor="w")
        tk.Label(info_frame, text="Academia • Saúde • Performance",
                 font=FONTE["tag"], bg=COR["card"],
                 fg=COR["acento_muted"]).pack(anchor="w")

        # Linha acento laranja
        tk.Frame(self, bg=COR["acento"], height=3).pack(fill="x")

        # ── Barra de abas ────────────────────────────────────────────
        self.barra_abas = tk.Frame(self, bg=COR["card2"])
        self.barra_abas.pack(fill="x")

        # ── Área de conteúdo ─────────────────────────────────────────
        self.area = tk.Frame(self, bg=COR["fundo"])
        self.area.pack(fill="both", expand=True)

        self._abas_config = [
            ("Busca",         AbaBusca),
            ("Professores",   AbaProfessores),
            ("Alunos",        AbaAlunos),
            ("Planos",        AbaPlanos),
            ("Matriculas",    AbaMatriculas),
            ("Acompan.",      AbaAcompanhamento),
            ("Exercicios",    AbaExercicios),
            ("Ficha",         AbaFicha),
        ]

        self._frames    = {}
        self._btn_abas  = {}
        self._aba_atual = None

        for titulo, Cls in self._abas_config:
            frame = Cls(self.area, self.banco)
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._frames[titulo] = frame

            btn = tk.Button(
                self.barra_abas,
                text=titulo,
                font=FONTE["botao"],
                bg=COR["card2"],
                fg=COR["muted"],
                activebackground=COR["acento"],
                activeforeground=COR["texto"],
                relief="flat",
                padx=14, pady=10,
                cursor="hand2",
                command=lambda t=titulo: self._mostrar_aba(t),
            )
            btn.pack(side="left")
            self._btn_abas[titulo] = btn

        # Rodapé
        rodape = tk.Frame(self, bg=COR["card"], pady=5)
        rodape.pack(fill="x", side="bottom")
        tk.Label(rodape,
                 text="FitLife  •  Gestão de Academia  •  Todos os direitos reservados",
                 font=FONTE["tag"], bg=COR["card"], fg=COR["desab"]).pack()

        self._mostrar_aba("Busca")

    def _desenhar_logo(self, parent):
        """Renderiza a logo FitLife no canvas usando as formas do SVG."""
        c = tk.Canvas(parent, width=140, height=52, bg=COR["card"],
                      highlightthickness=0)
        c.pack()

        # Escala: SVG original 680×340, queremos ~140×52 → scale ≈ 0.206×0.153
        # Centralizado verticalmente em y
        sx, sy = 0.206, 0.153
        ox, oy = 0, 0

        def rx(x): return int(x * sx + ox)
        def ry(y): return int(y * sy + oy)
        def rw(w): return max(1, int(w * sx))
        def rh(h): return max(1, int(h * sy))

        # Placas esquerdas
        c.create_rectangle(rx(192), ry(128), rx(192)+rw(14), ry(128)+rh(44),
                            fill=COR["texto"], outline="")
        c.create_rectangle(rx(178), ry(134), rx(178)+rw(14), ry(134)+rh(32),
                            fill=COR["texto"], outline="")
        # Placas direitas
        c.create_rectangle(rx(474), ry(128), rx(474)+rw(14), ry(128)+rh(44),
                            fill=COR["texto"], outline="")
        c.create_rectangle(rx(488), ry(134), rx(488)+rw(14), ry(134)+rh(32),
                            fill=COR["texto"], outline="")
        # Barra central
        c.create_rectangle(rx(206), ry(146), rx(206)+rw(268), ry(146)+rh(8),
                            fill=COR["texto"], outline="")
        # Linha laranja
        c.create_rectangle(rx(280), ry(157), rx(280)+rw(120), ry(157)+rh(3),
                            fill=COR["acento"], outline="")

        # Texto "Fit" + "Life"
        tx = rx(340)
        ty = ry(220)
        c.create_text(tx - 12, ty, text="Fit", font=("Segoe UI", 16, "bold"),
                      fill=COR["texto"], anchor="e")
        c.create_text(tx - 12, ty, text="    Life", font=("Segoe UI", 16, "bold"),
                      fill=COR["acento"], anchor="e")

        # ACADEMIA tagline
        c.create_text(tx, ry(240), text="ACADEMIA", font=FONTE["tag"],
                      fill=COR["muted"], anchor="center")

    def _mostrar_aba(self, titulo):
        if self._aba_atual == titulo:
            return
        self._aba_atual = titulo
        for t, btn in self._btn_abas.items():
            if t == titulo:
                btn.config(bg=COR["acento"], fg=COR["texto"])
            else:
                btn.config(bg=COR["card2"], fg=COR["muted"])
        frame = self._frames[titulo]
        frame.lift()
        if hasattr(frame, "atualizar"):
            frame.atualizar()

    def _ao_fechar(self):
        self.banco.fechar()
        self.destroy()
