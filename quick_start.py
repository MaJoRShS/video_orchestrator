#!/usr/bin/env python3
"""
Script de inicialização rápida do orquestrador de vídeos
"""

import os
import sys
import subprocess

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    print("Verificando dependências...")
    
    required_packages = [
        'torch', 'transformers', 'opencv-python', 'whisper', 
        'moviepy', 'sqlalchemy', 'scikit-learn', 'numpy', 'pandas'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (não instalado)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nPacotes faltando: {', '.join(missing_packages)}")
        print("Execute: python install_dependencies.py")
        return False
    
    print("✓ Todas as dependências estão instaladas!")
    return True

def quick_demo():
    """Demonstração rápida do sistema"""
    
    print("\n=== DEMONSTRAÇÃO RÁPIDA ===\n")
    
    # Solicita diretório de vídeos
    video_dir = input("Digite o caminho do diretório com vídeos (ou ENTER para pular): ").strip()
    
    if video_dir and os.path.exists(video_dir):
        print(f"\nProcessando vídeos em: {video_dir}")
        
        # Executa o processamento
        cmd = [sys.executable, "orchestrator.py", "process", video_dir, "--recursive"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print("Saída do processamento:")
            print(result.stdout)
            
            if result.stderr:
                print("Erros/Avisos:")
                print(result.stderr)
                
        except Exception as e:
            print(f"Erro ao executar processamento: {e}")
            return
        
        # Mostra resumo
        print("\n" + "="*50)
        print("RESUMO DO CONTEÚDO PROCESSADO")
        print("="*50)
        
        cmd = [sys.executable, "orchestrator.py", "summary"]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"Erro ao obter resumo: {e}")
        
        # Exemplo de busca
        print("\n" + "="*50)
        print("EXEMPLO DE BUSCA")
        print("="*50)
        
        search_term = input("\nDigite um termo para buscar (ou ENTER para pular): ").strip()
        
        if search_term:
            cmd = [sys.executable, "orchestrator.py", "search", "--query", search_term]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                print(f"Resultados para '{search_term}':")
                print(result.stdout)
            except Exception as e:
                print(f"Erro na busca: {e}")
    
    else:
        print("Diretório não especificado ou não existe. Pulando processamento...")
    
    print("\n" + "="*50)
    print("COMANDOS ÚTEIS")
    print("="*50)
    print("Processar vídeos:")
    print("  python orchestrator.py process /caminho/para/videos --recursive")
    print()
    print("Buscar conteúdo:")
    print("  python orchestrator.py search --query 'termo de busca'")
    print("  python orchestrator.py search --category 'adulto'") 
    print("  python orchestrator.py search --keywords 'sexo,educação'")
    print()
    print("Ver resumo:")
    print("  python orchestrator.py summary")
    print()
    print("Interface web (opcional):")
    print("  pip install flask")
    print("  python web_interface.py")
    print("  # Acesse http://localhost:5000")

def main():
    print("=== ORQUESTRADOR DE IAs PARA ANÁLISE DE VÍDEOS ===")
    print("Sistema de transcrição, análise e categorização automática")
    print()
    
    # Verifica dependências
    if not check_dependencies():
        print("\nInstale as dependências primeiro e tente novamente.")
        return
    
    # Menu de opções
    print("\nOpções:")
    print("1. Demonstração rápida")
    print("2. Ver exemplos de uso")
    print("3. Instalar dependências")
    print("4. Teste do sistema")
    print("5. Sair")
    
    choice = input("\nEscolha uma opção (1-5): ").strip()
    
    if choice == "1":
        quick_demo()
    
    elif choice == "2":
        subprocess.run([sys.executable, "test_example.py", "examples"])
    
    elif choice == "3":
        subprocess.run([sys.executable, "install_dependencies.py"])
    
    elif choice == "4":
        subprocess.run([sys.executable, "test_example.py"])
    
    elif choice == "5":
        print("Até logo!")
        return
    
    else:
        print("Opção inválida!")

if __name__ == "__main__":
    main()
