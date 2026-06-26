# Status Atual do Projeto

Atualizado em: 25/06/2026

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
* Saídas e transferências internas podem deixar o saldo da conta negativo temporariamente.
* A validação de saldo suficiente foi removida para evitar inconsistências ao lançar ou editar movimentações antigas.
* Existe pendência registrada para implementar futuramente uma validação cronológica de saldo mais correta.
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
* Chart.js integrado via CDN no dashboard.
* Tema dark/verde iniciado.
* Navbar global criada.
* Template base criado.
* Sistema global de notificações usando Django Messages.
* Projeto versionado no GitHub.

### Modelos e Validações

* Models principais definidos: `Conta`, `Categoria` e `Movimentacao`.
* Relacionamentos com o usuário padrão do Django implementados.
* Validações financeiras centralizadas no model `Movimentacao`.
* `clean()` implementado para regras de movimentação.
* `save()` usando `full_clean()` antes de persistir.
* Preenchimento automático de data e hora quando não informadas.
* Validação de valor maior que zero.
* Saídas e transferências permitem saldo negativo temporariamente.
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
* Criação de movimentação bloqueada quando o usuário não possui conta ativa.
* Aviso com atalho "Criar conta agora" quando não há conta disponível.
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
* Gráficos implementados com Chart.js:
  * entradas x saídas dos últimos seis meses;
  * evolução do resultado financeiro dos últimos seis meses;
  * gastos por categoria no mês atual;
  * entradas por categoria no mês atual;
  * patrimônio por conta.
* Patrimônio total exibido também no centro do gráfico de patrimônio.
* Dados dos gráficos enviados ao JavaScript com `json_script`.
* Gráficos sem dados são substituídos por mensagens amigáveis.
* Gráficos e indicadores respeitam o isolamento por usuário.
* A montagem dos dados do dashboard geral foi centralizada em `obter_dashboard_geral`.
* A seção de atalhos rápidos foi removida para reduzir poluição visual.
* O acesso para nova movimentação permanece disponível na área de movimentações recentes.

### Dashboard Individual da Conta

* Página própria para dashboard de uma conta específica.
* Serviço `obter_dashboard_conta` centraliza os dados da tela.
* Cards financeiros implementados:
  * saldo atual;
  * entradas do mês;
  * saídas do mês;
  * resultado do mês;
  * transferências recebidas;
  * transferências enviadas.
* Últimas movimentações da conta exibidas em tabela.
* Acesso para ver todas as movimentações relacionadas à conta.
* Acesso para detalhes cadastrais da conta.
* Acesso para resumo financeiro da conta.
* Gráficos implementados com Chart.js:
  * entradas x saídas da conta nos últimos seis meses;
  * evolução do resultado financeiro da conta nos últimos seis meses;
  * gastos por categoria da conta no mês atual;
  * transferências recebidas x enviadas nos últimos seis meses.
* Todos os dados são restritos à conta atual e ao usuário autenticado.

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
* A tabela "Resumo por Conta no Período" considera apenas o período selecionado, sem ser afetada por filtros de tipo ou categoria.
* Cards principais continuam respeitando período, tipo e categoria.
* Labels compactos indicam período, tipo e categoria filtrados.

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
* Labels compactos indicam período, tipo e categoria filtrados.

### Filtros dos Relatórios

* Filtros por período.
* Filtros por múltiplos tipos.
* Filtros por múltiplas categorias.
* Opção "Sem categoria".
* Dropdowns com seleção múltipla.
* Opção "Todos".
* Botão de limpar filtros nas telas com filtros.
* Filtro de movimentações por conta relacionada, considerando conta de origem ou destino.

### Navegação e Páginas Cadastrais

* Páginas cadastrais separadas de dashboards e resumos:
  * detalhes da conta;
  * detalhes da categoria;
  * detalhes da movimentação.
* Linhas de tabelas clicáveis para abrir detalhes em:
  * contas;
  * categorias;
  * movimentações;
  * tabelas de movimentações em dashboards e resumos.
