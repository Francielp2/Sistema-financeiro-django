# Erros e pontos anormais atuais

Arquivo criado para acompanhar os problemas encontrados na analise do projeto em desenvolvimento.

## Verificacao executada

- `python3 manage.py check`: sem erros.
- `python3 manage.py test`: nenhum teste executado.
- GET das paginas principais com `localhost`: retornaram 200.
- POST anonimo em criacao de conta/categoria: confirmou erro 500.
- Filtro de resumo com data invalida: confirmou erro 500.

## Problemas principais

### 1. Criacao sem login gera erro 500

Arquivos:
- `financeiro/views.py:28`
- `financeiro/views.py:97`
- `financeiro/views.py:165`

As views atribuem `request.user` aos campos `usuario`, mas nao exigem autenticacao. Se o usuario estiver anonimo, o Django tenta salvar `AnonymousUser` em uma `ForeignKey(User)` e gera erro.

Validar depois:
- Adicionar protecao de login ou outra regra clara de usuario.
- Confirmar que POST anonimo nao retorna mais 500.

### 2. Dados de usuarios diferentes ficam misturados

Arquivos:
- `financeiro/views.py:19`
- `financeiro/views.py:38`
- `financeiro/views.py:65`
- `financeiro/views.py:75`
- `financeiro/views.py:85`
- `financeiro/views.py:109`
- `financeiro/views.py:117`
- `financeiro/views.py:134`
- `financeiro/views.py:148`
- `financeiro/views.py:177`
- `financeiro/views.py:185`
- `financeiro/views.py:202`
- `financeiro/views.py:267`
- `financeiro/views.py:330`

As consultas usam `.objects.all()` ou buscam por `id` sem filtrar por `usuario=request.user`. Em um sistema multiusuario, um usuario pode ver, editar ou excluir dados de outro.

Validar depois:
- Listagens devem filtrar por usuario.
- Detalhe, edicao, exclusao e resumo por conta devem buscar apenas objetos do usuario autenticado.
- Formularios de movimentacao devem listar apenas contas/categorias do usuario correto.

### 3. Filtro com data invalida gera erro 500

Arquivos:
- `financeiro/views.py:222`
- `financeiro/views.py:223`
- `financeiro/views.py:338`
- `financeiro/views.py:339`

As views usam `datetime.strptime()` direto nos parametros `data_inicio` e `data_fim`. Se a URL receber uma data fora do formato esperado, ocorre `ValueError`.

Exemplo confirmado:
- `/resumo/?data_inicio=x&data_fim=2026-06-30`

Validar depois:
- Datas invalidas devem voltar para o periodo padrao ou mostrar erro controlado.
- A resposta nao deve ser 500.

### 4. Validacao de saldo pode falhar ao editar movimentacao

Arquivos:
- `financeiro/models.py:149`
- `financeiro/models.py:155`

Ao editar uma saida ou transferencia existente, `conta_origem.saldo_atual` ja considera a movimentacao antiga. Isso pode bloquear uma edicao que seria valida se o saldo anterior da propria movimentacao fosse desconsiderado no calculo.

Validar depois:
- Criacao continua bloqueando saldo insuficiente.
- Edicao considera corretamente o impacto anterior da movimentacao editada.

### 5. Templates nao exibem todos os erros dos formularios

Arquivos:
- `financeiro/templates/financeiro/contas/form_conta.html`
- `financeiro/templates/financeiro/categorias/form_categoria.html`
- `financeiro/templates/financeiro/movimentacoes/form_movimentacao.html`

Os templates de conta e categoria nao exibem erros do formulario. O template de movimentacao mostra `non_field_errors`, mas nao mostra erros especificos de campos.

Validar depois:
- Erros de campo aparecem perto do campo correspondente.
- Erros gerais continuam aparecendo.
- Usuario entende por que o formulario nao salvou.

### 6. Edicao de movimentacao pode falhar com conta/categoria inativa

Arquivo:
- `financeiro/forms.py:150`
- `financeiro/forms.py:152`
- `financeiro/forms.py:153`

O `MovimentacaoForm` filtra categoria, conta origem e conta destino apenas por `ativa=True`. Se uma movimentacao antiga usa uma conta ou categoria que depois foi inativada, editar essa movimentacao pode ficar invalido porque a opcao atual nao aparece no select.

Validar depois:
- Criacao deve listar apenas itens ativos, se essa for a regra.
- Edicao deve manter a opcao atual mesmo se ela estiver inativa.

### 7. HTML invalido na lista vazia de contas

Arquivo:
- `financeiro/templates/financeiro/contas/listar_contas.html:74`

No bloco `{% empty %}`, existe um `<td>` direto dentro do `<tbody>`, sem `<tr>`. Alem disso, a tabela tem 6 colunas, mas o `colspan` esta como 5.

Validar depois:
- O bloco vazio deve usar `<tr><td colspan="6">...</td></tr>`.

## Pontos de atencao

### Exclusao de conta apaga movimentacoes

Arquivo:
- `financeiro/models.py:86`
- `financeiro/models.py:94`

As chaves `conta_origem` e `conta_destino` usam `on_delete=models.CASCADE`. Ao excluir uma conta, movimentacoes relacionadas tambem sao excluidas. Isso pode ser indesejado em sistema financeiro, porque perde historico.

Validar depois:
- Decidir se a regra correta e impedir exclusao de conta com movimentacoes, inativar a conta ou manter `CASCADE`.

### Nao ha testes automatizados

Arquivo:
- `financeiro/tests.py`

O arquivo de testes esta vazio. Como o projeto tem regras financeiras, testes ajudariam a garantir saldo, transferencias, filtros e permissoes.

Validar depois:
- Adicionar testes para saldo atual, criacao/edicao de movimentacao, filtros de resumo e isolamento por usuario.
