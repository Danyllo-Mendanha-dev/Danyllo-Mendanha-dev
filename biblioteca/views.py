# biblioteca/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib import messages # Para mensagens de feedback ao usuário
# from django.contrib.auth import authenticate, login, logout # Será usado para o sistema de autenticação real do Django
from .models import Funcionario, Leitor, Livro
from .forms import FuncionarioForm, LeitorForm, LivroForm
from django.utils import timezone

# --- Views de Autenticação (Login e Logout) ---
# Usando a simulação do seu HTML por enquanto.
# O ideal é integrar com o sistema de autenticação do Django (django.contrib.auth)
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        # Simulação de autenticação com o modelo Funcionario
        try:
            funcionario = Funcionario.objects.get(email=email)
            # AQUI: Em um sistema real, você NUNCA compararia senhas em texto puro.
            # Usaria `check_password` do Django. Isso é só para o exemplo inicial.
            if funcionario.senha == senha:
                # Simula o login mantendo o ID e nome na sessão
                request.session['funcionario_logado_id'] = funcionario.id
                request.session['funcionario_logado_nome'] = funcionario.nome
                messages.success(request, f"Bem-vindo, {funcionario.nome}!")
                return redirect('home')
            else:
                messages.error(request, "Email ou senha inválidos.")
        except Funcionario.DoesNotExist:
            messages.error(request, "Email ou senha inválidos.")
    return render(request, 'login.html')

def logout_view(request):
    # Limpa a sessão do funcionário logado
    request.session.pop('funcionario_logado_id', None)
    request.session.pop('funcionario_logado_nome', None)
    messages.info(request, "Você foi desconectado.")
    return redirect('login')

