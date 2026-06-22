# Status Atual do Projeto

Atualizado em: 22/06/2026

## Visão Geral

O projeto é um sistema de controle financeiro pessoal desenvolvido em Django.

A aplicação está sendo construída para funcionar de forma independente, sem depender de inteligência artificial. A IA continua planejada como módulo futuro e complementar, responsável apenas por interpretar linguagem natural e gerar dados estruturados para o backend validar.

Toda a lógica financeira permanece centralizada no backend, garantindo consistência, segurança e independência da IA.

---

## Regras de Negócio Definidas

### Contas

* Toda movimentação financeira ocorre através de contas.
* Contas representam bancos, dinheiro físico, carteiras digitais, investimentos ou caixinhas.
* O saldo inicial é informado na criação da conta.
* O saldo atual não é editado manualmente.
* O saldo atual é calculado automaticamente pelas movimentações.
* O saldo inicial fica bloqueado para edição quando a conta já possui movimentações.

### Caixinhas

* Caixinhas são tratadas como contas independentes.
* Não são categorias.
* Participam normalmente dos cálculos de patrimônio.

### Categorias

* Categorias são utilizadas para classificação financeira.
* Categorias podem ser ativadas ou desativadas.
* Categorias inativas não aparecem nos formulários de criação de movimentações.

### Entradas

* Representam receitas.
* Exigem conta de destino.
* Não devem possuir conta de origem.
* Podem possuir categoria.

### Saídas

* Representam despesas.
* Exigem conta de origem.
* Não devem possuir conta de destino.
* Podem possuir categoria.
* São bloqueadas quando a conta de origem não possui saldo suficiente.

### Transferências Internas

* Representam movimentações entre contas próprias.
* Exigem conta de origem e conta de destino.
* A conta de origem e a conta de destino não podem ser iguais.
* Não alteram o patrimônio total.
* Não devem possuir categoria.
* São bloqueadas quando a conta de origem não possui saldo suficiente.

### Patrimônio

* Patrimônio representa a soma dos saldos atuais de todas as contas.
* Não sofre influência dos filtros dos relatórios.

### Resultado do Período

* Calculado com base nas entradas e saídas do período filtrado.
* Pode ser positivo ou negativo.
* Não altera o patrimônio acumulado.

---

## Funcionalidades Implementadas

### Estrutura Base

* Projeto Django criado.
* App `financeiro` criado.
* Configuração principal do Django organizada em `config`.
* Templates configurados.
* Arquivos estáticos configurados.
* Bootstrap integrado via CDN.
* Tema dark iniciado.
* Navbar global criada.
* Template base criado.
* Projeto versionado no GitHub.

### Modelos e Validações

* Models principais definidos: `Conta`, `Categoria` e `Movimentacao`.
* Relacionamentos entre usuário, contas, categorias e movimentações implementados.
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

### Movimentações

* CRUD completo de movimentações.
* Suporte a entradas, saídas e transferências internas.
* Página de detalhes da movimentação.
* Registro de data e hora.
* Controle de criação e atualização.
* Mensagens de erro gerais no formulário de movimentação.
* Listagem ordenada da movimentação mais recente para a mais antiga.
* Tabela com data, hora, tipo, descrição, categoria, contas, valor e ações.
* Filtros implementados por:
  * data inicial;
  * data final;
  * tipo;
  * categoria;
  * sem categoria;
  * conta de origem;
  * conta de destino;
  * descrição.

---

## Relatórios Implementados

### Resumo Financeiro Geral

Implementado com:

* Patrimônio total.
* Entradas do período.
* Saídas do período.
* Transferências internas do período.
* Resultado do período.
* Resumo financeiro por conta dentro do relatório geral.
* Período padrão baseado no mês atual.
* Patrimônio isolado dos filtros.

### Resumo Financeiro por Conta

Implementado com:

* Saldo atual da conta.
* Entradas da conta.
* Saídas da conta.
* Transferências recebidas.
* Transferências enviadas.
* Resultado da conta no período.
* Movimentações filtradas da conta.
* Período padrão baseado no mês atual.
* Saldo atual isolado dos filtros.

---

## Sistema de Filtros Implementado

### Resumo Financeiro Geral

Filtros por:

* Período.
* Múltiplos tipos.
* Múltiplas categorias.
* Sem categoria.

Recursos:

* Dropdowns avançados.
* Seleção múltipla.
* Opção "Todos".
* Opção "Sem categoria".
* Patrimônio isolado dos filtros.

### Resumo Financeiro por Conta

Filtros por:

* Período.
* Múltiplos tipos.
* Múltiplas categorias.
* Sem categoria.

Recursos:

* Cards adaptativos.
* Resultado contextualizado conforme filtros.
* Movimentações filtradas.
* Saldo atual da conta isolado dos filtros.

