#!/usr/bin/env python3
"""
Script para testar a configuração de GPU do sistema de transcrição
"""
import sys
import os

# Adiciona o diretório atual ao path para importar módulos locais
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_gpu_configuration():
    """Testa a configuração de GPU do sistema"""
    print("🧪 Testando configuração de GPU do Video Orchestrator")
    print("=" * 60)
    
    # 1. Teste de importações básicas
    print("\n1️⃣ Testando importações...")
    try:
        import torch
        print(f"   ✅ PyTorch {torch.__version__}")
        
        import whisper
        print(f"   ✅ OpenAI Whisper importado")
        
        import config
        print(f"   ✅ Configurações locais importadas")
        
    except ImportError as e:
        print(f"   ❌ Erro de importação: {e}")
        return False
    
    # 2. Teste de detecção de GPU
    print("\n2️⃣ Testando detecção de GPU...")
    cuda_available = torch.cuda.is_available()
    print(f"   CUDA disponível: {'✅' if cuda_available else '❌'} {cuda_available}")
    
    if cuda_available:
        print(f"   Versão CUDA: {torch.version.cuda}")
        print(f"   Número de GPUs: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"   GPU {i}: {torch.cuda.get_device_name(i)}")
    
    # 3. Teste de configuração
    print("\n3️⃣ Testando configuração local...")
    print(f"   USE_GPU configurado: {'✅' if config.USE_GPU else '❌'} {config.USE_GPU}")
    print(f"   GPU_DEVICE: {config.GPU_DEVICE}")
    print(f"   WHISPER_MODEL: {config.WHISPER_MODEL}")
    
    # 4. Teste do TranscriptionEngine
    print("\n4️⃣ Testando TranscriptionEngine...")
    try:
        from transcription import TranscriptionEngine
        
        print("   Criando instância do TranscriptionEngine...")
        engine = TranscriptionEngine()
        
        print(f"   Dispositivo selecionado: {engine.device}")
        print(f"   Modelo carregado: {'✅' if engine.model else '❌'}")
        
        # Teste de carregamento do modelo
        if hasattr(engine.model, 'device'):
            print(f"   Modelo está em: {engine.model.device}")
        
        print("   ✅ TranscriptionEngine inicializado com sucesso")
        
    except Exception as e:
        print(f"   ❌ Erro ao inicializar TranscriptionEngine: {e}")
        return False
    
    # 5. Verificação de compatibilidade
    print("\n5️⃣ Verificação de compatibilidade...")
    
    expected_device = "cpu"
    if config.USE_GPU and cuda_available:
        try:
            device = torch.device(config.GPU_DEVICE)
            torch.cuda.get_device_properties(device)
            expected_device = config.GPU_DEVICE
        except:
            expected_device = "cpu"
    
    actual_device = engine.device
    
    if actual_device == expected_device:
        print(f"   ✅ Dispositivo configurado corretamente: {actual_device}")
    else:
        print(f"   ⚠️ Dispositivo diferente do esperado:")
        print(f"      Esperado: {expected_device}")
        print(f"      Atual: {actual_device}")
    
    # 6. Resumo final
    print("\n📊 RESUMO DA CONFIGURAÇÃO")
    print("-" * 30)
    
    if cuda_available and config.USE_GPU and actual_device != "cpu":
        print("🚀 STATUS: GPU HABILITADA")
        print(f"   Dispositivo: {actual_device}")
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print("   ⚡ Transcrições serão processadas na GPU (mais rápido)")
    else:
        print("🐌 STATUS: CPU SENDO USADA")
        if not cuda_available:
            print("   Motivo: CUDA não disponível")
        elif not config.USE_GPU:
            print("   Motivo: USE_GPU = False na configuração")
        else:
            print("   Motivo: Fallback para CPU por erro na GPU")
        print("   📝 Transcrições serão processadas na CPU (mais lento)")
    
    print(f"\n💡 Para alterar configurações, edite o arquivo: config.py")
    return True

def main():
    success = test_gpu_configuration()
    
    if not success:
        print("\n❌ Teste falhou. Verifique as dependências e configurações.")
        sys.exit(1)
    else:
        print("\n✅ Teste concluído com sucesso!")

if __name__ == "__main__":
    main()
