# Status Atual do Projeto

## Visão Geral

O projeto consiste em um sistema de controle financeiro pessoal desenvolvido em Django.

A aplicação foi planejada para funcionar completamente sem IA. A inteligência artificial será implementada futuramente como um módulo complementar responsável apenas por interpretar linguagem natural e gerar dados estruturados para o backend validar.

Toda a lógica financeira permanece centralizada no backend, garantindo consistência, segurança e independência da IA.

---

# Regras de Negócio Definidas

## Contas

* Toda movimentação financeira ocorre através de contas.
* O saldo atual nunca é editado manualmente.
* O saldo atual é calculado automaticamente pelas movimentações.
* Contas podem representar bancos, dinheiro físico, carteiras digitais ou caixinhas.

## Caixinhas

* Caixinhas são tratadas como contas independentes.
* Não são categorias.
* Participam normalmente dos cálculos de patrimônio.

## Categorias

* Categorias são utilizadas para classificação financeira.
* Categorias podem ser ativadas ou desativadas.
* Categorias inativas não aparecem nos formulários.

## Entradas

* Representam receitas.
* Podem possuir categoria.

## Saídas

* Representam despesas.
* Podem possuir categoria.

## Transferências Internas

* Representam movimentações entre contas próprias.
* Não alteram o patrimônio total.
* Não devem possuir categoria.
* Possuem validação específica no backend.

## Patrimônio

* Patrimônio representa a soma dos saldos atuais de todas as contas.
* Não sofre influência dos filtros dos relatórios.

## Resultado do Período

* Calculado com base nas movimentações do período filtrado.
* Pode ser positivo ou negativo.
* Não altera o patrimônio acumulado.

---

# Funcionalidades Implementadas

## Estrutura Base

* Projeto Django criado.
* App financeiro criado.
* Templates configurados.
* Static configurado.
* Bootstrap integrado.
* Tema dark iniciado.
* Navbar global criada.
* Template base criado.
* Projeto versionado no GitHub.

## Modelos e Validações

* Models principais definidos.
* Relacionamentos implementados.
* Validações centralizadas nos models.
* clean() implementado.
* save() utilizando full_clean().
* Validação de saldo insuficiente implementada.
* Validação impedindo categoria em transferências internas implementada.

## Contas

* CRUD completo.
* Página de detalhes.
* Bloqueio de alteração do saldo inicial após movimentações.
* Cálculo automático do saldo atual.

## Categorias

* CRUD completo.
* Controle de categorias ativas e inativas.

## Movimentações

* CRUD completo.
* Entradas.
* Saídas.
* Transferências internas.
* Data e hora registradas.
* Controle de criação e atualização.
* Ordenação da mais recente para a mais antiga.
* Mensagens de erro nos formulários.

---

# Relatórios Implementados

## Resumo Financeiro Geral

Implementado com:

* Patrimônio total.
* Entradas do período.
* Saídas do período.
* Transferências internas.
* Resultado do período.

## Resumo Financeiro por Conta

Implementado com:

* Saldo atual da conta.
* Entradas da conta.
* Saídas da conta.
* Transferências recebidas.
* Transferências enviadas.
* Resultado da conta.

---

# Sistema de Filtros Implementado

## Resumo Financeiro Geral

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

## Resumo Financeiro por Conta

Filtros por:

* Período.
* Múltiplos tipos.
* Múltiplas categorias.
* Sem categoria.

Recursos:

* Cards adaptativos.
* Resultado contextualizado conforme filtros.
* Movimentações filtradas.

## Listagem de Contas

Filtros implementados:

* Nome.
* Tipo.
* Status ativa/inativa.

## Listagem de Categorias

Filtros implementados:

* Nome.
* Status ativa/inativa.

---

# Etapa Atual

Atualmente o projeto encontra-se na fase de refinamento das telas administrativas.

Próxima implementação:

* Filtros da listagem de movimentações.
* Melhoria da tabela de movimentações.
* Revisão geral dos filtros.

---

# Próximas Etapas

## Testes

* Recriar banco de dados.
* Inserir dados de teste controlados.
* Executar testes completos.
* Validar todas as regras financeiras.

## Dashboard Geral

Implementar:

* Patrimônio total.
* Entradas.
* Saídas.
* Resultado.
* Contas cadastradas.
* Movimentações recentes.

## Dashboard por Conta

Implementar:

* Resumo individual.
* Navegação integrada.
* Indicadores específicos por conta.

## Gráficos

Implementar com Chart.js:

* Gastos por categoria.
* Entradas por categoria.
* Distribuição do patrimônio.
* Evolução por período.
* Gráficos individuais por conta.

## Melhorias de Interface

* Refinamento visual.
* Melhor responsividade.
* Melhor organização dos componentes.

## Autenticação

Implementar:

* Cadastro.
* Login.
* Logout.
* Separação completa dos dados por usuário.

## Banco de Dados

* Migração de SQLite para PostgreSQL.
* Testes completos em PostgreSQL.

## Deploy

* Configuração de ambiente.
* Variáveis de ambiente.
* Publicação da aplicação.

## Inteligência Artificial

Implementar após conclusão do sistema financeiro:

* Chat financeiro.
* Interpretação de linguagem natural.
* Geração de JSON estruturado.
* Validação obrigatória pelo backend.
* Confirmação antes do salvamento.

A IA nunca terá acesso direto ao banco de dados.
Todo salvamento continuará passando pelas mesmas validações do sistema.