* Colunas de ações não disparam o clique da linha.
* Parâmetro `voltar_para` implementado para preservar origem e filtros.
* Retorno validado com URL segura/local antes de ser usado.
* Botões de voltar padronizados nas páginas relevantes.
* Botão global de voltar adicionado ao template base, retornando para a última página acessada.
* Fluxo de navegação disponível pela interface:
  * Dashboard Geral;
  * Dashboard da Conta;
  * Resumo Financeiro da Conta;
  * Dados/Detalhes da Conta.

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
  * gastos por categoria;
  * entradas por categoria;
  * patrimônio por conta;
  * entradas e saídas dos últimos meses;
  * criação de categorias padrão.

### Testes Automatizados

* Suíte com 52 testes automatizados.
* Cobertura atual inclui:
  * regras e validações dos models;
  * cálculo de saldo e patrimônio;
  * entradas, saídas e transferências;
  * comportamento com saldo negativo temporariamente permitido;
  * formulários e recursos ativos por usuário;
  * serviços financeiros e dados dos gráficos;
  * CRUDs e filtros;
  * isolamento de dados por usuário;
  * autenticação, perfil e permissões administrativas;
  * categorias padrão para novos usuários;
  * bloqueio de movimentações sem conta ativa.
* `python3 manage.py check` executado sem problemas.
* `python3 manage.py test` executado com os 52 testes aprovados.

---

## 4. Funcionalidades em Andamento

* Continuar centralizando cálculos financeiros na camada de serviços.
* Padronizar exibição de erros nos formulários financeiros.
* Definir e implementar validação cronológica de saldo para movimentações antigas.
* Melhorar responsividade e organização visual dos templates.
* Validar visualmente os gráficos com diferentes quantidades de contas e categorias.

---

## 5. Próximas Etapas

### Estabilidade e Regras Financeiras

* Tratar datas inválidas nos filtros dos resumos sem gerar erro 500.
* Implementar validação cronológica de saldo ao lançar ou editar saídas e transferências.
* Permitir edição de movimentações antigas que usam conta ou categoria atualmente inativa.
* Definir regra de exclusão de conta com movimentações:
  * bloquear exclusão;
  * inativar conta;
  * ou manter exclusão em cascata.
* Definir política de exclusão/inativação de usuários e retenção dos dados financeiros.

### Interface e Navegação

* Reorganizar templates de dashboard e relatórios.
* Implementar sidebar.
* Melhorar interface dark/verde.
* Melhorar responsividade das listagens e relatórios.

### Gráficos

Os gráficos principais do dashboard geral e do dashboard individual da conta já foram implementados. Próximas possibilidades:

* Integração entre filtros e gráficos.
* Refinar comportamento de legendas quando houver muitas contas ou categorias.

### Usuários e Administração

* Revisar permissões e segurança.
* Implementar funcionalidades administrativas complementares para gestão de usuários.
* Manter promoção, rebaixamento e permissões detalhadas no Django Admin enquanto não houver tela própria completa.

### Testes

* Ampliar testes para cenários de edição de movimentações antigas.
* Adicionar testes para datas inválidas nos filtros.
* Adicionar testes para decisões futuras sobre exclusão de contas e usuários.
* Manter testes de contexto e estrutura dos gráficos.
* Continuar executando `python3 manage.py check`.
* Executar `python3 manage.py test` após cada alteração relevante.

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
* O dashboard individual da conta é uma visão rápida focada em apenas uma conta.
* O patrimônio exibido no dashboard é acumulado e não depende do mês atual.
* Os dados do dashboard são preparados no backend e enviados aos gráficos com `json_script`.
* Chart.js é usado apenas para apresentação; os cálculos permanecem no backend.
* O resumo financeiro é a área analítica com filtros.
* As páginas de detalhes são cadastrais e não devem concentrar relatórios ou dashboards.
* Transferências internas não alteram patrimônio geral nem resultado geral.
* Saldo negativo é permitido temporariamente até a criação de uma validação cronológica mais adequada.

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

O projeto está em fase de estabilização, refinamento de navegação e preparação visual.

A base financeira, autenticação, dashboard geral, dashboard individual da conta, resumos, filtros, páginas cadastrais, notificações, testes automatizados e isolamento por usuário já estão implementados. Os dados financeiros permanecem calculados no backend e enviados aos templates de forma controlada.

O foco atual deve ser implementar a validação cronológica de saldo, definir políticas de exclusão, melhorar responsividade, reduzir poluição visual antes do template definitivo e ampliar os testes para casos extremos. PostgreSQL, deploy e inteligência artificial permanecem como etapas posteriores.
