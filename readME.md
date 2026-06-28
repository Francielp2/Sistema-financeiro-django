# Sistema de Controle Financeiro Pessoal

Sistema web para gerenciamento financeiro pessoal desenvolvido com **Django**, focado no controle de contas, movimentações financeiras, relatórios gerenciais e dashboards interativos.

O projeto foi desenvolvido como parte do **Projeto de Conclusão de Curso (PCC)**, priorizando boas práticas de desenvolvimento, organização em camadas, segurança dos dados e experiência do usuário.

---

# Objetivos

O sistema tem como objetivo permitir que cada usuário controle completamente sua vida financeira por meio de:

* gerenciamento de contas financeiras;
* controle de entradas, saídas e transferências;
* categorização das movimentações;
* dashboards financeiros;
* relatórios detalhados;
* gráficos interativos;
* acompanhamento da evolução patrimonial.

Toda a aplicação foi desenvolvida para funcionar com múltiplos usuários, mantendo completo isolamento dos dados.

---

# Principais funcionalidades

## Autenticação

* Cadastro de usuários
* Login
* Logout
* Perfil do usuário
* Alteração de senha
* Proteção das páginas através de autenticação
* Separação completa dos dados por usuário

---

## Contas

* Cadastro de contas
* Edição
* Exclusão
* Controle de saldo inicial
* Bloqueio da alteração do saldo inicial quando existem movimentações
* Dashboard individual da conta
* Resumo financeiro por conta

---

## Categorias

* Cadastro
* Edição
* Exclusão
* Ativação/Inativação
* Categorias padrão criadas automaticamente para novos usuários

---

## Movimentações

* Entradas
* Saídas
* Transferências internas

Cada movimentação possui:

* data;
* hora;
* categoria;
* descrição;
* conta de origem;
* conta de destino;
* valor.

Também são realizadas diversas validações de negócio, incluindo:

* saldo insuficiente;
* regras para transferências;
* consistência das categorias.

---

## Dashboards

### Dashboard Geral

Exibe indicadores financeiros como:

* patrimônio total;
* entradas;
* saídas;
* resultado;
* transferências.

Além disso apresenta:

* últimas movimentações;
* resumo das contas;
* gráficos financeiros.

### Dashboard Individual

Cada conta possui um dashboard próprio contendo:

* indicadores financeiros;
* movimentações recentes;
* gráficos específicos da conta;
* acesso rápido ao resumo financeiro.

---

## Relatórios

O sistema possui relatórios financeiros com filtros avançados.

É possível filtrar por:

* período;
* tipo de movimentação;
* categoria;
* conta.

Os relatórios apresentam:

* patrimônio;
* entradas;
* saídas;
* transferências;
* resultado financeiro.

---

## Gráficos

Os dashboards possuem gráficos interativos desenvolvidos com Chart.js.

Atualmente o sistema apresenta:

* evolução do resultado financeiro;
* entradas x saídas;
* patrimônio por conta;
* gastos por categoria;
* entradas por categoria;
* gráficos específicos do dashboard individual.

---

# Interface

A interface foi construída utilizando o template **Mazer Admin Dashboard**, adaptado para Django.

O sistema possui:

* tema claro;
* tema escuro;
* layout responsivo;
* sidebar de navegação;
* dashboards modernos;
* tabelas padronizadas;
* formulários adaptados;
* páginas de detalhes organizadas.

---

# Tecnologias utilizadas

* Python
* Django
* SQLite (desenvolvimento)
* PostgreSQL (planejado)
* HTML5
* CSS3
* JavaScript
* Bootstrap
* Chart.js
* Mazer Admin Template

---

# Arquitetura

O projeto foi desenvolvido buscando separar responsabilidades entre:

* Models
* Views
* Forms
* Templates
* Services
* Static

Os cálculos financeiros estão sendo gradualmente centralizados em uma camada de serviços para reduzir duplicação de código e facilitar manutenção.

---

# Segurança

Entre as medidas implementadas destacam-se:

* Login obrigatório nas áreas protegidas
* Isolamento completo dos dados por usuário
* Validações de negócio
* Proteção contra acesso indevido às informações financeiras
* Validação da origem das navegações
* Preservação segura dos filtros durante a navegação

---

# Estrutura do projeto

```text
financeiro/
│
├── financeiro/
├── templates/
├── static/
├── services/
├── migrations/
├── manage.py
└── README.md
```

*A estrutura poderá sofrer reorganizações durante a fase final de desenvolvimento.*

---

# Estado atual

O sistema encontra-se com a base funcional concluída.

Atualmente estão implementados:

* CRUDs completos;
* dashboards;
* relatórios;
* gráficos;
* autenticação;
* interface responsiva;
* tema claro e escuro;
* adaptação ao template Mazer.

O projeto encontra-se na fase de:

* revisão;
* estabilização;
* reorganização interna;
* preparação para migração para PostgreSQL;
* preparação para deploy.

---

# Funcionalidades planejadas

As próximas etapas incluem:

* reorganização da arquitetura do projeto;
* migração para PostgreSQL;
* deploy da aplicação;
* configurações personalizadas do usuário;
* personalização do dashboard;
* recuperação de senha;
* integração com Inteligência Artificial para interpretação de movimentações financeiras.

---

# Instalação

Clone o repositório:

```bash
git clone https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git
```

Acesse a pasta do projeto:

```bash
cd SEU-REPOSITORIO
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual.

**Windows**

```bash
.venv\Scripts\activate
```

**Linux/macOS**

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute as migrações:

```bash
python manage.py migrate
```

Crie um superusuário:

```bash
python manage.py createsuperuser
```

Inicie o servidor:

```bash
python manage.py runserver
```

A aplicação estará disponível em:

```
http://127.0.0.1:8000/
```

---

# Primeiros passos

Após iniciar a aplicação:

1. Faça login com o usuário criado.
2. Cadastre uma ou mais contas financeiras.
3. Cadastre categorias, caso deseje utilizar categorias personalizadas.
4. Registre entradas, saídas e transferências.
5. Acompanhe os dashboards e relatórios financeiros.
6. Utilize os filtros para analisar o comportamento financeiro em diferentes períodos.

---

# Autor

Projeto desenvolvido por **Franciel Prates de Oliveira** como Projeto de Conclusão de Curso (PCC) para o curso de **Informática para Internet**.

---

# Licença

Este projeto foi desenvolvido para fins acadêmicos e de aprendizado.
