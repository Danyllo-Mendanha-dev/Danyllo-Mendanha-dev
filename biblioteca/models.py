# biblioteca/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager # Usaremos o User do Django para autenticação
from django.utils import timezone
import datetime

# Se você quiser usar seu próprio modelo de usuário para funcionários
# com mais campos, você pode estender AbstractUser. Por simplicidade,
# vamos usar um modelo de Funcionario separado por enquanto, e para autenticação
# inicial faremos uma checagem simples, mas o ideal é usar o sistema de Auth do Django.

class Funcionario(models.Model):
    # Campos que você tem no HTML de cadastro de funcionário
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    # Importante: Senhas devem ser hashed! Por enquanto, um CharField simples
    # para corresponder ao seu HTML, mas isso será melhorado.
    senha = models.CharField(max_length=128)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    cpf = models.CharField(max_length=14, unique=True)
    endereco = models.CharField(max_length=200, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    # Adicione campos de auditoria
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Funcionário"
        verbose_name_plural = "Funcionários"

# Outros modelos como Leitor, Livro, Emprestimo, Acervo virão depois.

class Leitor(models.Model):
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=200, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    # Campos de auditoria (opcional, mas boa prática)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Leitor"
        verbose_name_plural = "Leitores"




class Livro(models.Model):
    STATUS_CHOICES = [
        ('disponivel', 'Disponivel'),
        ('emprestado','Emprestado')
    ]

    nome = models.CharField(max_length=200)
    isbn = models.CharField(max_length=17, unique=True, help_text="Ex: 978-85-333-0222-0") # Padrão ISBN-13
    autor = models.CharField(max_length=100)
    genero = models.CharField(max_length=50, blank=True, null=True)
    data_publicacao = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='disponivel',
    )
    # Campos de auditoria
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.autor})"

    class Meta:
        verbose_name = "Livro"
        verbose_name_plural = "Livros"

# ... (EMPRESTIMOS) ...

class Emprestimo(models.Model):
    """
    Modelo para registrar o empréstimo de um livro para um leitor.
    """
    STATUS_CHOICES = [
        ('EMPRESTADO', 'Emprestado'),
        ('DEVOLVIDO', 'Devolvido'),
        ('ATRASADO', 'Atrasado'),
    ]

    # --- Relacionamentos ---
    livro = models.ForeignKey(Livro, on_delete=models.PROTECT, related_name='emprestimos')
    leitor = models.ForeignKey(Leitor, on_delete=models.PROTECT, related_name='emprestimos')
    funcionario = models.ForeignKey(Funcionario, on_delete=models.SET_NULL, null=True, related_name='emprestimos_realizados')

    # --- Datas ---
    data_emprestimo = models.DateField(default=timezone.now)
    data_devolucao_prevista = models.DateField()
    data_devolucao_real = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='EMPRESTADO')

    # --- Auditoria (seguindo o padrão dos seus outros modelos) ---
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Define a data de devolução prevista para 14 dias após o empréstimo
        if not self.id:
            self.data_devolucao_prevista = self.data_emprestimo + datetime.timedelta(days=14)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.livro.nome} emprestado para {self.leitor.nome}"

    class Meta:
        verbose_name = "Empréstimo"
        verbose_name_plural = "Empréstimos"
        ordering = ['-data_emprestimo']