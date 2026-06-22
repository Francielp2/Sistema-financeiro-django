# Status Atual do Projeto

Atualizado em: 22/06/2026

## 1. Visão Geral

O projeto é um sistema de controle financeiro pessoal desenvolvido em Django. O app principal é `financeiro`.

A base financeira principal já está implementada: o sistema possui contas, categorias, movimentações, dashboard inicial, resumos financeiros, autenticação de usuários e isolamento dos dados por usuário autenticado.

O sistema foi projetado para funcionar sem inteligência artificial. A IA continua planejada como módulo futuro e complementar: ela deverá interpretar linguagem natural e gerar dados estruturados em JSON para o backend validar. A IA não deverá salvar diretamente no banco de dados.

---

## 2. Regras Principais

### Contas

* Toda movimentação financeira ocorre através de contas.
* Contas representam bancos, dinheiro físico, carteiras digitais, investimentos ou caixinhas.
* Caixinhas são contas independentes, não categorias.
* O saldo inicial é informado na criação da conta.
* O saldo atual não é editado manualmente.
* O saldo atual é calculado automaticamente pelas movimentações.
* O saldo inicial fica bloqueado para edição quando a conta já possui movimentações.

### Categorias

* Categorias classificam entradas e saídas.
* Categorias podem ser ativadas ou desativadas.
* Categorias inativas não aparecem nos formulários de criação de movimentações.
* Novos usuários recebem categorias padrão copiadas para sua própria conta.
* Categorias padrão não são globais nem compartilhadas entre usuários.
* Usuários antigos não recebem categorias padrão automaticamente.

### Movimentações

* Entradas representam receitas.
* Saídas representam despesas e transferências para terceiros.
* Transferências internas representam movimentações entre contas próprias.
* Transferências internas não alteram o patrimônio geral.
* Transferências internas não devem possuir categoria.
* Saídas e transferências internas são bloqueadas quando a conta de origem não possui saldo suficiente.
* Validações financeiras principais ficam no backend/model.

### Patrimônio e Resultado

* Patrimônio total é a soma dos saldos atuais das contas do usuário.
* Patrimônio é acumulado e não sofre influência dos filtros dos relatórios.
* Resultado do período é calculado por entradas menos saídas dentro do período filtrado.
* Transferências internas aparecem separadamente, mas não entram no resultado geral.
* Filtros afetam relatórios e listagens, mas não alteram o patrimônio real acumulado.

---

## 3. Funcionalidades Implementadas

### Estrutura Base

* Projeto Django criado.
* App `financeiro` criado.
* Configuração principal organizada em `config`.
* Templates configurados.
* Arquivos estáticos configurados.
* Bootstrap integrado via CDN.
* Tema dark/verde iniciado.
* Navbar global criada.
* Template base criado.
* Projeto versionado no GitHub.

### Modelos e Validações

* Models principais definidos: `Conta`, `Categoria` e `Movimentacao`.
* Relacionamentos com o usuário padrão do Django implementados.
* Validações financeiras centralizadas no model `Movimentacao`.
* `clean()` implementado para regras de movimentação.
* `save()` usando `full_clean()` antes de persistir.
* Preenchimento automático de data e hora quando não informadas.
* Validação de valor maior que zero.
* Validação de saldo insuficiente para saídas e transferências.
* Validação impedindo categoria em transferências internas.
* Ordenação padrão das movimentações da mais recente para a mais antiga.

### Contas

* CRUD completo de contas.
* Página de detalhes da conta.
* Listagem com saldo atual calculado.
* Bloqueio de alteração do saldo inicial após movimentações.
* Cálculo automático do saldo atual considerando:
  * saldo inicial;
  * entradas recebidas;
  * saídas enviadas;
  * transferências recebidas;
  * transferências enviadas.
* Filtros na listagem por nome, tipo e status ativa/inativa.

### Categorias

