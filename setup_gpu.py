#!/usr/bin/env python3
"""
Script para configurar e verificar suporte a GPU para o sistema de transcrição
"""
import subprocess
import sys
import platform

def check_gpu_info():
    """Verifica informações sobre a GPU do sistema"""
    print("🔍 Verificando informações da GPU...")
    
    try:
        # Verifica NVIDIA-SMI (para GPUs NVIDIA)
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ NVIDIA GPU detectada!")
            print(result.stdout)
            return True
        else:
            print("❌ nvidia-smi não encontrado ou falhou")
            return False
    except FileNotFoundError:
        print("❌ nvidia-smi não está instalado")
        return False

def check_current_pytorch():
    """Verifica a versão atual do PyTorch"""
    print("\n🔍 Verificando PyTorch atual...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} instalado")
        print(f"   CUDA disponível: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   Versão CUDA: {torch.version.cuda}")
            print(f"   Número de GPUs: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")
        else:
            print("   Versão CPU detectada")
        return torch.cuda.is_available()
    except ImportError:
        print("❌ PyTorch não está instalado")
        return False

def get_cuda_version():
    """Detecta a versão do CUDA instalada no sistema"""
    print("\n🔍 Detectando versão do CUDA...")
    
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout
            for line in output.split('\n'):
                if 'release' in line:
                    version = line.split('release ')[1].split(',')[0]
                    print(f"✅ CUDA {version} detectado")
                    return version
        return None
    except FileNotFoundError:
        print("❌ nvcc não encontrado")
        return None

def install_pytorch_cuda():
    """Instala PyTorch com suporte CUDA"""
    print("\n⚡ Instalando PyTorch com suporte CUDA...")
    
    # Detecta versão do CUDA
    cuda_version = get_cuda_version()
    
    # URLs para diferentes versões do CUDA
    cuda_urls = {
        "11.8": "https://download.pytorch.org/whl/cu118",
        "12.1": "https://download.pytorch.org/whl/cu121",
        "12.4": "https://download.pytorch.org/whl/cu124"
    }
    
    # Escolhe a versão mais adequada
    if cuda_version:
        if cuda_version.startswith("11.8"):
            index_url = cuda_urls["11.8"]
        elif cuda_version.startswith("12.1"):
            index_url = cuda_urls["12.1"]
        else:
            # Padrão para versões mais recentes
            index_url = cuda_urls["12.4"]
    else:
        print("⚠️ Versão CUDA não detectada, usando CUDA 12.4 como padrão")
        index_url = cuda_urls["12.4"]
    
    # Comando de instalação
    install_cmd = [
        sys.executable, "-m", "pip", "install", 
        "--upgrade", 
        "--index-url", index_url,
        "torch", "torchvision", "torchaudio"
    ]
    
    print(f"Executando: {' '.join(install_cmd)}")
    
    try:
        result = subprocess.run(install_cmd, check=True)
        print("✅ PyTorch com CUDA instalado com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na instalação: {e}")
        return False

def verify_installation():
    """Verifica se a instalação foi bem-sucedida"""
    print("\n🔍 Verificando instalação...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        
        if torch.cuda.is_available():
            print(f"✅ CUDA {torch.version.cuda} disponível")
            print(f"✅ {torch.cuda.device_count()} GPU(s) detectada(s)")
            
            # Teste simples de GPU
            device = torch.device('cuda:0')
            x = torch.randn(3, 3).to(device)
            y = torch.randn(3, 3).to(device)
            z = torch.mm(x, y)
            print("✅ Teste de operação GPU bem-sucedido")
            
            return True
        else:
            print("❌ CUDA não está disponível após instalação")
            return False
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

def main():
    print("🚀 Configuração de GPU para Video Orchestrator")
    print("=" * 50)
    
    # Verifica se há GPU NVIDIA
    has_nvidia_gpu = check_gpu_info()
    
    if not has_nvidia_gpu:
        print("\n⚠️ GPU NVIDIA não detectada.")
        print("   O sistema continuará usando CPU.")
        print("   Para usar GPU, instale uma GPU NVIDIA compatível.")
        return
    
    # Verifica PyTorch atual
    has_cuda_pytorch = check_current_pytorch()
    
    if has_cuda_pytorch:
        print("\n✅ PyTorch com CUDA já está configurado!")
        print("   O sistema já pode usar GPU.")
        return
    
    # Pergunta se quer instalar
    response = input("\n❓ Deseja instalar PyTorch com suporte CUDA? (s/n): ").lower()
    
    if response in ['s', 'sim', 'y', 'yes']:
        if install_pytorch_cuda():
            verify_installation()
            print("\n🎉 Configuração concluída!")
            print("   Reinicie o Python para usar as novas dependências.")
        else:
            print("\n❌ Falha na instalação. Verifique os logs acima.")
    else:
        print("\n⏭️ Instalação cancelada pelo usuário.")

if __name__ == "__main__":
    main()
