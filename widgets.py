import tkinter as tk
from tkinter import ttk
from tema import COR, FONTE


# ── Entradas ─────────────────────────────────────────────────────────
def make_field(parent, hint="", width=18):
    """Label + Entry empilhados."""
    frame = tk.Frame(parent, bg=COR["card"])
    tk.Label(frame, text=hint, font=FONTE["pequeno"],
             bg=COR["card"], fg=COR["muted"]).pack(anchor="w")
    e = tk.Entry(frame, font=FONTE["corpo"], width=width,
                 bg=COR["campo"], fg=COR["texto"],
                 insertbackground=COR["acento_claro"],
                 relief="flat", bd=5)
    e.pack(fill="x")
    return frame, e


def make_button(parent, texto, cor_bg=None, cor_fg=None, comando=None, largura=None):
    bg = cor_bg or COR["acento"]
    fg = cor_fg or COR["texto"]
    kw = dict(
        text=texto, font=FONTE["botao"],
        bg=bg, fg=fg,
        activebackground=COR["acento_hover"],
        activeforeground=COR["texto"],
        relief="flat", cursor="hand2",
        padx=12, pady=6,
        command=comando or (lambda: None),
    )
    if largura:
        kw["width"] = largura
    btn = tk.Button(parent, **kw)
    # hover suave
    btn.bind("<Enter>", lambda e: btn.config(bg=COR["acento_hover"] if cor_bg is None else bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def make_dropdown(parent, hint, valores, width=18):
    """Label + OptionMenu empilhados."""
    container = tk.Frame(parent, bg=COR["card"])
    tk.Label(container, text=hint, font=FONTE["pequeno"],
             bg=COR["card"], fg=COR["muted"]).pack(anchor="w")
    var = tk.StringVar(value=valores[0] if valores else "")
    om = tk.OptionMenu(container, var, *valores if valores else [""])
    om.config(font=FONTE["corpo"], bg=COR["campo"], fg=COR["texto"],
              activebackground=COR["borda"], activeforeground=COR["texto"],
              highlightthickness=0, relief="flat", width=width)
    om["menu"].config(bg=COR["campo"], fg=COR["texto"], font=FONTE["corpo"],
                      activebackground=COR["acento"], activeforeground=COR["texto"])
    om.pack(fill="x")
    return container, var, om


def _rebuild_menu(om, var, valores):
    menu = om["menu"]
    menu.delete(0, "end")
    for v in valores:
        menu.add_command(label=v, command=lambda val=v: var.set(val))
    if valores:
        var.set(valores[0])
    else:
        var.set("")


def make_label_secao(parent, texto, bg=None):
    bg = bg or COR["fundo"]
    return tk.Label(parent, text=texto.upper(),
                    font=FONTE["secao"], bg=bg,
                    fg=COR["acento_claro"])


def make_separador(parent, bg=None):
    return tk.Frame(parent, bg=bg or COR["borda"], height=1)


def make_label_erro(parent, bg=None):
    return tk.Label(parent, text="", font=FONTE["pequeno"],
                    bg=bg or COR["card"], fg=COR["vermelho"])


def make_badge(parent, texto, cor_fg, cor_bg, bold=True):
    f = FONTE["tag"] if bold else FONTE["pequeno"]
    return tk.Label(parent, text=f" {texto} ", font=f,
                    bg=cor_bg, fg=cor_fg, padx=4, pady=2)


def status_cores(status):
    """Retorna (fg, bg) para um status de matrícula."""
    m = {
        "Ativa":    (COR["verde"],   COR["verde_bg"]),
        "Inativa":  (COR["muted"],   COR["desab"]),
        "Suspensa": (COR["amarelo"], COR["amarelo_bg"]),
        "Vencida":  (COR["vermelho"],COR["vermelho_bg"]),
    }
    return m.get(status, (COR["muted"], COR["desab"]))


# ── Avatar com inicial ────────────────────────────────────────────────
class AvatarLabel(tk.Canvas):
    def __init__(self, parent, nome="?", size=44, **kw):
        super().__init__(parent, width=size, height=size,
                         bg=COR["card"], highlightthickness=0, **kw)
        self._size = size
        self._draw(nome)

    def _draw(self, nome):
        s = self._size
        self.delete("all")
        self.create_oval(2, 2, s-2, s-2, fill=COR["acento_muted"], outline=COR["acento"])
        inicial = nome[0].upper() if nome else "?"
        self.create_text(s//2, s//2, text=inicial, fill=COR["acento_claro"],
                         font=("Segoe UI", s//3, "bold"))

    def update_nome(self, nome):
        self._draw(nome)


# ── ScrollFrame ────────────────────────────────────────────────────────
class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg=None, **kwargs):
        bg = bg or COR["fundo"]
        super().__init__(parent, bg=bg, **kwargs)
        canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.interior = tk.Frame(canvas, bg=bg)
        self.interior.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        win = canvas.create_window((0, 0), window=self.interior, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(win, width=e.width))

        def _scroll(e):
            canvas.yview_scroll(int(-1*(e.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _scroll)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")


# ── Validação de CPF ────────────────────────────────────────────────────
def validar_cpf(cpf: str) -> bool:
    digits = "".join(c for c in cpf if c.isdigit())
    if len(digits) != 11 or len(set(digits)) == 1:
        return False
    for i in range(9, 11):
        soma = sum(int(digits[n]) * ((i + 1) - n) for n in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(digits[i]):
            return False
    return True


def formatar_cpf(cpf: str) -> str:
    digits = "".join(c for c in cpf if c.isdigit())[:11]
    if len(digits) >= 9:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    if len(digits) >= 6:
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:]}"
    if len(digits) >= 3:
        return f"{digits[:3]}.{digits[3:]}"
    return digits
