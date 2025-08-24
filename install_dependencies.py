#!/usr/bin/env python3
"""
Script para instalação automática das dependências do orquestrador de vídeos
"""

import subprocess
import sys
import os

def install_package(package):
    """Instala um pacote usando pip com --user para evitar problemas de permissões"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package])
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("=== Instalador de Dependências - Orquestrador de Vídeos ===\n")
    
    # Lista de dependências necessárias
    dependencies = [
        "torch",
        "torchaudio", 
        "transformers",
        "opencv-python",
        "librosa",
        "sqlalchemy",
        "openai-whisper",
        "moviepy",
        "scikit-learn",
        "numpy",
        "pandas"
    ]
    
    print(f"Instalando {len(dependencies)} dependências...\n")
    
    failed_packages = []
    
    for i, package in enumerate(dependencies, 1):
        print(f"[{i}/{len(dependencies)}] Instalando {package}...")
        
        if install_package(package):
            print(f"✓ {package} instalado com sucesso")
        else:
            print(f"✗ Falha ao instalar {package}")
            failed_packages.append(package)
        
        print()
    
    # Resumo final
    print("=== RESUMO DA INSTALAÇÃO ===")
    print(f"Pacotes instalados com sucesso: {len(dependencies) - len(failed_packages)}")
    
    if failed_packages:
        print(f"Pacotes com falha: {len(failed_packages)}")
        print("Pacotes que falharam:")
        for package in failed_packages:
            print(f"  - {package}")
        print("\nTente instalar manualmente os pacotes que falharam:")
        print(f"pip install {' '.join(failed_packages)}")
    else:
        print("✓ Todas as dependências foram instaladas com sucesso!")
    
    print("\nPara usar o orquestrador:")
    print("python orchestrator.py process /caminho/para/videos")
    print("python orchestrator.py search --query 'seu termo de busca'")
    print("python orchestrator.py summary")

if __name__ == "__main__":
    main()
