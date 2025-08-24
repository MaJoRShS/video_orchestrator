#!/usr/bin/env python3
"""
Script de diagnóstico completo do Python
Identifica problemas de instalação, PATH, permissões, etc.
"""

import sys
import os
import subprocess
import platform
import site
from pathlib import Path

def print_header(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_section(title):
    print(f"\n🔍 {title}")
    print("-" * 50)

def run_command(cmd, description):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_python_installation():
    print_header("DIAGNÓSTICO COMPLETO DO PYTHON")
    
    # Informações básicas do sistema
    print_section("Sistema Operacional")
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Arquitetura: {platform.architecture()[0]}")
    print(f"Usuário: {os.getenv('USERNAME', os.getenv('USER', 'Unknown'))}")
    
    # Informações do Python
    print_section("Python - Informações Básicas")
    print(f"Versão: {sys.version}")
    print(f"Executável: {sys.executable}")
    print(f"Plataforma: {sys.platform}")
    print(f"Encoding padrão: {sys.getdefaultencoding()}")
    
    # Verificar PATH do Python
    print_section("Python no PATH")
    success, output, error = run_command("python --version", "Verificar python no PATH")
    if success:
        print(f"✅ Python no PATH: {output}")
    else:
        print(f"❌ Python não encontrado no PATH")
        print(f"Erro: {error}")
    
    success, output, error = run_command("where python", "Localizar executável python")
    if success:
        print(f"✅ Executável encontrado em: {output}")
    else:
        print(f"❌ Executável não encontrado: {error}")
    
    # Verificar pip
    print_section("Pip - Gerenciador de Pacotes")
    try:
        import pip
        print(f"✅ Pip importado: versão {pip.__version__}")
    except ImportError:
        print("❌ Pip não pode ser importado")
    
    success, output, error = run_command("pip --version", "Verificar pip no PATH")
    if success:
        print(f"✅ Pip no PATH: {output}")
    else:
        print(f"❌ Pip não encontrado no PATH: {error}")
    
    # Verificar paths importantes
    print_section("Paths e Diretórios")
    print(f"sys.path[0]: {sys.path[0]}")
    print(f"Site packages: {site.getsitepackages()}")
    print(f"User site: {site.getusersitepackages()}")
    
    # Variáveis de ambiente
    print_section("Variáveis de Ambiente")
    path_env = os.getenv('PATH', '')
    python_paths = [p for p in path_env.split(os.pathsep) if 'python' in p.lower()]
    
    if python_paths:
        print("✅ Paths do Python no PATH:")
        for p in python_paths:
            print(f"  - {p}")
    else:
        print("❌ Nenhum path do Python encontrado na variável PATH")
    
    pythonpath = os.getenv('PYTHONPATH')
    if pythonpath:
        print(f"PYTHONPATH: {pythonpath}")
    else:
        print("PYTHONPATH não definido")
    
    # Verificar permissões
    print_section("Permissões")
    python_dir = Path(sys.executable).parent
    print(f"Diretório do Python: {python_dir}")
    
    if python_dir.exists():
        print(f"✅ Diretório existe: {python_dir}")
        print(f"Permissão leitura: {os.access(python_dir, os.R_OK)}")
        print(f"Permissão escrita: {os.access(python_dir, os.W_OK)}")
        print(f"Permissão execução: {os.access(python_dir, os.X_OK)}")
    else:
        print(f"❌ Diretório não existe: {python_dir}")
    
    # Testar instalação de pacote
    print_section("Teste de Instalação de Pacotes")
    print("Testando instalação do pacote 'requests'...")
    
    # Teste 1: Instalação normal
    success, output, error = run_command("pip install requests", "Instalação normal")
    if success:
        print("✅ Instalação normal funcionou")
    else:
        print(f"❌ Instalação normal falhou: {error}")
        
        # Teste 2: Instalação como usuário
        success, output, error = run_command("pip install --user requests", "Instalação como usuário")
        if success:
            print("✅ Instalação como usuário funcionou")
        else:
            print(f"❌ Instalação como usuário falhou: {error}")
    
    # Testar importação
    print_section("Teste de Importação")
    test_packages = ['os', 'sys', 'json', 'requests', 'numpy']
    
    for package in test_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
    
    # Verificar pacotes instalados
    print_section("Pacotes Instalados (pip list)")
    success, output, error = run_command("pip list", "Listar pacotes")
    if success:
        lines = output.split('\n')[:10]  # Mostrar apenas primeiros 10
        print("Primeiros 10 pacotes instalados:")
        for line in lines:
            print(f"  {line}")
        print("  ...")
    else:
        print(f"❌ Erro ao listar pacotes: {error}")

def generate_recommendations():
    print_section("Recomendações de Correção")
    
    # Verificar se python funciona
    success, _, _ = run_command("python --version", "")
    if not success:
        print("❌ PROBLEMA: Python não encontrado no PATH")
        print("📋 SOLUÇÃO:")
        print("1. Reinstale o Python marcando 'Add to PATH'")
        print("2. Ou adicione manualmente ao PATH:")
        print("   - C:\\Python311")
        print("   - C:\\Python311\\Scripts")
        
    # Verificar se pip funciona
    success, _, _ = run_command("pip --version", "")
    if not success:
        print("\n❌ PROBLEMA: Pip não encontrado")
        print("📋 SOLUÇÃO:")
        print("1. python -m ensurepip --upgrade")
        print("2. python -m pip install --upgrade pip")
        
    # Verificar permissões
    python_dir = Path(sys.executable).parent
    if not os.access(python_dir, os.W_OK):
        print("\n❌ PROBLEMA: Sem permissão de escrita no diretório Python")
        print("📋 SOLUÇÃO:")
        print("1. Execute como administrador")
        print("2. Ou use: pip install --user <pacote>")
        print("3. Ou crie ambiente virtual")

def main():
    try:
        check_python_installation()
        generate_recommendations()
        
        print_header("RESUMO")
        print("Diagnóstico concluído!")
        print("\nSe encontrou problemas:")
        print("1. Consulte o arquivo PYTHON_INSTALLATION_GUIDE.md")
        print("2. Execute install_dependencies.bat após corrigir Python")
        print("3. Ou peça ajuda com as informações acima")
        
    except Exception as e:
        print(f"\n❌ Erro durante diagnóstico: {e}")
        print("Isso pode indicar problemas graves na instalação do Python")

if __name__ == "__main__":
    main()
