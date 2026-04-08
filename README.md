
# Task Management API

API robusta e escalável para gestão de tarefas e utilizadores, desenvolvida com FastAPI. O projeto utiliza SQLModel para uma integração nativa entre modelos de dados e ORM, seguindo o Repository Pattern.


## 🛠 Tecnologias e Ferramentas

* **Framework:** [FastAPI](https://fastapi.tiangolo.com/).
* **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/)
* **Banco de Dados:** SQLite (Desenvolvimento) com suporte a migrações via **Alembic**.
* **Repository pattern:** [Repository pattern](https://medium.com/@kmuhsinn/the-repository-pattern-in-python-write-flexible-testable-code-with-fastapi-examples-aa0105e40776)
* **Qualidade de Código:** **Ruff** (Linter/Formatter) e **Pytest** (Testes Automatizados).
* **Gerenciamento de Dependências:** `pyproject.toml


## 🔧 Instalação e Ambiente

Este projeto utiliza o padrão moderno de configuração via `pyproject.toml`.



## 📂 Estrutura do projeto
Baseado na arquitetura implementada:

* **task_fastapi/models/:**  Definição das entidades User e Task.
* **task_fastapi/repositories/:**  Lógica de persistência (ex: get_by_id)..
* **task_fastapi/routers/:** Endpoints da API para utilizadores e tarefas.
* **task_fastapi/schemas/:** Validação de dados com Pydantic.
## 🚀 Como Executar o Projeto

Siga os passos abaixo para configurar o ambiente e rodar a aplicação localmente.

1. **Clone o repositório:**
   ```bash
    git clone [https://github.com/seu-usuario/nome-do-projeto.git](https://github.com/seu-usuario/nome-do-projeto.git)
    cd nome-do-projeto

2. **Crie e ative o ambiente virtual:**
   ```bash
      python -m venv .venv
    # Windows:
        .venv\Scripts\activate
    # Linux/Mac:
     source .venv/bin/activate

3. **Instale as deoendências**
   ```bash
     pip install -e .[dev]
    
4. **Executando a API**
   ```bash
     fastapi dev task_fastapi/app.py 
     Acesse à documentação interactiva em: http://127.0.0.1:8000/docs

5. **Testes e qualidade**
   ```bash
      # Executar testes com relatório de cobertura
     pytest --cov=task_fasta
## ✅ Funcionalidades Implementadas

### Gestão de Utilizadores

- [x] Registo: Cadastro de novos utilizadores
- [x] Verificação: Controlo de duplicidade de registos.
- [x] Consulta: Busca de utilizadores por ID (Método get_by_id).
- [x] Listagem: Recuperação de utilizadores correntes.
- [x] Edição: Modificação de dados de utilizador.

### Gestão de Tarefas

- [x] CRUD Completo: Criação, leitura, atualização e remoção de tarefas.
- [x] Relacionamento: Vínculo entre tarefas e utilizadores.

Documentação atualizada de acordo com os resultados de cobertura de 08-04-2026.

## 🔗 Redes Sociais

[![linkedin](https://img.shields.io/badge/linkedin-000?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/daniel-almeida-822332165/)

[![instagram](https://img.shields.io/badge/instagram-000?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/dhantaro/)

[![github](https://img.shields.io/badge/github-000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/danalmeidap)
