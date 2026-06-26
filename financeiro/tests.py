from datetime import date, time
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from . import models, servicos
from .forms import (
    CadastroUsuarioForm,
    ContaEditarForm,
    EditarPerfilForm,
    MovimentacaoForm,
)
from .usuarios_views import usuario_e_administrador


class FinanceiroTestMixin:
    senha = 'SenhaForte123!'

    def criar_dados_basicos(self):
        self.usuario = User.objects.create_user(
            username='usuario',
            password=self.senha,
            first_name='Usuário'
        )
        self.outro_usuario = User.objects.create_user(
            username='outro',
            password=self.senha
        )
        self.conta = models.Conta.objects.create(
            usuario=self.usuario,
            nome='Conta principal',
            tipo='corrente',
            saldo_inicial=Decimal('1000.00')
        )
        self.conta_destino = models.Conta.objects.create(
            usuario=self.usuario,
            nome='Reserva',
            tipo='investimento',
            saldo_inicial=Decimal('500.00')
        )
        self.outra_conta = models.Conta.objects.create(
            usuario=self.outro_usuario,
            nome='Conta de outro usuário',
            tipo='corrente',
            saldo_inicial=Decimal('5000.00')
        )
        self.categoria = models.Categoria.objects.create(
            usuario=self.usuario,
            nome='Alimentação'
        )
        self.outra_categoria = models.Categoria.objects.create(
            usuario=self.outro_usuario,
            nome='Categoria de outro usuário'
        )

    def criar_movimentacao(
        self,
        tipo='entrada',
        valor='100.00',
        usuario=None,
        conta_origem=None,
        conta_destino=None,
        categoria=None,
        data_movimentacao=date(2026, 1, 10),
        descricao=None
    ):
        usuario = usuario or self.usuario

        if tipo == 'entrada':
            conta_destino = conta_destino or self.conta
        elif tipo == 'saida':
            conta_origem = conta_origem or self.conta
        elif tipo == 'transferencia':
            conta_origem = conta_origem or self.conta
            conta_destino = conta_destino or self.conta_destino

        return models.Movimentacao.objects.create(
            usuario=usuario,
            descricao=descricao or f'Movimentação {tipo}',
            valor=Decimal(valor),
            tipo=tipo,
            categoria=categoria,
            conta_origem=conta_origem,
            conta_destino=conta_destino,
            data=data_movimentacao,
            hora=time(10, 0)
        )


class ModelsTestCase(FinanceiroTestMixin, TestCase):
    def setUp(self):
        self.criar_dados_basicos()

    def test_representacoes_textuais(self):
        movimentacao = self.criar_movimentacao(valor='150.00')

        self.assertEqual(str(self.conta), 'Conta principal')
        self.assertEqual(str(self.categoria), 'Alimentação')
        self.assertEqual(
            str(movimentacao),
            'Movimentação entrada - R$ 150.00'
        )

    def test_saldo_atual_considera_todos_os_tipos(self):
        self.criar_movimentacao('entrada', '300.00')
        self.criar_movimentacao('saida', '100.00')
        self.criar_movimentacao('transferencia', '200.00')
        self.criar_movimentacao(
            'transferencia',
            '50.00',
            conta_origem=self.conta_destino,
            conta_destino=self.conta
        )

        self.assertEqual(self.conta.saldo_atual, Decimal('1050.00'))
        self.assertEqual(self.conta_destino.saldo_atual, Decimal('650.00'))

    @patch('financeiro.models.timezone.localtime')
    def test_save_preenche_data_e_hora_automaticamente(self, localtime_mock):
        from datetime import datetime

        localtime_mock.return_value = datetime(2026, 4, 5, 14, 30)
        movimentacao = models.Movimentacao.objects.create(
            usuario=self.usuario,
            descricao='Entrada automática',
            valor=Decimal('100.00'),
            tipo='entrada',
            conta_destino=self.conta
        )

        self.assertEqual(movimentacao.data, date(2026, 4, 5))
        self.assertEqual(movimentacao.hora.hour, 14)
        self.assertEqual(movimentacao.hora.minute, 30)

    def test_valor_deve_ser_maior_que_zero(self):
        movimentacao = models.Movimentacao(
            usuario=self.usuario,
            descricao='Inválida',
            valor=Decimal('0.00'),
            tipo='entrada',
            conta_destino=self.conta
        )

        with self.assertRaisesMessage(
            ValidationError,
            'O valor da movimentação deve ser maior que zero.'
        ):
            movimentacao.full_clean()

    def test_data_informada_exige_hora(self):
        movimentacao = models.Movimentacao(
            usuario=self.usuario,
            descricao='Sem hora',
            valor=Decimal('10.00'),
            tipo='entrada',
            conta_destino=self.conta,
            data=date(2026, 1, 1)
        )

        with self.assertRaisesMessage(
            ValidationError,
            'Ao informar uma data, a hora da movimentação também deve ser informada.'
        ):
            movimentacao.full_clean()

    def test_entrada_exige_destino_e_proibe_origem(self):
        sem_destino = models.Movimentacao(
            usuario=self.usuario,
            descricao='Entrada',
            valor=Decimal('10.00'),
            tipo='entrada'
        )
        com_origem = models.Movimentacao(
            usuario=self.usuario,
            descricao='Entrada',
            valor=Decimal('10.00'),
            tipo='entrada',
            conta_origem=self.conta,
            conta_destino=self.conta_destino
        )

        with self.assertRaisesMessage(
            ValidationError,
            'Entradas precisam de uma conta de destino.'
        ):
            sem_destino.full_clean()
        with self.assertRaisesMessage(
            ValidationError,
            'Entradas não devem ter conta de origem.'
        ):
            com_origem.full_clean()

    def test_saida_exige_origem_proibe_destino_e_permite_saldo_negativo(self):
        sem_origem = models.Movimentacao(
            usuario=self.usuario,
            descricao='Saída',
            valor=Decimal('10.00'),
            tipo='saida'
        )
        com_destino = models.Movimentacao(
            usuario=self.usuario,
            descricao='Saída',
            valor=Decimal('10.00'),
            tipo='saida',
            conta_origem=self.conta,
            conta_destino=self.conta_destino
        )
        with self.assertRaisesMessage(
            ValidationError,
            'Saídas precisam de uma conta de origem.'
        ):
            sem_origem.full_clean()
        with self.assertRaisesMessage(
            ValidationError,
            'Saídas não devem ter conta de destino.'
        ):
            com_destino.full_clean()

        self.criar_movimentacao('saida', '1200.00')

        self.assertEqual(self.conta.saldo_atual, Decimal('-200.00'))

    def test_transferencia_valida_contas_categoria_e_permite_saldo_negativo(
        self
    ):
        casos = [
            (
                models.Movimentacao(
                    usuario=self.usuario,
                    descricao='Transferência',
                    valor=Decimal('10.00'),
                    tipo='transferencia',
                    conta_origem=self.conta
                ),
                'Transferências precisam de conta de origem e destino.'
            ),
            (
                models.Movimentacao(
                    usuario=self.usuario,
                    descricao='Transferência',
                    valor=Decimal('10.00'),
                    tipo='transferencia',
                    conta_origem=self.conta,
                    conta_destino=self.conta
                ),
                'A conta de origem e destino não podem ser iguais.'
            ),
            (
                models.Movimentacao(
                    usuario=self.usuario,
                    descricao='Transferência',
                    valor=Decimal('10.00'),
                    tipo='transferencia',
                    categoria=self.categoria,
                    conta_origem=self.conta,
                    conta_destino=self.conta_destino
                ),
                'Transferências internas não devem possuir categoria.'
            ),
        ]

        for movimentacao, mensagem in casos:
            with self.subTest(mensagem=mensagem):
                with self.assertRaisesMessage(ValidationError, mensagem):
                    movimentacao.full_clean()

        transferencia = self.criar_movimentacao(
            'transferencia',
            '1200.00'
        )

        self.assertEqual(self.conta.saldo_atual, Decimal('-200.00'))
        self.assertEqual(
            transferencia.conta_destino.saldo_atual,
            Decimal('1700.00')
        )


