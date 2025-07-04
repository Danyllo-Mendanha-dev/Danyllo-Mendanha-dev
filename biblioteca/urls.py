# biblioteca_projeto/urls.py
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
# Importe todas as views do seu app 'biblioteca'
from biblioteca import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # URLs de Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home_view, name='home'), # Página inicial

    # URLs para Funcionário (CRUD)
    path('funcionario/', views.funcionario_index, name='funcionario_index'),
    path('funcionario/cadastrar/', views.cadastrar_funcionario, name='cadastrar_funcionario'),
    path('funcionario/consultar/', views.consultar_funcionario, name='funcionario_consultar'),
    path('funcionario/atualizar/<int:pk>/', views.atualizar_funcionario, name='atualizar_funcionario'),
    path('funcionario/excluir/<int:pk>/', views.excluir_funcionario, name='excluir_funcionario'),

      # --- NOVAS URLs para Leitor (CRUD) ---
    path('leitor/', views.leitor_index, name='leitor_index'),
    path('leitor/cadastrar/', views.cadastrar_leitor, name='cadastrar_leitor'),
    path('leitor/consultar/', views.consultar_leitor, name='leitor_consultar'),
    path('leitor/atualizar/<int:pk>/', views.atualizar_leitor, name='atualizar_leitor'),
    path('leitor/excluir/<int:pk>/', views.excluir_leitor, name='excluir_leitor'),

     # --- NOVAS URLs para Livro (CRUD) ---
    path('livro/', views.livro_index, name='livro_index'),
    path('livro/cadastrar/', views.cadastrar_livro, name='cadastrar_livro'),
    path('livro/consultar/', views.consultar_livro, name='livro_consultar'),
    path('livro/atualizar/<int:pk>/', views.atualizar_livro, name='atualizar_livro'),
    path('livro/excluir/<int:pk>/', views.excluir_livro, name='excluir_livro'),

     # URLs para Livro (CRUD - OBRA/TÍTULO)
    path('livro/', views.livro_index, name='livro_index'),
    path('livro/cadastrar/', views.cadastrar_livro, name='cadastrar_livro'),
    path('livro/consultar/', views.consultar_livro, name='livro_consultar'),
    path('livro/atualizar/<int:pk>/', views.atualizar_livro, name='atualizar_livro'),
    path('livro/excluir/<int:pk>/', views.excluir_livro, name='excluir_livro'),

    # --- URLs para Empréstimo (CRUD) ---
    path('emprestimo/', views.emprestimo_index, name='emprestimo_index'),
    path('emprestimo/cadastrar/', views.cadastrar_emprestimo, name='cadastrar_emprestimo'),
    path('emprestimo/consultar/', views.consultar_emprestimos, name='consultar_emprestimos'),
    path('emprestimo/atualizar/<int:pk>/', views.atualizar_emprestimo, name='atualizar_emprestimo'),
    path('emprestimo/excluir/<int:pk>/', views.excluir_emprestimo, name='excluir_emprestimo'),

    # --- NOVA URL PARA RELATÓRIOS ---
    path('relatorio/', views.relatorio_index, name='relatorio_index'),
    path('relatorio/livros_emprestados/', views.relatorio_livros_emprestados, name='relatorio_livros_emprestados'),
    path('relatorio/historico_livro/', views.relatorio_historico_livro, name='relatorio_historico_livro'),
    path('relatorio/leitores_atrasados/', views.relatorio_leitores_atrasados, name='relatorio_leitores_atrasados'),

     # --- NOVA URL PÚBLICA PARA O ACERVO ---
    path('acervo/', views.acervo_view, name='acervo'),

    
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Se você tiver arquivos de mídia (ex: fotos de livros), adicione também:
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)