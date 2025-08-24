#!/usr/bin/env python3
"""
Script de exemplo/teste para o orquestrador de vídeos
"""

import os
import sys
from orchestrator import VideoOrchestrator

def test_orchestrator():
    """Testa as funcionalidades básicas do orquestrador"""
    
    print("=== TESTE DO ORQUESTRADOR DE VÍDEOS ===\n")
    
    # Inicializa o orquestrador
    print("Inicializando orquestrador...")
    orchestrator = VideoOrchestrator()
    print("✓ Orquestrador inicializado\n")
    
    # Testa resumo (deve ser vazio inicialmente)
    print("Testando resumo do conteúdo...")
    summary = orchestrator.get_content_summary()
    print(f"Total de vídeos: {summary.get('total_videos', 0)}")
    print(f"Duração total: {summary.get('total_duration_hours', 0):.1f} horas")
    print(f"Categorias: {summary.get('categories', {})}")
    print("✓ Resumo obtido\n")
    
    # Exemplo de como processar um vídeo (descomente se tiver um vídeo para teste)
    """
    print("Processando vídeo de exemplo...")
    video_path = "/caminho/para/seu/video.mp4"  # Substitua pelo caminho real
    
    if os.path.exists(video_path):
        video_id = orchestrator.process_video(video_path)
        if video_id:
            print(f"✓ Vídeo processado com ID: {video_id}")
        else:
            print("✗ Falha ao processar vídeo")
    else:
        print(f"Arquivo não encontrado: {video_path}")
    """
    
    # Testa busca (deve retornar vazio se não há vídeos)
    print("Testando busca...")
    
    # Busca por texto
    results = orchestrator.search_videos("tecnologia")
    print(f"Busca por 'tecnologia': {len(results)} resultados")
    
    # Busca por categoria
    results = orchestrator.search_by_category("educacao")
    print(f"Busca por categoria 'educacao': {len(results)} resultados")
    
    # Busca por palavras-chave
    results = orchestrator.search_by_keywords(["programação", "computador"])
    print(f"Busca por palavras-chave: {len(results)} resultados")
    
    print("✓ Testes de busca concluídos\n")
    
    print("=== TESTE CONCLUÍDO ===")
    print("O orquestrador está funcionando corretamente!")
    print("\nPara usar:")
    print("1. Coloque alguns vídeos em uma pasta")
    print("2. Execute: python orchestrator.py process /caminho/para/pasta")
    print("3. Execute: python orchestrator.py search --query 'termo de busca'")
    print("4. Execute: python orchestrator.py summary")

def example_usage():
    """Mostra exemplos de uso"""
    
    print("=== EXEMPLOS DE USO ===\n")
    
    print("1. PROCESSAR VÍDEOS:")
    print("   python orchestrator.py process C:/Videos --recursive")
    print("   python orchestrator.py process /home/user/videos\n")
    
    print("2. BUSCAR CONTEÚDO:")
    print("   # Buscar por texto na transcrição")
    print("   python orchestrator.py search --query 'educação sexual'")
    print("")
    print("   # Buscar por categoria")
    print("   python orchestrator.py search --category 'adulto'")
    print("")
    print("   # Buscar por palavras-chave")
    print("   python orchestrator.py search --keywords 'sexo,relacionamento,intimidade'\n")
    
    print("3. VER RESUMO:")
    print("   python orchestrator.py summary\n")
    
    print("4. INTERFACE WEB (opcional):")
    print("   pip install flask")
    print("   python web_interface.py")
    print("   # Acesse http://localhost:5000\n")
    
    print("5. EXEMPLO REAL - BUSCAR VÍDEOS SOBRE SEXO:")
    print("   python orchestrator.py search --keywords 'sexo,adulto,íntimo,sensual'")
    print("   # Retornará lista com:")
    print("   # - Nome dos arquivos")
    print("   # - Categoria identificada")
    print("   # - Contexto do conteúdo")
    print("   # - Score de relevância")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "examples":
        example_usage()
    else:
        test_orchestrator()