class FormulariosTestCase(FinanceiroTestMixin, TestCase):
    def setUp(self):
        self.criar_dados_basicos()

    def test_cadastro_cria_usuario_comum(self):
        form = CadastroUsuarioForm(data={
            'username': 'novo',
            'first_name': 'Novo',
            'last_name': 'Usuário',
            'email': 'novo@example.com',
            'password1': self.senha,
            'password2': self.senha,
        })

        self.assertTrue(form.is_valid(), form.errors)
        usuario = form.save()
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
        self.assertTrue(usuario.check_password(self.senha))

    def test_editar_perfil_exige_senha_atual_correta(self):
        dados = {
            'first_name': 'Nome',
            'last_name': 'Alterado',
            'email': 'alterado@example.com',
            'senha_atual': 'incorreta',
        }
        form = EditarPerfilForm(
            data=dados,
            instance=self.usuario,
            usuario=self.usuario
        )

        self.assertFalse(form.is_valid())
        self.assertIn('senha_atual', form.errors)

        dados['senha_atual'] = self.senha
        form = EditarPerfilForm(
            data=dados,
            instance=self.usuario,
            usuario=self.usuario
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_edicao_de_conta_pode_bloquear_saldo_inicial(self):
        form = ContaEditarForm(
            instance=self.conta,
            bloquear_saldo=True
        )

        self.assertTrue(form.fields['saldo_inicial'].disabled)
        self.assertIn(
            'não pode ser alterado',
            form.fields['saldo_inicial'].help_text
        )

    def test_form_movimentacao_exibe_apenas_recursos_ativos_do_usuario(self):
        models.Conta.objects.create(
            usuario=self.usuario,
            nome='Inativa',
            tipo='corrente',
            ativa=False
        )
        models.Categoria.objects.create(
            usuario=self.usuario,
            nome='Inativa',
            ativa=False
        )

        form = MovimentacaoForm(usuario=self.usuario)

        self.assertQuerySetEqual(
            form.fields['conta_origem'].queryset.order_by('id'),
            [self.conta, self.conta_destino]
        )
        self.assertQuerySetEqual(
            form.fields['categoria'].queryset,
            [self.categoria]
        )
        self.assertNotIn(
            self.outra_conta,
            form.fields['conta_destino'].queryset
        )
        self.assertNotIn(
            self.outra_categoria,
            form.fields['categoria'].queryset
        )


class ServicosTestCase(FinanceiroTestMixin, TestCase):
    def setUp(self):
        self.criar_dados_basicos()

    def test_criar_categorias_padrao_e_idempotente(self):
        usuario = User.objects.create_user('sem_categorias')

        criadas = servicos.criar_categorias_padrao(usuario)
        segunda_execucao = servicos.criar_categorias_padrao(usuario)

        self.assertEqual(len(criadas), len(servicos.CATEGORIAS_PADRAO))
        self.assertEqual(segunda_execucao, [])
        self.assertEqual(
            models.Categoria.objects.filter(usuario=usuario).count(),
            len(servicos.CATEGORIAS_PADRAO)
        )

    @patch('financeiro.servicos.timezone.localdate')
    def test_obter_periodo_mes_atual(self, localdate_mock):
        localdate_mock.return_value = date(2024, 2, 10)

        self.assertEqual(
            servicos.obter_periodo_mes_atual(),
            (date(2024, 2, 1), date(2024, 2, 29))
        )

    def test_patrimonio_total_filtra_usuario(self):
        self.criar_movimentacao('entrada', '200.00')

        self.assertEqual(
            servicos.calcular_patrimonio_total(self.usuario),
            Decimal('1700.00')
        )

    def test_resumo_periodo_soma_tipos_e_filtra_usuario_e_datas(self):
        self.criar_movimentacao('entrada', '500.00')
        self.criar_movimentacao('saida', '100.00')
        self.criar_movimentacao('transferencia', '50.00')
        self.criar_movimentacao(
            'entrada',
            '900.00',
            usuario=self.outro_usuario,
            conta_destino=self.outra_conta
        )
        self.criar_movimentacao(
            'entrada',
            '700.00',
            data_movimentacao=date(2025, 12, 31)
        )

        resumo = servicos.calcular_resumo_periodo(
            self.usuario,
            date(2026, 1, 1),
            date(2026, 1, 31)
        )

        self.assertEqual(resumo['entradas'], Decimal('500.00'))
        self.assertEqual(resumo['saidas'], Decimal('100.00'))
        self.assertEqual(resumo['transferencias'], Decimal('50.00'))
        self.assertEqual(resumo['resultado'], Decimal('400.00'))

    def test_filtros_aceitam_tipos_categorias_e_sem_categoria_validos(self):
        outra_categoria = models.Categoria.objects.create(
            usuario=self.usuario,
            nome='Salário'
        )
        entrada_categoria = self.criar_movimentacao(
            'entrada',
            '500.00',
            categoria=outra_categoria
        )
        entrada_sem_categoria = self.criar_movimentacao('entrada', '200.00')
        self.criar_movimentacao('saida', '50.00', categoria=self.categoria)

        resumo = servicos.calcular_resumo_periodo(
            self.usuario,
            date(2026, 1, 1),
            date(2026, 1, 31),
            tipos_filtro=['entrada', 'invalido'],
            categorias_filtro=[
                str(outra_categoria.id),
                'sem_categoria',
                str(self.outra_categoria.id),
            ],
            categorias=models.Categoria.objects.filter(usuario=self.usuario)
        )

        self.assertEqual(resumo['tipos_filtro'], ['entrada'])
        self.assertEqual(
            resumo['categorias_filtro'],
            [str(outra_categoria.id), 'sem_categoria']
        )
        self.assertCountEqual(
            resumo['movimentacoes'],
            [entrada_categoria, entrada_sem_categoria]
        )

    def test_resumo_por_conta_e_resumo_individual(self):
        self.criar_movimentacao('entrada', '300.00')
        self.criar_movimentacao('saida', '100.00')
        self.criar_movimentacao('transferencia', '200.00')
        movimentacoes = models.Movimentacao.objects.all()

        por_conta = servicos.calcular_resumo_por_conta(
            self.usuario,
            models.Conta.objects.all(),
            movimentacoes
        )
        conta_principal = next(
            item for item in por_conta if item['conta'] == self.conta
        )
        resumo = servicos.calcular_resumo_conta(
            self.usuario,
            self.conta,
            date(2026, 1, 1),
            date(2026, 1, 31)
        )

        self.assertEqual(conta_principal['resultado_periodo'], Decimal('0.00'))
        self.assertEqual(resumo['entradas'], Decimal('300.00'))
        self.assertEqual(resumo['saidas'], Decimal('100.00'))
        self.assertEqual(
            resumo['transferencias_enviadas'],
            Decimal('200.00')
        )
        self.assertEqual(resumo['resultado_periodo'], Decimal('0.00'))

    def test_movimentacoes_recentes_respeita_ordem_limite_e_usuario(self):
        antiga = self.criar_movimentacao(
            descricao='Antiga',
            data_movimentacao=date(2026, 1, 1)
        )
        recente = self.criar_movimentacao(
            descricao='Recente',
            data_movimentacao=date(2026, 1, 2)
        )
        self.criar_movimentacao(
            usuario=self.outro_usuario,
            conta_destino=self.outra_conta,
            data_movimentacao=date(2026, 1, 3)
        )

        resultado = list(
            servicos.obter_movimentacoes_recentes(self.usuario, 2)
        )

        self.assertEqual(resultado, [recente, antiga])

    @patch(
        'financeiro.servicos.timezone.localdate',
        return_value=date(2026, 2, 15)
    )
    @patch('financeiro.servicos.obter_periodo_mes_atual')
    def test_dashboard_conta_reutiliza_resumo_e_isola_movimentacoes(
        self,
        periodo_mock,
        localdate_mock
    ):
        periodo_mock.return_value = (
            date(2026, 1, 1),
            date(2026, 1, 31)
        )
        entrada = self.criar_movimentacao('entrada', '300.00')
        self.criar_movimentacao('saida', '100.00')
        self.criar_movimentacao('transferencia', '200.00')
        self.criar_movimentacao(
            'transferencia',
            '50.00',
            conta_origem=self.conta_destino,
            conta_destino=self.conta
        )
        recente_fora_do_mes = self.criar_movimentacao(
            'entrada',
            '20.00',
            data_movimentacao=date(2026, 2, 1)
        )
        self.criar_movimentacao(
            'entrada',
            '900.00',
            conta_destino=self.conta_destino
        )

        dashboard = servicos.obter_dashboard_conta(
            self.usuario,
            self.conta
        )

        self.assertEqual(dashboard['conta'], self.conta)
        self.assertEqual(dashboard['saldo_inicial'], Decimal('1000.00'))
        self.assertEqual(dashboard['saldo_atual'], Decimal('1070.00'))
        self.assertEqual(dashboard['entradas_mes'], Decimal('300.00'))
        self.assertEqual(dashboard['saidas_mes'], Decimal('100.00'))
        self.assertEqual(
            dashboard['transferencias_recebidas_mes'],
            Decimal('50.00')
        )
        self.assertEqual(
            dashboard['transferencias_enviadas_mes'],
            Decimal('200.00')
        )
        self.assertEqual(dashboard['resultado_mes'], Decimal('50.00'))
        self.assertEqual(
            dashboard['dados_resultado_mensal_conta']['resultados'][-2:],
            [Decimal('200.00'), Decimal('20.00')]
        )
        self.assertEqual(
            list(dashboard['movimentacoes_recentes'])[0],
            recente_fora_do_mes
        )
        self.assertIn(
            entrada,
            dashboard['movimentacoes_recentes']
        )

    def test_dashboard_conta_rejeita_conta_de_outro_usuario(self):
        with self.assertRaises(ValueError):
            servicos.obter_dashboard_conta(
                self.usuario,
                self.outra_conta
            )

    def test_gastos_por_categoria_agrupa_ordena_e_isola_usuario(self):
        self.criar_movimentacao(
            'saida', '100.00', categoria=self.categoria
        )
        self.criar_movimentacao('saida', '50.00')
        self.criar_movimentacao('entrada', '900.00')
        self.criar_movimentacao(
            'saida',
            '800.00',
            usuario=self.outro_usuario,
            conta_origem=self.outra_conta
        )

        resultado = servicos.obter_gastos_por_categoria(
            self.usuario,
            date(2026, 1, 1),
            date(2026, 1, 31)
        )

        self.assertEqual(
            resultado,
            {
                'labels': ['Alimentação', 'Sem categoria'],
                'valores': [Decimal('100.00'), Decimal('50.00')],
            }
        )

    def test_entradas_por_categoria_inclui_sem_categoria(self):
        salario = models.Categoria.objects.create(
            usuario=self.usuario,
            nome='Salário'
        )
        self.criar_movimentacao('entrada', '1200.00', categoria=salario)
        self.criar_movimentacao('entrada', '200.00')

        resultado = servicos.obter_entradas_por_categoria(
            self.usuario,
            date(2026, 1, 1),
            date(2026, 1, 31)
        )

        self.assertEqual(
            resultado,
            {
                'labels': ['Salário', 'Sem categoria'],
                'valores': [Decimal('1200.00'), Decimal('200.00')],
            }
        )

    def test_patrimonio_por_conta_usa_saldo_atual_e_ordena(self):
        self.criar_movimentacao('entrada', '300.00')

        resultado = servicos.obter_patrimonio_por_conta(self.usuario)

        self.assertEqual(resultado['labels'], ['Conta principal', 'Reserva'])
        self.assertEqual(
            resultado['valores'],
            [Decimal('1300.00'), Decimal('500.00')]
        )

    @patch('financeiro.servicos.timezone.localdate')
    def test_entradas_saidas_meses_vazios_transicao_e_transferencias(
        self,
        localdate_mock
    ):
        localdate_mock.return_value = date(2026, 2, 15)
        self.criar_movimentacao(
            'entrada', '500.00', data_movimentacao=date(2025, 11, 10)
        )
        self.criar_movimentacao(
            'saida', '80.00', data_movimentacao=date(2026, 1, 10)
        )
        self.criar_movimentacao(
            'entrada', '300.00', data_movimentacao=date(2026, 2, 20)
        )
        self.criar_movimentacao(
            'transferencia', '100.00', data_movimentacao=date(2026, 2, 11)
        )

        resultado = servicos.obter_entradas_saidas_ultimos_meses(
            self.usuario,
            4
        )

        self.assertEqual(
            resultado,
            {
                'labels': [
                    'Nov/2025', 'Dez/2025', 'Jan/2026', 'Fev/2026'
                ],
                'entradas': [
                    Decimal('500.00'), 0, 0, Decimal('300.00')
                ],
                'saidas': [0, 0, Decimal('80.00'), 0],
            }
        )
        self.assertEqual(
            servicos.obter_entradas_saidas_ultimos_meses(self.usuario, 0),
            {'labels': [], 'entradas': [], 'saidas': []}
        )

    def test_resultado_mensal_subtrai_saidas_e_preserva_meses_zerados(self):
        resultado = servicos.calcular_resultado_mensal({
            'labels': ['Jan/2026', 'Fev/2026', 'Mar/2026'],
            'entradas': [
                Decimal('500.00'),
                Decimal('100.00'),
                0,
            ],
            'saidas': [
                Decimal('200.00'),
                Decimal('300.00'),
                0,
            ],
        })

        self.assertEqual(
            resultado,
            {
                'labels': ['Jan/2026', 'Fev/2026', 'Mar/2026'],
                'resultados': [
                    Decimal('300.00'),
                    Decimal('-200.00'),
                    0,
                ],
            }
        )

    @patch('financeiro.servicos.timezone.localdate')
    def test_entradas_saidas_conta_meses_isola_conta_e_preenche_zeros(
        self,
        localdate_mock
    ):
        localdate_mock.return_value = date(2026, 2, 15)
        self.criar_movimentacao(
            'entrada', '500.00', data_movimentacao=date(2025, 11, 10)
        )
        self.criar_movimentacao(
            'saida', '80.00', data_movimentacao=date(2026, 1, 10)
        )
        self.criar_movimentacao(
            'entrada',
            '300.00',
            conta_destino=self.conta_destino,
            data_movimentacao=date(2026, 2, 10)
        )
        self.criar_movimentacao(
            'transferencia',
            '100.00',
            data_movimentacao=date(2026, 2, 11)
        )
        self.criar_movimentacao(
            'entrada',
            '900.00',
            usuario=self.outro_usuario,
            conta_destino=self.outra_conta,
            data_movimentacao=date(2026, 2, 12)
        )

        resultado = servicos.obter_entradas_saidas_conta_ultimos_meses(
            self.usuario,
            self.conta,
            4
        )

        self.assertEqual(
            resultado,
            {
                'labels': [
                    'Nov/2025', 'Dez/2025', 'Jan/2026', 'Fev/2026'
                ],
                'entradas': [
                    Decimal('500.00'), 0, 0, 0
                ],
                'saidas': [0, 0, Decimal('80.00'), 0],
            }
        )
        self.assertEqual(
            servicos.obter_entradas_saidas_conta_ultimos_meses(
                self.usuario,
                self.conta,
                0
            ),
            {'labels': [], 'entradas': [], 'saidas': []}
        )

    def test_gastos_categoria_conta_agrupa_e_isola_conta(self):
        self.criar_movimentacao(
            'saida',
            '100.00',
            categoria=self.categoria
        )
        self.criar_movimentacao('saida', '50.00')
        self.criar_movimentacao(
            'saida',
            '200.00',
            conta_origem=self.conta_destino
        )

        resultado = servicos.obter_gastos_por_categoria_conta(
            self.usuario,
            self.conta,
            date(2026, 1, 1),
            date(2026, 1, 31)
        )

        self.assertEqual(
            resultado,
            {
                'labels': ['Alimentação', 'Sem categoria'],
                'valores': [Decimal('100.00'), Decimal('50.00')],
            }
        )

    @patch('financeiro.servicos.timezone.localdate')
    def test_transferencias_conta_meses_separa_direcoes_e_preenche_zeros(
        self,
        localdate_mock
    ):
        localdate_mock.return_value = date(2026, 2, 15)
        self.criar_movimentacao(
            'transferencia',
            '200.00',
            data_movimentacao=date(2025, 11, 10)
        )
        self.criar_movimentacao(
            'transferencia',
            '50.00',
            conta_origem=self.conta_destino,
            conta_destino=self.conta,
            data_movimentacao=date(2026, 1, 10)
        )
        self.criar_movimentacao(
            'entrada',
            '300.00',
            data_movimentacao=date(2026, 2, 10)
        )

        resultado = servicos.obter_transferencias_conta_ultimos_meses(
            self.usuario,
            self.conta,
            4
        )

        self.assertEqual(
            resultado,
            {
                'labels': [
                    'Nov/2025', 'Dez/2025', 'Jan/2026', 'Fev/2026'
                ],
                'recebidas': [0, 0, Decimal('50.00'), 0],
                'enviadas': [Decimal('200.00'), 0, 0, 0],
            }
        )
        self.assertEqual(
            servicos.obter_transferencias_conta_ultimos_meses(
                self.usuario,
                self.conta,
                0
            ),
            {'labels': [], 'recebidas': [], 'enviadas': []}
        )


class ViewsFinanceirasTestCase(FinanceiroTestMixin, TestCase):
    def setUp(self):
        self.criar_dados_basicos()

    def test_views_financeiras_exigem_login(self):
        urls = [
            reverse('inicio'),
            reverse('listar_contas'),
            reverse('criar_conta'),
            reverse('detalhes_conta', args=[self.conta.id]),
            reverse('editar_conta', args=[self.conta.id]),
            reverse('excluir_conta', args=[self.conta.id]),
            reverse('listar_categorias'),
            reverse('criar_categoria'),
            reverse('detalhes_categoria', args=[self.categoria.id]),
            reverse('editar_categoria', args=[self.categoria.id]),
            reverse('excluir_categoria', args=[self.categoria.id]),
            reverse('listar_movimentacoes'),
            reverse('criar_movimentacao'),
            reverse('resumo_financeiro'),
            reverse('resumo_conta', args=[self.conta.id]),
            reverse('dashboard_conta', args=[self.conta.id]),
        ]

        for url in urls:
            with self.subTest(url=url):
                resposta = self.client.get(url)
                self.assertRedirects(
                    resposta,
                    f"{reverse('login')}?next={url}"
                )

    def test_inicio_exibe_apenas_dados_do_usuario(self):
        self.client.force_login(self.usuario)
        movimentacao = self.criar_movimentacao('entrada', '200.00')
        self.criar_movimentacao(
            'entrada',
            '900.00',
            usuario=self.outro_usuario,
            conta_destino=self.outra_conta
        )

        with patch(
            'financeiro.servicos.obter_periodo_mes_atual',
            return_value=(date(2026, 1, 1), date(2026, 1, 31))
        ):
            resposta = self.client.get(reverse('inicio'))

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.context['patrimonio_total'],
            Decimal('1700.00')
        )
        self.assertEqual(
            resposta.context['total_entradas_mes'],
            Decimal('200.00')
        )
        self.assertIn(movimentacao, resposta.context['movimentacoes_recentes'])
        self.assertNotIn(
            self.outra_conta,
            resposta.context['contas']
        )
        self.assertEqual(
            resposta.context['dados_entradas_por_categoria'],
            {
                'labels': ['Sem categoria'],
                'valores': [Decimal('200.00')],
            }
        )
        self.assertNotIn(
            'Conta de outro usuário',
            resposta.context['dados_patrimonio_por_conta']['labels']
        )

    def test_inicio_envia_dados_dos_graficos_para_o_contexto(self):
        self.client.force_login(self.usuario)
        inicio_mes = date(2026, 1, 1)
        fim_mes = date(2026, 1, 31)
        gastos = {'labels': ['Alimentação'], 'valores': [Decimal('50.00')]}
        entradas = {'labels': ['Salário'], 'valores': [Decimal('500.00')]}
        patrimonio = {
            'labels': ['Conta principal'],
            'valores': [Decimal('1000.00')],
        }
        meses = {
            'labels': ['Jan/2026'],
            'entradas': [Decimal('500.00')],
            'saidas': [Decimal('50.00')],
        }

        with (
            patch(
                'financeiro.servicos.obter_periodo_mes_atual',
                return_value=(inicio_mes, fim_mes)
            ),
            patch(
                'financeiro.servicos.obter_gastos_por_categoria',
                return_value=gastos
            ) as gastos_mock,
            patch(
                'financeiro.servicos.obter_entradas_por_categoria',
                return_value=entradas
            ) as entradas_mock,
            patch(
                'financeiro.servicos.obter_patrimonio_por_conta',
                return_value=patrimonio
            ) as patrimonio_mock,
            patch(
                'financeiro.servicos.obter_entradas_saidas_ultimos_meses',
                return_value=meses
            ) as meses_mock,
        ):
            resposta = self.client.get(reverse('inicio'))

        gastos_mock.assert_called_once_with(
            self.usuario,
            inicio_mes,
            fim_mes
        )
        entradas_mock.assert_called_once_with(
            self.usuario,
            inicio_mes,
            fim_mes
        )
        patrimonio_mock.assert_called_once_with(self.usuario)
        meses_mock.assert_called_once_with(
            self.usuario,
            quantidade_meses=6
        )
        self.assertEqual(
            resposta.context['dados_gastos_por_categoria'],
            gastos
        )
        self.assertEqual(
            resposta.context['dados_entradas_por_categoria'],
            entradas
        )
        self.assertEqual(
            resposta.context['dados_patrimonio_por_conta'],
            patrimonio
        )
        self.assertEqual(
            resposta.context['dados_entradas_saidas_meses'],
            meses
        )
        self.assertEqual(
            resposta.context['dados_resultado_mensal'],
            {
                'labels': ['Jan/2026'],
                'resultados': [Decimal('450.00')],
            }
        )
        self.assertContains(resposta, 'id="graficoEntradasSaidas"')
        self.assertContains(resposta, 'id="graficoResultadoMensal"')
        self.assertContains(resposta, 'id="graficoGastosCategoria"')
        self.assertContains(resposta, 'id="graficoPatrimonioConta"')
        self.assertContains(resposta, 'id="totalPatrimonioConta"')
        self.assertContains(resposta, 'id="valorTotalPatrimonioConta"')
        self.assertContains(resposta, 'id="graficoEntradasCategoria"')
        self.assertContains(
            resposta,
            'id="dados-entradas-saidas-meses"'
        )
        self.assertContains(
            resposta,
            'id="dados-resultado-mensal"'
        )
        self.assertContains(
            resposta,
            'id="dados-gastos-por-categoria"'
        )
        self.assertContains(
            resposta,
            'id="dados-patrimonio-por-conta"'
        )
        self.assertContains(
            resposta,
            'id="dados-entradas-por-categoria"'
        )
        self.assertContains(
            resposta,
            'Nenhum gasto encontrado no mês atual.'
        )
        self.assertContains(
            resposta,
            'Nenhum patrimônio disponível para exibir.'
        )
        self.assertContains(
            resposta,
            'Nenhuma entrada encontrada no mês atual.'
        )

    @patch('financeiro.servicos.obter_periodo_mes_atual')
    def test_dashboard_conta_exibe_dados_e_bloqueia_conta_alheia(
        self,
        periodo_mock
    ):
        periodo_mock.return_value = (
            date(2026, 1, 1),
            date(2026, 1, 31)
        )
        self.client.force_login(self.usuario)
        movimentacao = self.criar_movimentacao('entrada', '300.00')

        resposta = self.client.get(
            reverse('dashboard_conta', args=[self.conta.id])
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(
            resposta,
            'financeiro/dashboard_conta.html'
        )
        self.assertEqual(resposta.context['conta'], self.conta)
        self.assertEqual(
            resposta.context['entradas_mes'],
            Decimal('300.00')
        )
        self.assertIn(
            movimentacao,
            resposta.context['movimentacoes_recentes']
        )
        self.assertContains(resposta, 'Dashboard da Conta')
        self.assertContains(
            resposta,
            reverse('resumo_conta', args=[self.conta.id])
        )
        self.assertContains(
            resposta,
            reverse('editar_conta', args=[self.conta.id])
        )
        self.assertContains(
            resposta,
            'id="graficoEntradasSaidasConta"'
        )
        self.assertContains(
            resposta,
            'id="graficoGastosCategoriaConta"'
        )
        self.assertContains(
            resposta,
            'id="graficoTransferenciasConta"'
        )
        self.assertContains(
            resposta,
            'id="graficoResultadoMensalConta"'
        )
        self.assertContains(
            resposta,
            'id="dados-entradas-saidas-conta-meses"'
        )
        self.assertContains(
            resposta,
            'id="dados-gastos-categoria-conta"'
        )
        self.assertContains(
            resposta,
            'id="dados-transferencias-conta-meses"'
        )
        self.assertContains(
            resposta,
            'id="dados-resultado-mensal-conta"'
        )
        self.assertContains(
            resposta,
            'Nenhum gasto encontrado nesta conta no mês atual.'
        )
        self.assertContains(
            resposta,
            (
                'Nenhuma transferência encontrada nesta conta '
                'nos últimos 6 meses.'
            )
        )
        self.assertEqual(
            self.client.get(
                reverse('dashboard_conta', args=[self.outra_conta.id])
            ).status_code,
            404
        )

    def test_inicio_aponta_contas_para_dashboard_individual(self):
        self.client.force_login(self.usuario)

        resposta = self.client.get(reverse('inicio'))

        self.assertContains(
            resposta,
            reverse('dashboard_conta', args=[self.conta.id])
        )
        self.assertContains(resposta, 'Dashboard')

    def test_crud_conta_e_bloqueio_de_objeto_alheio(self):
        self.client.force_login(self.usuario)
        resposta = self.client.post(reverse('criar_conta'), {
            'nome': 'Nova conta',
            'tipo': 'corrente',
            'saldo_inicial': '250.00',
            'descricao': '',
            'ativa': 'on',
        })
        conta = models.Conta.objects.get(nome='Nova conta')

        self.assertRedirects(resposta, reverse('listar_contas'))
        self.assertEqual(conta.usuario, self.usuario)

        resposta = self.client.post(
            reverse('editar_conta', args=[conta.id]),
            {
                'nome': 'Conta editada',
                'tipo': 'investimento',
                'saldo_inicial': '300.00',
                'descricao': 'Editada',
                'ativa': 'on',
            }
        )
        conta.refresh_from_db()
        self.assertRedirects(resposta, reverse('listar_contas'))
        self.assertEqual(conta.nome, 'Conta editada')

        self.assertEqual(
            self.client.get(
                reverse('detalhes_conta', args=[self.outra_conta.id])
            ).status_code,
            404
        )
        resposta = self.client.post(
            reverse('excluir_conta', args=[conta.id])
        )
        self.assertRedirects(resposta, reverse('listar_contas'))
        self.assertFalse(models.Conta.objects.filter(id=conta.id).exists())

    def test_editar_conta_com_movimentacao_mantem_saldo_inicial(self):
        self.client.force_login(self.usuario)
        self.criar_movimentacao('entrada', '100.00')

        resposta = self.client.post(
            reverse('editar_conta', args=[self.conta.id]),
            {
                'nome': 'Conta alterada',
                'tipo': 'corrente',
                'saldo_inicial': '9999.00',
                'descricao': '',
                'ativa': 'on',
            }
        )
        self.conta.refresh_from_db()

        self.assertRedirects(resposta, reverse('listar_contas'))
        self.assertEqual(self.conta.saldo_inicial, Decimal('1000.00'))
        self.assertEqual(self.conta.nome, 'Conta alterada')

    def test_listar_contas_aplica_filtros(self):
        self.client.force_login(self.usuario)
        self.conta_destino.ativa = False
        self.conta_destino.save()

        resposta = self.client.get(reverse('listar_contas'), {
            'nome': 'Reserva',
            'tipo': 'investimento',
            'ativa': 'nao',
        })

        self.assertQuerySetEqual(
            resposta.context['contas'],
            [self.conta_destino]
        )

    def test_detalhes_conta_valida_url_de_retorno(self):
        self.client.force_login(self.usuario)
        url = reverse('detalhes_conta', args=[self.conta.id])
        retorno_filtrado = '/contas/?nome=principal&ativa=sim'

        resposta = self.client.get(url, {
            'voltar_para': retorno_filtrado
        })
        self.assertEqual(resposta.context['voltar_para'], retorno_filtrado)
        self.assertContains(resposta, f'href="{retorno_filtrado.replace("&", "&amp;")}"')

        resposta = self.client.get(url, {
            'voltar_para': 'https://site-malicioso.example/contas/'
        })
        self.assertEqual(
            resposta.context['voltar_para'],
            reverse('listar_contas')
        )

    def test_crud_categoria_filtros_e_isolamento(self):
        self.client.force_login(self.usuario)
        resposta = self.client.post(reverse('criar_categoria'), {
            'nome': 'Lazer',
            'descricao': 'Passeios',
            'ativa': 'on',
        })
        categoria = models.Categoria.objects.get(nome='Lazer')
        self.assertRedirects(resposta, reverse('listar_categorias'))
        self.assertEqual(categoria.usuario, self.usuario)

        resposta = self.client.post(
            reverse('editar_categoria', args=[categoria.id]),
            {'nome': 'Lazer editado', 'descricao': '', 'ativa': ''}
        )
        categoria.refresh_from_db()
        self.assertRedirects(resposta, reverse('listar_categorias'))
        self.assertFalse(categoria.ativa)

        resposta = self.client.get(
            reverse('listar_categorias'),
            {'nome': 'editado', 'ativa': 'nao'}
        )
        self.assertQuerySetEqual(
            resposta.context['categorias'],
            [categoria]
        )
        self.assertEqual(
            self.client.get(
                reverse(
                    'detalhes_categoria',
                    args=[self.outra_categoria.id]
                )
            ).status_code,
            404
        )

        resposta = self.client.post(
            reverse('excluir_categoria', args=[categoria.id])
        )
        self.assertRedirects(resposta, reverse('listar_categorias'))
        self.assertFalse(
            models.Categoria.objects.filter(id=categoria.id).exists()
        )

    def test_detalhes_categoria_valida_url_de_retorno(self):
        self.client.force_login(self.usuario)
        url = reverse('detalhes_categoria', args=[self.categoria.id])
        retorno_filtrado = '/categorias/?nome=Alimenta%C3%A7%C3%A3o&ativa=sim'

        resposta = self.client.get(url, {
            'voltar_para': retorno_filtrado
        })
        self.assertEqual(resposta.context['voltar_para'], retorno_filtrado)

        resposta = self.client.get(url, {
            'voltar_para': '//site-malicioso.example/categorias/'
        })
        self.assertEqual(
            resposta.context['voltar_para'],
            reverse('listar_categorias')
        )

    def test_crud_movimentacao_e_isolamento(self):
        self.client.force_login(self.usuario)
        dados = {
            'descricao': 'Salário',
            'valor': '800.00',
            'tipo': 'entrada',
            'categoria': '',
            'conta_origem': '',
            'conta_destino': str(self.conta.id),
            'data': '2026-01-10',
            'hora': '10:00',
            'observacao': '',
        }
        resposta = self.client.post(reverse('criar_movimentacao'), dados)
        movimentacao = models.Movimentacao.objects.get(descricao='Salário')
        self.assertRedirects(resposta, reverse('listar_movimentacoes'))
        self.assertEqual(movimentacao.usuario, self.usuario)

        dados.update({'descricao': 'Salário editado', 'valor': '900.00'})
        resposta = self.client.post(
            reverse('editar_movimentacao', args=[movimentacao.id]),
            dados
        )
        movimentacao.refresh_from_db()
        self.assertRedirects(resposta, reverse('listar_movimentacoes'))
        self.assertEqual(movimentacao.valor, Decimal('900.00'))

        alheia = self.criar_movimentacao(
            usuario=self.outro_usuario,
            conta_destino=self.outra_conta
        )
        self.assertEqual(
            self.client.get(
                reverse('detalhes_movimentacao', args=[alheia.id])
            ).status_code,
            404
        )

        resposta = self.client.post(
            reverse('excluir_movimentacao', args=[movimentacao.id])
        )
        self.assertRedirects(resposta, reverse('listar_movimentacoes'))
        self.assertFalse(
            models.Movimentacao.objects.filter(id=movimentacao.id).exists()
        )

    def test_detalhes_movimentacao_valida_url_de_retorno(self):
        self.client.force_login(self.usuario)
        movimentacao = self.criar_movimentacao('entrada', '100.00')
        url = reverse(
            'detalhes_movimentacao',
            args=[movimentacao.id]
        )
        retorno_filtrado = '/movimentacoes/?tipo=entrada&descricao=salario'

        resposta = self.client.get(url, {
            'voltar_para': retorno_filtrado
        })
        self.assertEqual(resposta.context['voltar_para'], retorno_filtrado)

        resposta = self.client.get(url, {
            'voltar_para': 'javascript:alert(1)'
        })
        self.assertEqual(
            resposta.context['voltar_para'],
            reverse('listar_movimentacoes')
        )

    def test_criar_movimentacao_exige_conta_ativa(self):
        usuario_sem_conta = User.objects.create_user(
            username='sem_conta',
            password=self.senha
        )
        self.client.force_login(usuario_sem_conta)

        resposta = self.client.get(
            reverse('criar_movimentacao'),
            follow=True
        )

        self.assertRedirects(
            resposta,
            reverse('listar_movimentacoes')
        )
        self.assertContains(
            resposta,
            'Você precisa ter uma conta ativa para cadastrar movimentações.'
        )
        self.assertContains(resposta, 'Criar conta agora')
        self.assertContains(resposta, reverse('criar_conta'))

        resposta_post = self.client.post(
            reverse('criar_movimentacao'),
            {
                'descricao': 'Movimentação sem conta',
                'valor': '100.00',
                'tipo': 'entrada',
                'data': '2026-01-10',
                'hora': '10:00',
            }
        )

        self.assertRedirects(
            resposta_post,
            reverse('listar_movimentacoes')
        )
        self.assertFalse(
            models.Movimentacao.objects.filter(
                usuario=usuario_sem_conta
            ).exists()
        )

    def test_listar_movimentacoes_aplica_filtros_e_descarta_invalidos(self):
        self.client.force_login(self.usuario)
        esperada = self.criar_movimentacao(
            'saida',
            '50.00',
            categoria=self.categoria,
            descricao='Mercado',
            data_movimentacao=date(2026, 1, 15)
        )
        self.criar_movimentacao(
            'entrada',
            '500.00',
            descricao='Salário',
            data_movimentacao=date(2026, 2, 1)
        )

        resposta = self.client.get(reverse('listar_movimentacoes'), {
            'data_inicio': '2026-01-01',
            'data_fim': '2026-01-31',
            'tipo': 'saida',
            'categoria': str(self.categoria.id),
            'conta_origem': str(self.conta.id),
            'descricao': 'merc',
        })
        self.assertQuerySetEqual(
            resposta.context['movimentacoes'],
            [esperada]
        )

        resposta = self.client.get(reverse('listar_movimentacoes'), {
            'data_inicio': 'data-invalida',
            'tipo': 'invalido',
            'categoria': str(self.outra_categoria.id),
            'conta_origem': str(self.outra_conta.id),
        })
        self.assertEqual(resposta.context['data_inicio_filtro'], '')
        self.assertEqual(resposta.context['tipo_filtro'], '')
        self.assertEqual(resposta.context['categoria_filtro'], '')
        self.assertEqual(resposta.context['conta_origem_filtro'], '')

    def test_resumos_geral_e_por_conta(self):
        self.client.force_login(self.usuario)
        self.criar_movimentacao('entrada', '300.00')
        self.criar_movimentacao('saida', '100.00')

        resposta = self.client.get(reverse('resumo_financeiro'), {
            'data_inicio': '2026-01-01',
            'data_fim': '2026-01-31',
            'tipos': ['entrada', 'saida'],
        })
        self.assertEqual(
            resposta.context['total_entradas_periodo'],
            Decimal('300.00')
        )
        self.assertEqual(
            resposta.context['total_saidas_periodo'],
            Decimal('100.00')
        )
        self.assertEqual(
            resposta.context['resultado_periodo'],
            Decimal('200.00')
        )

        resposta = self.client.get(
            reverse('resumo_conta', args=[self.conta.id]),
            {
                'data_inicio': '2026-01-01',
                'data_fim': '2026-01-31',
            }
        )
        self.assertEqual(resposta.context['entradas'], Decimal('300.00'))
        self.assertEqual(resposta.context['saidas'], Decimal('100.00'))
        self.assertEqual(
            self.client.get(
                reverse('resumo_conta', args=[self.outra_conta.id])
            ).status_code,
            404
        )

    def test_resumo_por_conta_ignora_filtros_de_tipo_e_categoria(self):
        self.client.force_login(self.usuario)
        self.criar_movimentacao('entrada', '300.00')
        self.criar_movimentacao(
            'saida',
            '100.00',
            categoria=self.categoria
        )
        self.criar_movimentacao('transferencia', '50.00')
        self.criar_movimentacao(
            'entrada',
            '900.00',
            data_movimentacao=date(2026, 2, 1)
        )

        resposta = self.client.get(reverse('resumo_financeiro'), {
            'data_inicio': '2026-01-01',
            'data_fim': '2026-01-31',
            'tipos': ['saida'],
            'categorias': [str(self.categoria.id)],
        })

        self.assertEqual(
            resposta.context['total_entradas_periodo'],
            0
        )
        self.assertEqual(
            resposta.context['total_saidas_periodo'],
            Decimal('100.00')
        )

        resumo_conta = next(
            item
            for item in resposta.context['resumo_por_conta']
            if item['conta'] == self.conta
        )
        self.assertEqual(resumo_conta['entradas'], Decimal('300.00'))
        self.assertEqual(resumo_conta['saidas'], Decimal('100.00'))
        self.assertEqual(
            resumo_conta['transferencias_recebidas'],
            0
        )
        self.assertEqual(
            resumo_conta['transferencias_enviadas'],
            Decimal('50.00')
        )
        self.assertEqual(
            resumo_conta['resultado_periodo'],
            Decimal('150.00')
        )
        self.assertContains(
            resposta,
            'De 01/01/2026'
        )
        self.assertContains(
            resposta,
            'Até 31/01/2026'
        )
        self.assertEqual(
            resposta.context['tipos_filtro_rotulo'],
            'Saída'
        )
        self.assertEqual(
            resposta.context['categorias_filtro_rotulo'],
            'Alimentação'
        )
        self.assertContains(
            resposta,
            'Limpar filtros'
        )


class UsuariosViewsTestCase(FinanceiroTestMixin, TestCase):
    def setUp(self):
        self.criar_dados_basicos()

    def test_cadastro_cria_usuario_e_categorias_padrao(self):
        resposta = self.client.post(reverse('cadastro'), {
            'username': 'cadastrado',
            'first_name': 'Usuário',
            'last_name': 'Cadastrado',
            'email': 'cadastrado@example.com',
            'password1': self.senha,
            'password2': self.senha,
        })
        usuario = User.objects.get(username='cadastrado')

        self.assertRedirects(resposta, reverse('login'))
        self.assertFalse(usuario.is_staff)
        self.assertEqual(
            models.Categoria.objects.filter(usuario=usuario).count(),
            len(servicos.CATEGORIAS_PADRAO)
        )

    def test_usuario_autenticado_nao_acessa_cadastro_ou_login(self):
        self.client.force_login(self.usuario)

        self.assertRedirects(
            self.client.get(reverse('cadastro')),
            reverse('inicio')
        )
        self.assertRedirects(
            self.client.get(reverse('login')),
            reverse('inicio')
        )

    def test_login_logout_e_perfil(self):
        resposta = self.client.post(reverse('login'), {
            'username': self.usuario.username,
            'password': self.senha,
        })
        self.assertRedirects(resposta, reverse('inicio'))
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(
            self.client.get(reverse('perfil')).status_code,
            200
        )

        resposta = self.client.get(reverse('logout'))
        self.assertRedirects(resposta, reverse('inicio'))
        self.assertIn('_auth_user_id', self.client.session)

        resposta = self.client.post(reverse('logout'))
        self.assertRedirects(resposta, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_editar_perfil_valida_senha_e_salva_dados(self):
        self.client.force_login(self.usuario)
        url = reverse('editar_perfil')
        dados = {
            'first_name': 'Nome alterado',
            'last_name': 'Sobrenome',
            'email': 'alterado@example.com',
            'senha_atual': 'errada',
        }

        resposta = self.client.post(url, dados)
        self.assertEqual(resposta.status_code, 200)
        self.assertIn('senha_atual', resposta.context['form'].errors)

        dados['senha_atual'] = self.senha
        resposta = self.client.post(url, dados)
        self.usuario.refresh_from_db()
        self.assertRedirects(resposta, reverse('perfil'))
        self.assertEqual(self.usuario.first_name, 'Nome alterado')

    def test_alterar_senha_mantem_sessao_autenticada(self):
        self.client.force_login(self.usuario)
        nova_senha = 'NovaSenha456!'

        resposta = self.client.post(reverse('alterar_senha'), {
            'old_password': self.senha,
            'new_password1': nova_senha,
            'new_password2': nova_senha,
        })
        self.usuario.refresh_from_db()

        self.assertRedirects(resposta, reverse('perfil'))
        self.assertTrue(self.usuario.check_password(nova_senha))
        self.assertIn('_auth_user_id', self.client.session)

    def test_listar_usuarios_restrito_a_administradores(self):
        self.assertFalse(usuario_e_administrador(self.usuario))
        self.client.force_login(self.usuario)
        self.assertRedirects(
            self.client.get(reverse('listar_usuarios')),
            f"{reverse('inicio')}?next={reverse('listar_usuarios')}"
        )

        administrador = User.objects.create_user(
            username='admin',
            password=self.senha,
            is_staff=True
        )
        self.client.force_login(administrador)
        resposta = self.client.get(reverse('listar_usuarios'))

        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(usuario_e_administrador(administrador))
        self.assertIn(self.usuario, resposta.context['usuarios'])
