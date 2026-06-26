from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Conta(models.Model):
    # TIPOS DISPONÍVEIS PARA CONTA
    TIPO_CONTA_CHOICES = [
        ('corrente', 'Conta Corrente'),
        ('investimento', 'Investimento/Caixinha'),
    ]

    # DADOS PRINCIPAIS DA CONTA
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CONTA_CHOICES)
    saldo_inicial = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    descricao = models.TextField(blank=True, null=True)
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def saldo_atual(self):
        # CALCULA ENTRADAS, SAÍDAS E TRANSFERÊNCIAS DA CONTA
        entradas = self.movimentacoes_destino.filter(tipo='entrada').aggregate(
            total=models.Sum('valor')
        )['total'] or 0

        saidas = self.movimentacoes_origem.filter(tipo='saida').aggregate(
            total=models.Sum('valor')
        )['total'] or 0

        transferencias_recebidas = self.movimentacoes_destino.filter(tipo='transferencia').aggregate(
            total=models.Sum('valor')
        )['total'] or 0

        transferencias_enviadas = self.movimentacoes_origem.filter(tipo='transferencia').aggregate(
            total=models.Sum('valor')
        )['total'] or 0

        return self.saldo_inicial + entradas - saidas + transferencias_recebidas - transferencias_enviadas


class Categoria(models.Model):
    # DADOS PRINCIPAIS DA CATEGORIA
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Movimentacao(models.Model):
    # TIPOS DISPONÍVEIS PARA MOVIMENTAÇÃO
    TIPO_MOVIMENTACAO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
        ('transferencia', 'Transferência Interna'),
    ]

    # DADOS PRINCIPAIS DA MOVIMENTAÇÃO
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=150)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMENTACAO_CHOICES)

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    conta_origem = models.ForeignKey(
        Conta,
        on_delete=models.CASCADE,
        related_name='movimentacoes_origem',
        blank=True,
        null=True
    )

    conta_destino = models.ForeignKey(
        Conta,
        on_delete=models.CASCADE,
        related_name='movimentacoes_destino',
        blank=True,
        null=True
    )

    data = models.DateField(blank=True, null=True)
    hora = models.TimeField(blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'
        ordering = ['-data', '-hora', '-criada_em']

    def __str__(self):
        return f'{self.descricao} - R$ {self.valor}'

    def clean(self):
        # VALIDA REGRAS GERAIS DA MOVIMENTAÇÃO
        if self.valor <= 0:
            raise ValidationError(
                'O valor da movimentação deve ser maior que zero.')

        if self.data and not self.hora:
            raise ValidationError(
                'Ao informar uma data, a hora da movimentação também deve ser informada.')

        # VALIDA CAMPOS OBRIGATÓRIOS POR TIPO
        if self.tipo == 'entrada':
            if not self.conta_destino:
                raise ValidationError(
                    'Entradas precisam de uma conta de destino.')
            if self.conta_origem:
                raise ValidationError(
                    'Entradas não devem ter conta de origem.')

        if self.tipo == 'saida':
            if not self.conta_origem:
                raise ValidationError(
                    'Saídas precisam de uma conta de origem.')
            if self.conta_destino:
                raise ValidationError('Saídas não devem ter conta de destino.')

        if self.tipo == 'transferencia':
            if not self.conta_origem or not self.conta_destino:
                raise ValidationError(
                    'Transferências precisam de conta de origem e destino.')
            if self.conta_origem == self.conta_destino:
                raise ValidationError(
                    'A conta de origem e destino não podem ser iguais.')

        if self.tipo == 'transferencia' and self.categoria:
            raise ValidationError(
                'Transferências internas não devem possuir categoria.')

    def save(self, *args, **kwargs):
        # PREENCHE DATA E HORA AUTOMATICAMENTE QUANDO NÃO INFORMADAS
        agora = timezone.localtime()

        if not self.data:
            self.data = agora.date()

        if not self.hora:
            self.hora = agora.time()

        self.full_clean()
        super().save(*args, **kwargs)
