#!/usr/bin/env python3
"""
Script para testar se todas as dependências estão funcionando corretamente
"""

def test_import(module_name, package_name=None):
    """Testa se um módulo pode ser importado"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        print(f"✓ {package_name} - OK")
        return True
    except ImportError as e:
        print(f"✗ {package_name} - ERRO: {e}")
        return False

def main():
    print("=== Teste de Dependências - Orquestrador de Vídeos ===\n")
    
    # Lista de dependências para testar
    dependencies = [
        ("torch", "PyTorch"),
        ("torchaudio", "TorchAudio"),
        ("transformers", "Transformers"),
        ("cv2", "OpenCV"),
        ("librosa", "Librosa"),
        ("sqlalchemy", "SQLAlchemy"),
        ("whisper", "OpenAI Whisper"),
        ("moviepy", "MoviePy"),
        ("sklearn", "Scikit-learn"),
        ("numpy", "NumPy"),
        ("pandas", "Pandas")
    ]
    
    print("Testando dependências...\n")
    
    failed_imports = []
    successful_imports = []
    
    for module, package in dependencies:
        if test_import(module, package):
            successful_imports.append(package)
        else:
            failed_imports.append(package)
    
    print(f"\n=== RESUMO DOS TESTES ===")
    print(f"Dependências funcionando: {len(successful_imports)}/{len(dependencies)}")
    
    if failed_imports:
        print(f"Dependências com problemas: {len(failed_imports)}")
        print("Pacotes que falharam:")
        for package in failed_imports:
            print(f"  - {package}")
        print("\nPara corrigir, execute:")
        print("python install_dependencies.py")
    else:
        print("✓ Todas as dependências estão funcionando corretamente!")
        print("\nO orquestrador está pronto para uso:")
        print("python orchestrator.py process /caminho/para/videos")
        print("python orchestrator.py search --query 'seu termo de busca'")
        print("python orchestrator.py summary")

if __name__ == "__main__":
    main()