* CRUD completo de categorias.
* Página de detalhes da categoria.
* Controle de categorias ativas e inativas.
* Filtro na listagem por nome e status ativa/inativa.
* Categorias padrão criadas automaticamente para novos usuários:
  * Salário;
  * Alimentação;
  * Transporte;
  * Moradia;
  * Saúde;
  * Educação;
  * Lazer;
  * Outros.

### Movimentações

* CRUD completo de movimentações.
* Suporte a entradas, saídas e transferências internas.
* Página de detalhes da movimentação.
* Registro de data e hora.
* Controle de criação e atualização.
* Listagem ordenada da movimentação mais recente para a mais antiga.
* Tabela com data, hora, tipo, descrição, categoria, contas, valor e ações.
* Filtros avançados por:
  * data inicial;
  * data final;
  * tipo;
  * categoria;
  * sem categoria;
  * conta de origem;
  * conta de destino;
  * descrição.

### Dashboard Inicial

* Página inicial transformada em dashboard financeiro.
* Dashboard usa o mês atual como referência.
* Cards financeiros implementados:
  * patrimônio total;
  * entradas do mês;
  * saídas do mês;
  * resultado do mês;
  * transferências internas do mês.
* Atalhos rápidos para criação e navegação.
* Listagem de contas cadastradas.
* Listagem de movimentações recentes.
* Área reservada para gráficos futuros.

### Resumos Financeiros

#### Resumo Financeiro Geral

* Patrimônio total.
* Entradas do período.
* Saídas do período.
* Transferências internas do período.
* Resultado do período.
* Resumo financeiro por conta dentro do relatório geral.
* Período padrão baseado no mês atual.
* Patrimônio isolado dos filtros.

#### Resumo Individual por Conta

* Saldo atual da conta.
* Entradas da conta.
* Saídas da conta.
* Transferências recebidas.
* Transferências enviadas.
* Resultado da conta no período.
* Movimentações filtradas da conta.
* Período padrão baseado no mês atual.
* Saldo atual isolado dos filtros.

### Filtros dos Relatórios

* Filtros por período.
* Filtros por múltiplos tipos.
* Filtros por múltiplas categorias.
* Opção "Sem categoria".
* Dropdowns com seleção múltipla.
* Opção "Todos".

### Usuários e Autenticação

* Cadastro de usuários usando o model `User` padrão do Django.
* Login.
* Logout.
* Página "Meu perfil".
* Edição de dados pessoais com confirmação da senha atual.
* Alteração de senha usando validações nativas do Django.
* Listagem simples de usuários restrita a administradores/staff.
* Diferenciação visual entre usuário comum e administrador.
* Django Admin preservado para manutenção.

### Isolamento por Usuário

* Views financeiras protegidas por login.
* Contas, categorias e movimentações filtradas por `request.user`.
* Detalhes, edição, exclusão e resumo individual buscam objetos pelo usuário autenticado.
* Formulários de movimentação exibem apenas contas e categorias do usuário logado.
* Administradores/staff usam o sistema comum como usuários normais e veem apenas os próprios dados.
* Superusuários continuam podendo acessar todos os dados pelo Django Admin.

### Camada de Serviços

* Arquivo `financeiro/servicos.py` iniciado.
* Cálculos financeiros comuns foram centralizados parcialmente.
* Serviços existentes incluem:
  * período do mês atual;
  * patrimônio total;
  * totais por período;
  * filtros por tipo e categoria;
  * resumo por conta;
  * resumo individual de conta;
  * movimentações recentes;
  * criação de categorias padrão.

---

## 4. Funcionalidades em Andamento

* Refinar a página de resumo individual da conta.
* Melhorar a navegação entre dashboard, resumo geral e resumo por conta.
* Separar melhor informações cadastrais da conta e relatórios financeiros.
* Continuar centralizando cálculos financeiros na camada de serviços.
* Padronizar exibição de erros nos formulários financeiros.
* Revisar casos de edição de movimentações antigas.
* Melhorar responsividade e organização visual dos templates.

---

## 5. Próximas Etapas

### Estabilidade e Regras Financeiras

