#!/usr/bin/env python3
"""
Interface web opcional para o orquestrador de vídeos
Requer: pip install flask
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
from orchestrator import VideoOrchestrator
import config

app = Flask(__name__)
orchestrator = VideoOrchestrator()

@app.route('/')
def index():
    """Página principal"""
    summary = orchestrator.get_content_summary()
    return render_template('index.html', summary=summary)

@app.route('/process', methods=['GET', 'POST'])
def process_videos():
    """Página para processar vídeos"""
    if request.method == 'POST':
        directory = request.form.get('directory')
        recursive = request.form.get('recursive') == 'on'
        
        if directory and os.path.exists(directory):
            try:
                # Processa em background (em produção, use Celery ou similar)
                results = orchestrator.process_directory(directory, recursive)
                return jsonify({
                    'success': True,
                    'message': f'{len(results)} vídeos processados com sucesso',
                    'processed_count': len(results)
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'Erro ao processar: {str(e)}'
                })
        else:
            return jsonify({
                'success': False,
                'message': 'Diretório não existe ou não foi especificado'
            })
    
    return render_template('process.html')

@app.route('/search')
def search():
    """Página de busca"""
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    keywords = request.args.get('keywords', '')
    
    results = []
    
    if query:
        results = orchestrator.search_videos(query)
    elif category:
        results = orchestrator.search_by_category(category)
    elif keywords:
        results = orchestrator.search_by_keywords(keywords)
    
    return render_template('search.html', 
                         results=results, 
                         query=query, 
                         category=category, 
                         keywords=keywords,
                         categories=config.CATEGORIES)

@app.route('/api/search')
def api_search():
    """API endpoint para busca"""
    query = request.args.get('query', '')
    category = request.args.get('category', '')
    keywords = request.args.get('keywords', '')
    
    results = []
    
    if query:
        results = orchestrator.search_videos(query)
    elif category:
        results = orchestrator.search_by_category(category)
    elif keywords:
        results = orchestrator.search_by_keywords(keywords)
    
    return jsonify({
        'success': True,
        'results': results,
        'count': len(results)
    })

@app.route('/api/summary')
def api_summary():
    """API endpoint para resumo"""
    summary = orchestrator.get_content_summary()
    return jsonify(summary)

# Templates HTML inline (em produção, use arquivos separados)
@app.route('/templates/base.html')
def base_template():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Orquestrador de Vídeos</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { max-width: 1200px; margin: 0 auto; }
            .card { background: #f5f5f5; padding: 20px; margin: 10px 0; border-radius: 5px; }
            .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px; }
            .btn:hover { background: #0056b3; }
            .form-group { margin: 10px 0; }
            label { display: block; margin-bottom: 5px; }
            input, select { padding: 8px; width: 300px; }
            .result { border-left: 4px solid #007bff; padding: 10px; margin: 10px 0; background: white; }
            .nav { background: #343a40; padding: 10px 0; margin-bottom: 20px; }
            .nav a { color: white; text-decoration: none; margin: 0 20px; }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/">Início</a>
            <a href="/process">Processar</a>
            <a href="/search">Buscar</a>
        </div>
        <div class="container">
            {% block content %}{% endblock %}
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    # Cria templates básicos se não existirem
    template_dir = 'templates'
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    
    # Template index.html
    with open(f'{template_dir}/index.html', 'w', encoding='utf-8') as f:
        f.write('''
{% extends "base.html" %}
{% block content %}
<h1>Orquestrador de Vídeos</h1>

<div class="card">
    <h2>Resumo do Conteúdo</h2>
    <p><strong>Total de vídeos:</strong> {{ summary.total_videos }}</p>
    <p><strong>Duração total:</strong> {{ summary.total_duration_hours }} horas</p>
    
    <h3>Por categoria:</h3>
    <ul>
    {% for category, count in summary.categories.items() %}
        <li>{{ category }}: {{ count }} vídeos</li>
    {% endfor %}
    </ul>
</div>

<div class="card">
    <h2>Ações Rápidas</h2>
    <a href="/process" class="btn">Processar Vídeos</a>
    <a href="/search" class="btn">Buscar Conteúdo</a>
</div>
{% endblock %}
        ''')
    
    # Template process.html
    with open(f'{template_dir}/process.html', 'w', encoding='utf-8') as f:
        f.write('''
{% extends "base.html" %}
{% block content %}
<h1>Processar Vídeos</h1>

<div class="card">
    <form method="POST">
        <div class="form-group">
            <label>Diretório dos vídeos:</label>
            <input type="text" name="directory" placeholder="/caminho/para/videos">
        </div>
        
        <div class="form-group">
            <label>
                <input type="checkbox" name="recursive" checked> Buscar em subdiretórios
            </label>
        </div>
        
        <button type="submit" class="btn">Processar</button>
    </form>
</div>

<script>
document.querySelector('form').onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    const btn = e.target.querySelector('button');
    btn.disabled = true;
    btn.textContent = 'Processando...';
    
    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
        } else {
            alert('Erro: ' + result.message);
        }
    } catch (error) {
        alert('Erro: ' + error.message);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Processar';
    }
};
</script>
{% endblock %}
        ''')
    
    # Template search.html
    with open(f'{template_dir}/search.html', 'w', encoding='utf-8') as f:
        f.write('''
{% extends "base.html" %}
{% block content %}
<h1>Buscar Vídeos</h1>

<div class="card">
    <form method="GET">
        <div class="form-group">
            <label>Busca por texto:</label>
            <input type="text" name="query" value="{{ query }}" placeholder="Digite o termo de busca">
        </div>
        
        <div class="form-group">
            <label>Categoria:</label>
            <select name="category">
                <option value="">Todas</option>
                {% for cat in categories %}
                <option value="{{ cat }}" {% if category == cat %}selected{% endif %}>{{ cat }}</option>
                {% endfor %}
            </select>
        </div>
        
        <div class="form-group">
            <label>Palavras-chave (separadas por vírgula):</label>
            <input type="text" name="keywords" value="{{ keywords }}" placeholder="sexo,educação,tecnologia">
        </div>
        
        <button type="submit" class="btn">Buscar</button>
    </form>
</div>

{% if results %}
<div class="card">
    <h2>Resultados ({{ results|length }})</h2>
    
    {% for result in results %}
    <div class="result">
        <h3>{{ result.file_name }}</h3>
        <p><strong>Categoria:</strong> {{ result.category }}</p>
        {% if result.score %}
        <p><strong>Score:</strong> {{ "%.4f"|format(result.score) }}</p>
        {% endif %}
        {% if result.confidence %}
        <p><strong>Confiança:</strong> {{ "%.2f"|format(result.confidence) }}</p>
        {% endif %}
        {% if result.matched_keywords %}
        <p><strong>Palavras encontradas:</strong> {{ result.matched_keywords|join(', ') }}</p>
        {% endif %}
        <p><strong>Contexto:</strong> {{ result.context[:200] }}{% if result.context|length > 200 %}...{% endif %}</p>
    </div>
    {% endfor %}
</div>
{% endif %}
{% endblock %}
        ''')
    
    # Template base.html
    with open(f'{template_dir}/base.html', 'w', encoding='utf-8') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>Orquestrador de Vídeos</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; }
        .container { max-width: 1200px; margin: 0 auto; }
        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 3px; border: none; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        .form-group { margin: 10px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, textarea { padding: 8px; width: 300px; border: 1px solid #ddd; border-radius: 3px; }
        .result { border-left: 4px solid #007bff; padding: 15px; margin: 10px 0; background: #f8f9fa; }
        .nav { background: #343a40; padding: 15px 0; margin-bottom: 20px; }
        .nav a { color: white; text-decoration: none; margin: 0 20px; font-weight: bold; }
        .nav a:hover { color: #ccc; }
        h1, h2, h3 { color: #333; }
    </style>
</head>
<body>
    <div class="nav">
        <div class="container">
            <a href="/">🏠 Início</a>
            <a href="/process">⚙️ Processar</a>
            <a href="/search">🔍 Buscar</a>
        </div>
    </div>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
        ''')
    
    print("Interface web iniciando em http://localhost:5000")
    app.run(debug=True, port=5000)