# Middleware simples para proteger as views
def funcionario_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'funcionario_logado_id' not in request.session:
            messages.warning(request, "Você precisa estar logado para acessar esta página.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# --- Views Gerais ---

@funcionario_login_required
def home_view(request):
    """
    Exibe o dashboard principal com estatísticas da biblioteca.
    """
    # Realiza as contagens no banco de dados
    total_livros = Livro.objects.count()
    total_leitores = Leitor.objects.count()
    total_funcionarios = Funcionario.objects.count()
    
    # Conta apenas os empréstimos que não foram devolvidos
    emprestimos_ativos = Emprestimo.objects.filter(status__in=['EMPRESTADO', 'ATRASADO']).count()

    context = {
        'total_livros': total_livros,
        'total_leitores': total_leitores,
        'total_funcionarios': total_funcionarios,
        'emprestimos_ativos': emprestimos_ativos,
    }
    
    return render(request, 'home.html', context)


# --- Views para Funcionário (CRUD) ---
@funcionario_login_required
def funcionario_index(request):
    # Esta é a página principal de gestão de funcionário (funcionario.html)
    return render(request, 'funcionario/funcionario.html')

@funcionario_login_required
def cadastrar_funcionario(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Funcionário cadastrado com sucesso!")
            return redirect('funcionario_consultar') # Redireciona para a lista
        else:
            messages.error(request, "Erro ao cadastrar funcionário. Verifique os dados.")
    else:
        form = FuncionarioForm() # Formulário vazio para GET
    return render(request, 'funcionario/cadastrar_funcionario.html', {'form': form})

@funcionario_login_required
def consultar_funcionario(request):
    query = request.GET.get('q')
    funcionarios = Funcionario.objects.all().order_by('nome')

    if query:
        # Filtra por nome OU email que contenham o termo da busca
        funcionarios = funcionarios.filter(
            Q(nome__icontains=query) | Q(email__icontains=query)
        )
        if not funcionarios.exists():
            messages.info(request, f"Nenhum funcionário encontrado para a busca: '{query}'.")

    return render(request, 'funcionario/consultar_funcionario.html', {'funcionarios': funcionarios, 'query': query})

@funcionario_login_required
def atualizar_funcionario(request, pk): # 'pk' para Primary Key do funcionário
    funcionario = get_object_or_404(Funcionario, pk=pk)
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, instance=funcionario)
        if form.is_valid():
            form.save()
            messages.success(request, "Funcionário atualizado com sucesso!")
            return redirect('funcionario_consultar')
        else:
            messages.error(request, "Erro ao atualizar funcionário. Verifique os dados.")
    else:
        form = FuncionarioForm(instance=funcionario) # Preenche o formulário com dados existentes
    return render(request, 'funcionario/atualizar_funcionario.html', {'form': form, 'funcionario': funcionario})

@funcionario_login_required
def excluir_funcionario(request, pk):
    funcionario = get_object_or_404(Funcionario, pk=pk)
    if request.method == 'POST':
        funcionario.delete()
        messages.success(request, "Funcionário excluído com sucesso!")
        return redirect('funcionario_consultar')
    # Se for GET, apenas exibe uma página de confirmação
    return render(request, 'funcionario/excluir_funcionario.html', {'funcionario': funcionario})

# --- Views para Leitor (CRUD) ---
@funcionario_login_required
def leitor_index(request):
    # Esta é a página principal de gestão de leitor (leitor.html)
    return render(request, 'leitor/leitor.html')

@funcionario_login_required
def cadastrar_leitor(request):
    if request.method == 'POST':
        form = LeitorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Leitor cadastrado com sucesso!")
            return redirect('leitor_consultar') # Redireciona para a lista
        else:
            messages.error(request, "Erro ao cadastrar leitor. Verifique os dados.")
    else:
        form = LeitorForm() # Formulário vazio para GET
    return render(request, 'leitor/cadastrar_leitor.html', {'form': form})

@funcionario_login_required
def consultar_leitor(request):
    query = request.GET.get('q')
    leitores = Leitor.objects.all().order_by('nome')

    if query:
        # Filtra por nome OU CPF que contenham o termo da busca
        leitores = leitores.filter(
            Q(nome__icontains=query) | Q(cpf__icontains=query)
        )
        if not leitores.exists():
            messages.info(request, f"Nenhum leitor encontrado para a busca: '{query}'.")

    return render(request, 'leitor/consultar_leitor.html', {'leitores': leitores, 'query': query})

@funcionario_login_required
def atualizar_leitor(request, pk): # 'pk' para Primary Key do leitor
    leitor = get_object_or_404(Leitor, pk=pk)
    if request.method == 'POST':
        form = LeitorForm(request.POST, instance=leitor)
        if form.is_valid():
            form.save()
            messages.success(request, "Leitor atualizado com sucesso!")
            return redirect('leitor_consultar')
        else:
            messages.error(request, "Erro ao atualizar leitor. Verifique os dados.")
    else:
        form = LeitorForm(instance=leitor) # Preenche o formulário com dados existentes
    return render(request, 'leitor/atualizar_leitor.html', {'form': form, 'leitor': leitor})

@funcionario_login_required
def excluir_leitor(request, pk):
    leitor = get_object_or_404(Leitor, pk=pk)
    if request.method == 'POST':
        leitor.delete()
        messages.success(request, "Leitor excluído com sucesso!")
        return redirect('leitor_consultar')
    # Se for GET, apenas exibe uma página de confirmação
    return render(request, 'leitor/excluir_leitor.html', {'leitor': leitor})


# --- Views para Livro (CRUD) ---
@funcionario_login_required
def livro_index(request):
    # Página principal de gestão de livros (livro.html)
    return render(request, 'livro/livro.html')

@funcionario_login_required
def cadastrar_livro(request):
    if request.method == 'POST':
        form = LivroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Livro cadastrado com sucesso!")
            return redirect('livro_consultar') # Redireciona para a lista
        else:
            messages.error(request, "Erro ao cadastrar livro. Verifique os dados.")
    else:
        form = LivroForm() # Formulário vazio para GET
    return render(request, 'livro/cadastrar_livro.html', {'form': form})

# biblioteca/views.py

@funcionario_login_required
def consultar_livro(request):
    """
    Painel de gerenciamento de livros com busca e abas para filtrar por status.
    """
    # Parâmetros da URL
    query = request.GET.get('q')
    status_selecionado = request.GET.get('status', 'disponivel') # Padrão é 'disponivel'

    # Começa com todos os livros
    livros_list = Livro.objects.all().order_by('nome')

    # 1. Aplica o filtro de busca primeiro, se houver
    if query:
        livros_list = livros_list.filter(
            Q(nome__icontains=query) | Q(isbn__icontains=query) | Q(autor__icontains=query)
        )
    
    # Contagens para as abas (baseadas na lista completa ou na busca)
    count_disponiveis = livros_list.filter(status='disponivel').count()
    count_emprestados = livros_list.filter(status='emprestado').count()
    
    # 2. Aplica o filtro de status (aba selecionada)
    if status_selecionado == 'emprestados':
        livros_filtrados = livros_list.filter(status='emprestado')
    else: # 'disponivel'
        livros_filtrados = livros_list.filter(status='disponivel')

    context = {
        'livros': livros_filtrados,
        'query': query,
        'status_selecionado': status_selecionado,
        'count_disponiveis': count_disponiveis,
        'count_emprestados': count_emprestados,
    }
    
    return render(request, 'livro/consultar_livro.html', context)

@funcionario_login_required
def atualizar_livro(request, pk): # 'pk' para Primary Key do livro
    livro = get_object_or_404(Livro, pk=pk)
    if request.method == 'POST':
        form = LivroForm(request.POST, instance=livro)
        if form.is_valid():
            form.save()
            messages.success(request, "Livro atualizado com sucesso!")
            return redirect('livro_consultar')
        else:
            messages.error(request, "Erro ao atualizar livro. Verifique os dados.")
    else:
        form = LivroForm(instance=livro) # Preenche o formulário com dados existentes
    return render(request, 'livro/atualizar_livro.html', {'form': form, 'livro': livro})

@funcionario_login_required
def excluir_livro(request, pk):
    livro = get_object_or_404(Livro, pk=pk)
    if request.method == 'POST':
        livro.delete()
        messages.success(request, "Livro excluído com sucesso!")
        return redirect('livro_consultar')
    # Se for GET, apenas exibe uma página de confirmação
    return render(request, 'livro/excluir_livro.html', {'livro': livro})


# --- Views para Livro (CRUD - Manterá o foco na OBRA/TÍTULO) ---
@funcionario_login_required
def livro_index(request):
    return render(request, 'livro/livro.html')

@funcionario_login_required
def cadastrar_livro(request):
    if request.method == 'POST':
        form = LivroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Livro (obra) cadastrado com sucesso!")
            return redirect('livro_consultar')
        else:
            messages.error(request, "Erro ao cadastrar livro. Verifique os dados.")
    else:
        form = LivroForm()
    return render(request, 'livro/cadastrar_livro.html', {'form': form})

@funcionario_login_required
def consultar_livro(request):
    query = request.GET.get('q')
    livros = Livro.objects.all()

    if query:
        livros = livros.filter(Q(nome__icontains=query) | Q(isbn__icontains=query))
        if not livros.exists():
            messages.info(request, f"Nenhum livro (obra) encontrado para a busca: '{query}'.")
    
    return render(request, 'livro/consultar_livro.html', {'livros': livros, 'query': query})

@funcionario_login_required
def atualizar_livro(request, pk):
    livro = get_object_or_404(Livro, pk=pk)
    if request.method == 'POST':
        form = LivroForm(request.POST, instance=livro)
        if form.is_valid():
            form.save()
            messages.success(request, "Livro (obra) atualizado com sucesso!")
            return redirect('livro_consultar')
        else:
            messages.error(request, "Erro ao atualizar livro. Verifique os dados.")
    else:
        form = LivroForm(instance=livro)
    return render(request, 'livro/atualizar_livro.html', {'form': form, 'livro': livro})

@funcionario_login_required
def excluir_livro(request, pk):
    livro = get_object_or_404(Livro, pk=pk)
    if request.method == 'POST':
        livro.delete()
        messages.success(request, "Livro (obra) excluído com sucesso!")
        return redirect('livro_consultar')
    return render(request, 'livro/excluir_livro.html', {'livro': livro})

# ... (outras importações e views)

# --- Views para Empréstimo ---

@funcionario_login_required
def emprestimo_index(request):
    """
    Renderiza a página principal de gestão de empréstimos.
    """
    return render(request, 'emprestimo/emprestimo.html')

# biblioteca/views.py

from .models import Funcionario, Leitor, Livro, Emprestimo # Verifique se Emprestimo está importado
from .forms import FuncionarioForm, LeitorForm, LivroForm, EmprestimoForm # Adicione EmprestimoForm

# ... (outras views) ...

@funcionario_login_required
def cadastrar_emprestimo(request):
    if request.method == 'POST':
        form = EmprestimoForm(request.POST)
        if form.is_valid():
            # Não salva o objeto no banco ainda, apenas cria uma instância
            emprestimo = form.save(commit=False)
            
            # --- Adiciona a lógica de negócio ---
            
            # 1. Associa o funcionário logado ao empréstimo
            try:
                funcionario_logado_id = request.session.get('funcionario_logado_id')
                emprestimo.funcionario = Funcionario.objects.get(pk=funcionario_logado_id)
            except Funcionario.DoesNotExist:
                messages.error(request, "Erro: Funcionário logado não encontrado.")
                return render(request, 'emprestimo/cadastrar_emprestimo.html', {'form': form})

            # 2. Salva o empréstimo no banco de dados
            emprestimo.save()
            
            # 3. Atualiza o status do livro para 'emprestado'
            livro_emprestado = emprestimo.livro
            livro_emprestado.status = 'emprestado'
            livro_emprestado.save()
            
            messages.success(request, f"Empréstimo do livro '{livro_emprestado.nome}' registrado com sucesso!")
            return redirect('consultar_emprestimos') # Redireciona para a lista de empréstimos
    else:
        form = EmprestimoForm() # Cria um formulário vazio para uma requisição GET
        
    return render(request, 'emprestimo/cadastrar_emprestimo.html', {'form': form})

# biblioteca/views.py

# ... (outras views) ...

# biblioteca/views.py

@funcionario_login_required
def consultar_emprestimos(request):
    """
    Painel de gerenciamento de empréstimos com abas para filtrar por status.
    """
    # Lógica para atualizar o status dos atrasados (que já temos)
    hoje = timezone.now().date()
    Emprestimo.objects.filter(data_devolucao_prevista__lt=hoje, status='EMPRESTADO').update(status='ATRASADO')

    # Pega o parâmetro 'aba' da URL para saber qual filtro aplicar
    aba_selecionada = request.GET.get('aba', 'andamento') # Padrão é 'andamento'

    # Começa com todos os empréstimos e depois filtra
    todos_emprestimos = Emprestimo.objects.select_related('livro', 'leitor', 'funcionario').all()

    if aba_selecionada == 'atrasados':
        emprestimos_filtrados = todos_emprestimos.filter(status='ATRASADO')
    elif aba_selecionada == 'historico':
        emprestimos_filtrados = todos_emprestimos.filter(status='DEVOLVIDO')
    else: # 'andamento'
        emprestimos_filtrados = todos_emprestimos.filter(status='EMPRESTADO')
    
    context = {
        'emprestimos': emprestimos_filtrados,
        'aba_selecionada': aba_selecionada,
        # Contagens para exibir nas abas
        'count_andamento': todos_emprestimos.filter(status='EMPRESTADO').count(),
        'count_atrasados': todos_emprestimos.filter(status='ATRASADO').count(),
        'count_historico': todos_emprestimos.filter(status='DEVOLVIDO').count(),
    }
    
    return render(request, 'emprestimo/consultar_emprestimos.html', context)

@funcionario_login_required
def atualizar_emprestimo(request, pk):
    emprestimo = get_object_or_404(Emprestimo, pk=pk)
    
    if request.method == 'POST':
        # 1. Mudar o status do empréstimo
        emprestimo.status = 'DEVOLVIDO'
        emprestimo.data_devolucao_real = timezone.now().date()
        emprestimo.save()

        # 2. Mudar o status do livro de volta para 'disponível'
        livro = emprestimo.livro
        livro.status = 'disponivel'
        livro.save()
        
        messages.success(request, f"Devolução do livro '{livro.nome}' registrada com sucesso!")
        return redirect('consultar_emprestimos')

    # Se a requisição for GET, apenas mostra a página de confirmação
    return render(request, 'emprestimo/atualizar_emprestimo.html', {'emprestimo': emprestimo})

# biblioteca/views.py

# ...

@funcionario_login_required
def excluir_emprestimo(request, pk):
    emprestimo = get_object_or_404(Emprestimo, pk=pk)

    if request.method == 'POST':
        livro = emprestimo.livro
        emprestimo.delete()
        
        # Opcional, mas recomendado: verificar se o livro deveria voltar a ser disponível
        # Esta lógica pode ser mais complexa se o livro tiver outros empréstimos
        # Por simplicidade, vamos assumir que ele volta a ser disponível
        livro.status = 'disponivel'
        livro.save()

        messages.success(request, "Registro de empréstimo excluído com sucesso.")
        return redirect('consultar_emprestimos')
    
    return render(request, 'emprestimo/excluir_emprestimo.html', {'emprestimo': emprestimo})

# biblioteca/views.py

@funcionario_login_required
def relatorio_index(request):
    """
    Renderiza a Central de Relatórios com dados prévios (ex: contagem de atrasos).
    """
    # Lógica para atualizar o status dos atrasados
    hoje = timezone.now().date()
    Emprestimo.objects.filter(data_devolucao_prevista__lt=hoje, status='EMPRESTADO').update(status='ATRASADO')

    # Contagem de empréstimos atrasados para exibir no card
    count_atrasados = Emprestimo.objects.filter(status='ATRASADO').count()

    context = {
        'count_atrasados': count_atrasados,
    }
    
    return render(request, 'relatorio/relatorio.html', context)

@funcionario_login_required
def relatorio_livros_emprestados(request):
    """
    Busca e exibe todos os empréstimos com status 'EMPRESTADO' ou 'ATRASADO'.
    """
    # Filtramos o modelo Emprestimo para pegar apenas os que nos interessam
    emprestimos_ativos = Emprestimo.objects.filter(
        status__in=['EMPRESTADO', 'ATRASADO']
    ).select_related('livro', 'leitor')

    context = {
        'emprestimos': emprestimos_ativos
    }
    
    return render(request, 'relatorio/livros_emprestados.html', context)

@funcionario_login_required
def relatorio_historico_livro(request):
    """
    Relatório que permite ao usuário selecionar um livro e ver todo o seu
    histórico de empréstimos.
    """
    # Pega o ID do livro da URL (ex: ?livro_id=5)
    livro_id = request.GET.get('livro_id')
    
    # Busca todos os livros para popular o menu de seleção
    todos_livros = Livro.objects.all().order_by('nome')
    
    livro_selecionado = None
    emprestimos = None

    if livro_id:
        # Se um livro foi selecionado, busca seu histórico
        livro_selecionado = get_object_or_404(Livro, pk=livro_id)
        emprestimos = Emprestimo.objects.filter(
            livro=livro_selecionado
        ).select_related('leitor', 'funcionario').order_by('-data_emprestimo')

    context = {
        'todos_livros': todos_livros,
        'livro_selecionado': livro_selecionado,
        'emprestimos': emprestimos
    }
    
    return render(request, 'relatorio/historico_livro.html', context)

@funcionario_login_required
def relatorio_leitores_atrasados(request):
    """
    Atualiza e exibe todos os leitores com empréstimos atrasados.
    """
    # 1. Atualiza o status de empréstimos que se tornaram atrasados
    # Pega a data de hoje
    hoje = timezone.now().date()
    # Busca empréstimos que estão 'EMPRESTADO' mas a data de devolução já passou
    emprestimos_para_atualizar = Emprestimo.objects.filter(
        data_devolucao_prevista__lt=hoje, 
        status='EMPRESTADO'
    )
    # Atualiza o status de todos eles para 'ATRASADO'
    emprestimos_para_atualizar.update(status='ATRASADO')

    # 2. Busca todos os empréstimos que agora estão com status 'ATRASADO'
    leitores_com_atraso = Emprestimo.objects.filter(
        status='ATRASADO'
    ).select_related('livro', 'leitor').order_by('leitor__nome', 'data_devolucao_prevista')

    context = {
        'emprestimos_atrasados': leitores_com_atraso
    }
    
    return render(request, 'relatorio/leitores_atrasados.html', context)


def acervo_view(request):
    """
    Exibe o acervo público de livros e permite a busca por nome ou autor.
    """
    # Pega o termo de busca da URL (ex: /acervo/?q=Harry Potter)
    query = request.GET.get('q')
    
    # Começa com todos os livros do acervo
    livros = Livro.objects.all().order_by('nome')

    if query:
        # Se houver uma busca, filtra os livros por nome OU autor
        livros = livros.filter(
            Q(nome__icontains=query) | Q(autor__icontains=query)
        )

    context = {
        'livros': livros,
        'query': query # Envia o termo de busca de volta para o template
    }
    
    return render(request, 'acervo.html', context)