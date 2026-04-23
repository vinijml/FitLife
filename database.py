import sqlite3
from datetime import datetime, timedelta

NOME_BANCO = "fitlife.db"


def _iso_para_br(d: str) -> str:
    try:
        return datetime.strptime(d.strip(), "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return d.strip()


def _br_para_iso(d: str) -> str:
    try:
        return datetime.strptime(d.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return d.strip()


class BancoDeDados:
    def __init__(self):
        self.conn = sqlite3.connect(NOME_BANCO)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._criar_tabelas()

   
    def _criar_tabelas(self):
        self.conn.executescript("""
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS Professor (
                ID_Professor  INTEGER PRIMARY KEY AUTOINCREMENT,
                Nome          TEXT NOT NULL,
                Especialidade TEXT,
                Telefone      TEXT
            );

            CREATE TABLE IF NOT EXISTS Aluno (
                ID_Aluno        INTEGER PRIMARY KEY AUTOINCREMENT,
                Nome            TEXT NOT NULL,
                CPF             TEXT UNIQUE,
                Telefone        TEXT,
                Email           TEXT,
                Endereco        TEXT,
                DataNascimento  TEXT,
                Foto            TEXT
            );

            CREATE TABLE IF NOT EXISTS Plano (
                ID_Plano INTEGER PRIMARY KEY AUTOINCREMENT,
                Nome     TEXT NOT NULL,
                Duracao  INTEGER DEFAULT 30,
                Valor    REAL
            );

            CREATE TABLE IF NOT EXISTS Matricula (
                ID_Matricula INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_Aluno     INTEGER NOT NULL,
                ID_Plano     INTEGER NOT NULL,
                ID_Professor INTEGER,
                Data_inicio  TEXT,
                Data_fim     TEXT,
                Status       TEXT DEFAULT 'Ativa',
                FOREIGN KEY (ID_Aluno)     REFERENCES Aluno(ID_Aluno)         ON DELETE CASCADE,
                FOREIGN KEY (ID_Plano)     REFERENCES Plano(ID_Plano)         ON DELETE CASCADE,
                FOREIGN KEY (ID_Professor) REFERENCES Professor(ID_Professor) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS Acompanha (
                ID_Professor INTEGER NOT NULL,
                ID_Aluno     INTEGER NOT NULL,
                PRIMARY KEY (ID_Professor, ID_Aluno),
                FOREIGN KEY (ID_Professor) REFERENCES Professor(ID_Professor) ON DELETE CASCADE,
                FOREIGN KEY (ID_Aluno)     REFERENCES Aluno(ID_Aluno)         ON DELETE CASCADE
            );

            -- Exercícios do banco (com vídeo e grupo)
            CREATE TABLE IF NOT EXISTS Exercicio (
                ID_Exercicio   INTEGER PRIMARY KEY AUTOINCREMENT,
                Nome           TEXT NOT NULL,
                Grupo_muscular TEXT,
                Descricao      TEXT,
                Video          TEXT
            );

            -- Ficha unificada: treino do aluno por dia
            CREATE TABLE IF NOT EXISTS Ficha (
                ID_Ficha     INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_Aluno     INTEGER NOT NULL,
                ID_Exercicio INTEGER NOT NULL,
                Dia          TEXT,
                Series       TEXT,
                Repeticoes   TEXT,
                Carga        TEXT,
                Concluido    INTEGER DEFAULT 0,
                Data_conclusao TEXT DEFAULT '',
                Obs          TEXT,
                FOREIGN KEY (ID_Aluno)     REFERENCES Aluno(ID_Aluno)         ON DELETE CASCADE,
                FOREIGN KEY (ID_Exercicio) REFERENCES Exercicio(ID_Exercicio) ON DELETE CASCADE
            );
        """)
        self.conn.commit()

 #Professor:
    def listar_professores(self):
        return self.conn.execute(
            "SELECT * FROM Professor ORDER BY Nome").fetchall()

    def adicionar_professor(self, nome, especialidade, telefone):
        self.conn.execute(
            "INSERT INTO Professor (Nome, Especialidade, Telefone) VALUES (?,?,?)",
            (nome, especialidade, telefone))
        self.conn.commit()

    def deletar_professor(self, pid):
        self.conn.execute(
            "DELETE FROM Professor WHERE ID_Professor=?", (pid,))
        self.conn.commit()

    #Alunos:
    def listar_alunos(self):
        return self.conn.execute(
            "SELECT * FROM Aluno ORDER BY Nome").fetchall()

    def adicionar_aluno(self, nome, cpf, telefone, email,
                        endereco="", nascimento="", foto=""):
        self.conn.execute(
            "INSERT INTO Aluno "
            "(Nome,CPF,Telefone,Email,Endereco,DataNascimento,Foto) "
            "VALUES (?,?,?,?,?,?,?)",
            (nome, cpf or None, telefone, email, endereco, nascimento, foto))
        self.conn.commit()

    def atualizar_foto_aluno(self, id_aluno, caminho):
        self.conn.execute(
            "UPDATE Aluno SET Foto=? WHERE ID_Aluno=?", (caminho, id_aluno))
        self.conn.commit()

    def deletar_aluno(self, aid):
        self.conn.execute("DELETE FROM Aluno WHERE ID_Aluno=?", (aid,))
        self.conn.commit()

    def buscar_aluno(self, id_aluno):
        row = self.conn.execute(
            "SELECT * FROM Aluno WHERE ID_Aluno=?", (id_aluno,)).fetchone()
        return dict(row) if row else None

    #Planos:
    def listar_planos(self):
        return self.conn.execute(
            "SELECT * FROM Plano ORDER BY Nome").fetchall()

    def adicionar_plano(self, nome, duracao, valor):
        try:
            dur = int(duracao)
        except (ValueError, TypeError):
            dur = 30
        self.conn.execute(
            "INSERT INTO Plano (Nome, Duracao, Valor) VALUES (?,?,?)",
            (nome, dur, valor))
        self.conn.commit()

    def deletar_plano(self, pid):
        self.conn.execute("DELETE FROM Plano WHERE ID_Plano=?", (pid,))
        self.conn.commit()

    #Matrículas:
    def listar_matriculas(self):
        rows = self.conn.execute("""
            SELECT m.ID_Matricula, a.Nome as Aluno, p.Nome as Plano,
                   pr.Nome as Professor,
                   m.Data_inicio, m.Data_fim, m.Status
            FROM Matricula m
            JOIN Aluno a ON a.ID_Aluno = m.ID_Aluno
            JOIN Plano p ON p.ID_Plano = m.ID_Plano
            LEFT JOIN Professor pr ON pr.ID_Professor = m.ID_Professor
            ORDER BY m.Status, a.Nome
        """).fetchall()
        resultado = []
        for r in rows:
            d = dict(r)
            d["Data_inicio"] = _iso_para_br(d["Data_inicio"] or "")
            d["Data_fim"]    = _iso_para_br(d["Data_fim"] or "")
            resultado.append(d)
        return resultado

    def adicionar_matricula(self, id_aluno, id_plano, id_prof, duracao_dias, status="Ativa"):
        inicio     = datetime.now()
        vencimento = inicio + timedelta(days=int(duracao_dias or 30))
        self.conn.execute(
            "INSERT INTO Matricula "
            "(ID_Aluno,ID_Plano,ID_Professor,Data_inicio,Data_fim,Status) "
            "VALUES (?,?,?,?,?,?)",
            (id_aluno, id_plano, id_prof or None,
             inicio.strftime("%Y-%m-%d"),
             vencimento.strftime("%Y-%m-%d"),
             status))
        self.conn.commit()

    def deletar_matricula(self, mid):
        self.conn.execute(
            "DELETE FROM Matricula WHERE ID_Matricula=?", (mid,))
        self.conn.commit()

    def buscar_matricula_aluno(self, id_aluno):
        row = self.conn.execute("""
            SELECT pr.Nome as Professor, p.Nome as Plano,
                   m.Data_fim as Vencimento, m.Status, p.Valor
            FROM Matricula m
            JOIN Plano p ON p.ID_Plano = m.ID_Plano
            LEFT JOIN Professor pr ON pr.ID_Professor = m.ID_Professor
            WHERE m.ID_Aluno = ?
            ORDER BY m.ID_Matricula DESC LIMIT 1
        """, (id_aluno,)).fetchone()
        return dict(row) if row else None

    #Acompanhamento:
    def listar_acompanhamentos(self):
        return self.conn.execute("""
            SELECT p.Nome as Professor, a.Nome as Aluno,
                   ac.ID_Professor, ac.ID_Aluno
            FROM Acompanha ac
            JOIN Professor p ON p.ID_Professor = ac.ID_Professor
            JOIN Aluno     a ON a.ID_Aluno     = ac.ID_Aluno
            ORDER BY p.Nome, a.Nome
        """).fetchall()

    def adicionar_acompanhamento(self, id_prof, id_aluno):
        try:
            self.conn.execute(
                "INSERT INTO Acompanha (ID_Professor, ID_Aluno) VALUES (?,?)",
                (id_prof, id_aluno))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def deletar_acompanhamento(self, id_prof, id_aluno):
        self.conn.execute(
            "DELETE FROM Acompanha WHERE ID_Professor=? AND ID_Aluno=?",
            (id_prof, id_aluno))
        self.conn.commit()

    #Exercícios:
    def listar_exercicios(self, grupo=None, busca=None):
        q = "SELECT * FROM Exercicio WHERE 1=1"
        p = []
        if grupo:
            q += " AND Grupo_muscular LIKE ?"
            p.append(f"%{grupo}%")
        if busca:
            q += " AND (Nome LIKE ? OR Descricao LIKE ?)"
            p.extend([f"%{busca}%", f"%{busca}%"])
        q += " ORDER BY Grupo_muscular, Nome"
        return self.conn.execute(q, p).fetchall()

    def adicionar_exercicio(self, nome, grupo, descricao, video=""):
        self.conn.execute(
            "INSERT INTO Exercicio (Nome,Grupo_muscular,Descricao,Video) VALUES (?,?,?,?)",
            (nome, grupo, descricao, video))
        self.conn.commit()

    def deletar_exercicio(self, eid):
        self.conn.execute(
            "DELETE FROM Exercicio WHERE ID_Exercicio=?", (eid,))
        self.conn.commit()

    def listar_grupos_musculares(self):
        rows = self.conn.execute(
            "SELECT DISTINCT Grupo_muscular FROM Exercicio "
            "WHERE Grupo_muscular IS NOT NULL AND Grupo_muscular != '' "
            "ORDER BY Grupo_muscular").fetchall()
        return [r[0] for r in rows]

    #Ficha unificada:
    def listar_ficha(self, id_aluno, dia=None, grupo=None, busca=None):
        q = """
            SELECT f.ID_Ficha, e.Nome, e.Grupo_muscular, e.Video,
                   f.Dia, f.Series, f.Repeticoes, f.Carga,
                   f.Concluido, f.Data_conclusao, f.Obs
            FROM Ficha f
            JOIN Exercicio e ON e.ID_Exercicio = f.ID_Exercicio
            WHERE f.ID_Aluno = ?
        """
        p = [id_aluno]
        if dia:
            q += " AND f.Dia LIKE ?"
            p.append(f"%{dia}%")
        if grupo:
            q += " AND e.Grupo_muscular LIKE ?"
            p.append(f"%{grupo}%")
        if busca:
            q += " AND (e.Nome LIKE ? OR e.Grupo_muscular LIKE ?)"
            p.extend([f"%{busca}%", f"%{busca}%"])
        q += " ORDER BY f.Dia, e.Grupo_muscular, e.Nome"
        rows = self.conn.execute(q, p).fetchall()
        resultado = []
        for r in rows:
            d = dict(r)
            d["Data_conclusao"] = _iso_para_br(d["Data_conclusao"] or "")
            resultado.append(d)
        return resultado

    def adicionar_ficha(self, id_aluno, id_exercicio, dia, series, repeticoes, carga, obs=""):
        self.conn.execute(
            "INSERT INTO Ficha "
            "(ID_Aluno,ID_Exercicio,Dia,Series,Repeticoes,Carga,Obs) "
            "VALUES (?,?,?,?,?,?,?)",
            (id_aluno, id_exercicio, dia, series, repeticoes, carga, obs))
        self.conn.commit()

    def marcar_concluido_ficha(self, id_ficha, valor):
        data = datetime.now().strftime("%Y-%m-%d") if valor else ""
        self.conn.execute(
            "UPDATE Ficha SET Concluido=?, Data_conclusao=? WHERE ID_Ficha=?",
            (1 if valor else 0, data, id_ficha))
        self.conn.commit()

    def deletar_ficha(self, id_ficha):
        self.conn.execute("DELETE FROM Ficha WHERE ID_Ficha=?", (id_ficha,))
        self.conn.commit()

    def dias_ficha_aluno(self, id_aluno):
        rows = self.conn.execute(
            "SELECT DISTINCT Dia FROM Ficha "
            "WHERE ID_Aluno=? AND Dia IS NOT NULL AND Dia != '' "
            "ORDER BY Dia",
            (id_aluno,)).fetchall()
        return [r[0] for r in rows]

    def contagem_ficha_aluno(self, id_aluno):
        r = self.conn.execute(
            "SELECT COUNT(*) FROM Ficha WHERE ID_Aluno=?", (id_aluno,)).fetchone()
        return r[0] if r else 0

    #Busca global:
    def buscar_global(self, termo):
        t = f"%{termo}%"
        alunos = self.conn.execute("""
            SELECT Nome as principal,
                   'CPF: '||COALESCE(CPF,'—')||'  |  '||COALESCE(Email,'—')||'  |  '||COALESCE(Telefone,'—') as detalhe
            FROM Aluno WHERE Nome LIKE ? OR CPF LIKE ? OR Email LIKE ? OR Telefone LIKE ?
        """, (t, t, t, t)).fetchall()

        professores = self.conn.execute("""
            SELECT Nome as principal,
                   COALESCE(Especialidade,'—')||'  |  Tel: '||COALESCE(Telefone,'—') as detalhe
            FROM Professor WHERE Nome LIKE ? OR Especialidade LIKE ? OR Telefone LIKE ?
        """, (t, t, t)).fetchall()

        planos = self.conn.execute("""
            SELECT Nome as principal,
                   CAST(COALESCE(Duracao,0) AS TEXT)||' dias  |  R$ '||CAST(COALESCE(Valor,0) AS TEXT) as detalhe
            FROM Plano WHERE Nome LIKE ?
        """, (t,)).fetchall()

        matriculas = self.conn.execute("""
            SELECT a.Nome as principal,
                   p.Nome||'  |  '||COALESCE(m.Status,'—')||'  |  venc. '||COALESCE(m.Data_fim,'—') as detalhe
            FROM Matricula m
            JOIN Aluno a ON a.ID_Aluno=m.ID_Aluno
            JOIN Plano p ON p.ID_Plano=m.ID_Plano
            WHERE a.Nome LIKE ? OR p.Nome LIKE ? OR m.Status LIKE ?
        """, (t, t, t)).fetchall()

        exercicios = self.conn.execute("""
            SELECT Nome as principal,
                   COALESCE(Grupo_muscular,'—')||'  |  '||COALESCE(Descricao,'—') as detalhe
            FROM Exercicio WHERE Nome LIKE ? OR Grupo_muscular LIKE ? OR Descricao LIKE ?
        """, (t, t, t)).fetchall()

        fichas = self.conn.execute("""
            SELECT a.Nome||' — '||e.Nome as principal,
                   COALESCE(f.Dia,'?')||'  |  '||COALESCE(e.Grupo_muscular,'—')||
                   '  |  '||COALESCE(f.Series,'—')||'x'||COALESCE(f.Repeticoes,'—') as detalhe
            FROM Ficha f
            JOIN Aluno a ON a.ID_Aluno=f.ID_Aluno
            JOIN Exercicio e ON e.ID_Exercicio=f.ID_Exercicio
            WHERE a.Nome LIKE ? OR e.Nome LIKE ? OR f.Dia LIKE ? OR e.Grupo_muscular LIKE ?
        """, (t, t, t, t)).fetchall()

        return {
            "Alunos":      [dict(r) for r in alunos],
            "Professores": [dict(r) for r in professores],
            "Planos":      [dict(r) for r in planos],
            "Matriculas":  [dict(r) for r in matriculas],
            "Exercicios":  [dict(r) for r in exercicios],
            "Fichas":      [dict(r) for r in fichas],
        }

    def fechar(self):
        self.conn.close()
