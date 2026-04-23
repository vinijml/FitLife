# FitLife — Sistema de Gestão de Academia

Sistema desktop para gerenciamento completo de academias, desenvolvido em Python com interface gráfica Tkinter e banco de dados SQLite.

## Tecnologias

- Python 3.10+
- Tkinter — interface gráfica nativa
- SQLite3 — banco de dados embutido
- Pillow — opcional, para exibir fotos dos alunos

## Como executar

```bash
# Instalar dependência opcional (fotos dos alunos)
pip install pillow

# Executar o sistema
python main.py
```

## Funcionalidades

- Cadastro de alunos com foto, CPF validado e dados completos
- Cadastro de professores e planos de assinatura
- Matrículas com cálculo automático de vencimento
- Vínculo entre professor e aluno
- Catálogo de exercícios com grupo muscular e link de vídeo
- Ficha de treino personalizada por aluno, organizada por dia da semana
- Marcação de exercícios concluídos com registro de data
- Busca global em tempo real

## Estrutura do Projeto

fitlife/
├── main.py              # Ponto de entrada
├── app.py               # Janela principal e navegação
├── database.py          # Camada de dados (SQLite)
├── tema.py              # Cores, fontes e constantes
├── widgets.py           # Componentes reutilizáveis
├── aba_busca.py         # Busca global
├── abas_basicas.py      # Professores, Alunos e Planos
├── abas_matriculas.py   # Matrículas e Acompanhamento
└── abas_treinos.py      # Exercícios e Ficha de treino
