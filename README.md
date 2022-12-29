# Bot de Aniversário

### Case do IEEE Estudantil CEFET/RJ

Processo seletivo utilizando um bot que obedece funções ligadas ao mês de aniversário.

## Como Executar o projeto?

### Pré-requisitos

Python 3.9 ou superior

### Instalação de dependências

#### Usando o poetry

Recomendo a utilização do [Poetry](https://python-poetry.org/) para gerenciar as dependências do projeto e ambiente virtual. 

Usando as dependências podem ser instaladas com o comando:

```bash
poetry install
```

Para entrar no ambiente virtual:

```bash
poetry shell
```

#### Usando o pip

Usando o [pip](https://pip.pypa.io/en/stable/getting-started/), as dependências podem ser instaladas com o comando:

```bash
pip install -r requirements.txt
```

## Criando o arquivo .env

Para executar o projeto, é necessário criar um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```bash
DISCORD_TOKEN=token_do_bot
```

### Executando o projeto

Para executar o projeto, basta executar o arquivo `app.py`:

```bash
python app.py
```