### Listagem de Movimentações

Filtros por:

* Período.
* Tipo.
* Categoria.
* Sem categoria.
* Conta de origem.
* Conta de destino.
* Descrição.

### Listagem de Contas

Filtros por:

* Nome.
* Tipo.
* Status ativa/inativa.

### Listagem de Categorias

Filtros por:

* Nome.
* Status ativa/inativa.

---

## Etapa Atual

O projeto está na fase de estabilização das regras financeiras, revisão de segurança multiusuário e refinamento das telas administrativas.

Os cadastros principais, relatórios e filtros já existem. O foco agora deve ser transformar o protótipo funcional em uma base mais segura e validada, antes de avançar para dashboards, gráficos, deploy ou inteligência artificial.

---

## Pontos de Atenção Atuais

Os pontos abaixo estão detalhados em `docs/ERROS_ATUAIS.md` e devem ser tratados antes de novas funcionalidades maiores:

* Views de criação ainda permitem tentativa de POST sem login, causando erro 500.
* Consultas ainda não isolam os dados por `request.user`, o que mistura dados entre usuários.
* Datas inválidas nos filtros dos resumos podem gerar erro 500.
* Validação de saldo pode bloquear edições válidas de movimentações existentes.
* Templates de formulários ainda não exibem todos os erros de campo.
* Edição de movimentação pode falhar quando conta ou categoria usada foi inativada.
* Lista vazia de contas possui HTML inválido no bloco `{% empty %}`.
* Exclusão de conta usa `CASCADE` e pode apagar movimentações relacionadas.
* Não há testes automatizados implementados.

---

## Próximos Passos Recomendados

### 1. Segurança e Autenticação

* Implementar login obrigatório nas views financeiras.
* Adicionar cadastro, login e logout.
* Filtrar listagens, detalhes, edições, exclusões e relatórios por usuário autenticado.
* Ajustar formulários para exibir apenas contas e categorias do usuário correto.
* Validar que um usuário não consegue acessar dados de outro por URL direta.

### 2. Correções de Estabilidade

* Tratar datas inválidas nos filtros dos resumos sem gerar erro 500.
* Corrigir a validação de saldo ao editar saídas e transferências existentes.
* Exibir erros de campo nos formulários de conta, categoria e movimentação.
* Permitir edição de movimentações antigas que usam conta ou categoria atualmente inativa.
* Corrigir o HTML da tabela vazia de contas.
* Definir regra de exclusão de conta com movimentações: bloquear exclusão, inativar conta ou manter exclusão em cascata.

### 3. Testes

* Recriar banco de dados de desenvolvimento, se necessário.
* Inserir dados de teste controlados.
* Criar testes automatizados para:
  * cálculo de saldo atual;
  * entradas, saídas e transferências;
  * bloqueio de saldo insuficiente;
  * edição de movimentações;
  * filtros dos relatórios;
  * isolamento de dados por usuário;
  * respostas sem erro 500 para entradas inválidas.
* Executar `python3 manage.py check` e `python3 manage.py test` como rotina.

### 4. Melhorias de Interface

* Revisar tabelas e botões das telas administrativas.
* Melhorar responsividade das listagens.
* Padronizar exibição de erros de formulário.
* Melhorar a página inicial para funcionar como dashboard ou ponto de navegação útil.
* Revisar organização visual dos cards de resumo.

### 5. Dashboard Geral

Implementar após estabilização:

* Patrimônio total.
* Entradas.
* Saídas.
* Resultado.
* Contas cadastradas.
* Movimentações recentes.
* Atalhos para criação de conta, categoria e movimentação.

### 6. Dashboard por Conta

Implementar ou ampliar:

* Resumo individual.
* Navegação integrada a partir da listagem e do resumo geral.
* Indicadores específicos por conta.
* Últimas movimentações da conta.

### 7. Gráficos

Implementar com Chart.js:

* Gastos por categoria.
* Entradas por categoria.
* Distribuição do patrimônio.
* Evolução por período.
* Gráficos individuais por conta.

### 8. Banco de Dados

* Manter SQLite durante desenvolvimento local.
* Planejar migração para PostgreSQL antes do deploy.
* Testar regras financeiras e relatórios no PostgreSQL.

### 9. Deploy

* Configurar variáveis de ambiente.
* Separar configurações de desenvolvimento e produção.
* Configurar arquivos estáticos para produção.
* Publicar a aplicação.

### 10. Inteligência Artificial

Implementar somente após conclusão e estabilização do sistema financeiro:

* Chat financeiro.
* Interpretação de linguagem natural.
* Geração de JSON estruturado.
* Validação obrigatória pelo backend.
* Confirmação antes do salvamento.

A IA nunca terá acesso direto ao banco de dados. Todo salvamento continuará passando pelas mesmas validações do sistema.
