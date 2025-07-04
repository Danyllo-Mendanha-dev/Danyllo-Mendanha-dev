# biblioteca/forms.py
from django import forms
from .models import Funcionario, Leitor, Livro, Emprestimo 

class FuncionarioForm(forms.ModelForm):
    # Definindo o tipo de input para o campo de senha
    senha = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = Funcionario
        # Inclua todos os campos do seu modelo que devem aparecer no form
        fields = ['nome', 'email', 'senha', 'telefone', 'cpf', 'endereco', 'data_nascimento']

    def __init__(self, *args, **kwargs):
        super(FuncionarioForm, self).__init__(*args, **kwargs)
        
        # Adiciona a classe 'form-control' do Bootstrap a todos os campos do formulário
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Customiza o campo de data para aceitar o formato brasileiro
        self.fields['data_nascimento'].widget = forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        )

class LeitorForm(forms.ModelForm):
    class Meta:
        model = Leitor
        # Campos do modelo Leitor que aparecerão no formulário
        fields = ['nome', 'cpf', 'email', 'telefone', 'endereco', 'data_nascimento']

    def __init__(self, *args, **kwargs):
        super(LeitorForm, self).__init__(*args, **kwargs)
        
        # Adiciona a classe 'form-control' a todos os campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Customiza o campo de data para usar o widget de data do navegador
        self.fields['data_nascimento'].widget = forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        )

class LivroForm(forms.ModelForm):
    class Meta:
        model = Livro
        # O campo 'status' não é incluído aqui, pois por padrão
        # todo livro novo será 'disponivel'.
        fields = ['nome', 'isbn', 'autor', 'genero', 'data_publicacao']

    def __init__(self, *args, **kwargs):
        super(LivroForm, self).__init__(*args, **kwargs)
        
        # Adiciona a classe 'form-control' a todos os campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        
        # Customiza o campo de data para usar o widget de data do navegador
        self.fields['data_publicacao'].widget = forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control'}
        )

class EmprestimoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra o campo 'livro' para mostrar apenas os livros com status 'disponivel'
        self.fields['livro'].queryset = Livro.objects.filter(status='disponivel')
        self.fields['livro'].empty_label = "Selecione um livro disponível"
        self.fields['leitor'].empty_label = "Selecione um leitor"

    class Meta:
        model = Emprestimo
        # Campos que o funcionário irá preencher no formulário
        fields = ['leitor', 'livro']