* Tratar datas inválidas nos filtros dos resumos sem gerar erro 500.
* Corrigir a validação de saldo ao editar saídas e transferências existentes.
* Permitir edição de movimentações antigas que usam conta ou categoria atualmente inativa.
* Definir regra de exclusão de conta com movimentações:
  * bloquear exclusão;
  * inativar conta;
  * ou manter exclusão em cascata.
* Definir política de exclusão/inativação de usuários e retenção dos dados financeiros.

### Interface e Navegação

* Implementar dashboard individual por conta.
* Melhorar navegação entre dashboard, resumo geral e resumo individual.
* Reorganizar templates de dashboard e relatórios.
* Implementar sidebar.
* Melhorar interface dark/verde.
* Melhorar responsividade das listagens e relatórios.

### Gráficos

Implementar com Chart.js:

* Gastos por categoria.
* Entradas por categoria.
* Distribuição do patrimônio.
* Evolução por período.
* Gráficos individuais por conta.
* Integração entre filtros e gráficos.

### Usuários e Administração

* Revisar permissões e segurança.
* Implementar funcionalidades administrativas complementares para gestão de usuários.
* Manter promoção, rebaixamento e permissões detalhadas no Django Admin enquanto não houver tela própria completa.

### Testes

* Criar testes automatizados para:
  * cálculo de saldo atual;
  * entradas, saídas e transferências;
  * bloqueio de saldo insuficiente;
  * edição de movimentações;
  * filtros dos relatórios;
  * isolamento de dados por usuário;
  * formulários com dados inválidos;
  * categorias padrão para novos usuários.
* Continuar executando `python3 manage.py check`.
* Executar `python3 manage.py test` após criação dos testes.

### Banco de Dados e Deploy

* Manter SQLite durante desenvolvimento local.
* Planejar migração para PostgreSQL no final do desenvolvimento.
* Testar regras financeiras e relatórios no PostgreSQL.
* Preparar configuração de produção.
* Configurar variáveis de ambiente.
* Configurar arquivos estáticos para produção.
* Publicar a aplicação.

---

## 6. Decisões Técnicas Importantes

* O model de usuário continua sendo o `User` padrão do Django.
* Não há model customizado de usuário neste momento.
* Cada usuário possui seus próprios dados financeiros.
* Categorias padrão são copiadas para novos usuários e podem ser editadas, excluídas ou desativadas.
* O sistema comum isola dados por usuário, inclusive para staff e superusuários.
* O Django Admin continua separado para manutenção e pode visualizar todos os registros.
* A lógica financeira principal permanece no backend.
* O saldo atual é uma propriedade calculada, não um campo editável manualmente.
* O dashboard é uma visão rápida do mês atual.
* O resumo financeiro é a área analítica com filtros.
* Transferências internas não alteram patrimônio geral nem resultado geral.

---

## 7. IA Futura

A inteligência artificial será implementada por último, após estabilização do sistema financeiro.

Planejado:

* Criar estrutura isolada para IA.
* Implementar chat financeiro.
* Interpretar mensagens em linguagem natural.
* Gerar JSON estruturado.
* Validar todo dado gerado no backend.
* Exigir confirmação do usuário antes de salvar.

Restrições:

* A IA não terá acesso direto ao banco de dados.
* A IA não poderá salvar movimentações diretamente.
* Todo salvamento continuará passando pelas validações do sistema.
* O sistema financeiro deve continuar funcionando sem IA.

---

## 8. Estado Atual do Projeto

O projeto está em fase de estabilização e refinamento.

A base financeira, autenticação, dashboard, resumos, filtros e isolamento por usuário já estão implementados. O foco atual deve ser corrigir pontos de estabilidade, padronizar formulários, ampliar testes e melhorar a experiência visual antes de avançar para gráficos, deploy, PostgreSQL e IA.

Pontos de atenção detalhados ficam no arquivo local `docs/PROBLEMAS_PARA_RESOLVER.md`, que não faz parte do repositório remoto.
