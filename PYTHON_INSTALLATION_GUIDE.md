# 🐍 Guia Completo: Instalação e Configuração do Python no Windows

## 🚨 PROBLEMAS COMUNS QUE VAMOS RESOLVER:
- ❌ Problemas de permissão de execução
- ❌ Conflitos de versões do Python
- ❌ PATH não configurado corretamente
- ❌ Pip não funcionando
- ❌ Bibliotecas não instalando

---

## 📋 PASSO 1: LIMPEZA COMPLETA (OPCIONAL MAS RECOMENDADO)

### 1.1 Desinstalar Versões Antigas:
```cmd
# Vá em: Configurações > Aplicativos > Python
# Desinstale TODAS as versões do Python encontradas
```

### 1.2 Limpar Variáveis de Ambiente:
1. Pressione `Win + R` → digite `sysdm.cpl` → Enter
2. Clique em "Variáveis de Ambiente"
3. Em "Variáveis do usuário" e "Variáveis do sistema":
   - Procure por `PATH`
   - Remova TODAS as entradas relacionadas ao Python
   - Procure por `PYTHONPATH` e delete se existir

### 1.3 Remover Pastas Residuais:
```bash
# No Git Bash ou PowerShell
rm -rf /c/Users/lukas/AppData/Local/Programs/Python*
rm -rf /c/Users/lukas/AppData/Roaming/Python*
rm -rf /c/Python*
```

---

## 📥 PASSO 2: DOWNLOAD E INSTALAÇÃO LIMPA

### 2.1 Download da Versão Recomendada:
- Acesse: https://www.python.org/downloads/
- Baixe **Python 3.11.x** (versão estável e compatível)
- ⚠️ **IMPORTANTE**: Baixe a versão "Windows installer (64-bit)"

### 2.2 Instalação Correta:

#### Opção A: Instalação Para Usuário (RECOMENDADA)
```
1. Execute o instalador como USUÁRIO NORMAL (não como administrador)
2. ✅ Marque "Add Python to PATH" 
3. ✅ Marque "Install for all users" (se aparecer)
4. Clique em "Customize installation"
5. ✅ Marque TODAS as opções na primeira tela
6. Na segunda tela:
   ✅ Install for all users
   ✅ Add Python to environment variables  
   ✅ Precompile standard library
   ✅ Download debugging symbols
   📁 Mude o local para: C:\Python311
7. Clique "Install"
```

#### Opção B: Se Opção A Não Funcionar
```
1. Execute o instalador como ADMINISTRADOR
2. ✅ Marque "Add Python to PATH"
3. Escolha instalação customizada
4. Local: C:\Python311
5. ✅ Marque "Install for all users"
```

---

## ⚙️ PASSO 3: VERIFICAÇÃO E CONFIGURAÇÃO

### 3.1 Verificar Instalação:
```bash
# Abra um NOVO terminal (Git Bash, PowerShell ou CMD)
python --version
# Deve mostrar: Python 3.11.x

pip --version  
# Deve mostrar a versão do pip

which python
# Deve mostrar: /c/Python311/python.exe ou similar
```

### 3.2 Se Não Funcionar, Configure o PATH Manualmente:

#### No PowerShell (como Administrador):
```powershell
# Adicionar ao PATH do sistema
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Python311;C:\Python311\Scripts", [EnvironmentVariableTarget]::Machine)

# Recarregar variáveis
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

#### Ou Configure via Interface:
```
1. Win + R → sysdm.cpl → Enter
2. Variáveis de Ambiente
3. Em "Variáveis do sistema", selecione PATH → Editar
4. Adicione essas linhas:
   C:\Python311
   C:\Python311\Scripts
5. OK → OK → OK
6. Reinicie o terminal
```

---

## 🔧 PASSO 4: CONFIGURAÇÃO AVANÇADA

### 4.1 Atualizar Pip:
```bash
python -m pip install --upgrade pip
```

### 4.2 Configurar Pip para Usuário (Evita problemas de permissão):
```bash
# Criar diretório para configuração
mkdir -p /c/Users/lukas/pip

# Criar arquivo de configuração
cat > /c/Users/lukas/pip/pip.conf << EOF
[global]
user = true
break-system-packages = true
trusted-host = pypi.org
               pypi.python.org
               files.pythonhosted.org
EOF
```

### 4.3 Configurar Variáveis Adicionais:
```bash
# Adicionar ao seu .bashrc ou .bash_profile
echo 'export PYTHONUSERBASE="/c/Users/lukas/AppData/Roaming/Python/Python311"' >> ~/.bashrc
echo 'export PATH="$PATH:/c/Users/lukas/AppData/Roaming/Python/Python311/Scripts"' >> ~/.bashrc
source ~/.bashrc
```

---

## 🧪 PASSO 5: TESTE COMPLETO

### 5.1 Script de Teste:
```bash
cd /c/Users/lukas/video_orchestrator

# Criar script de teste
cat > test_python.py << 'EOF'
#!/usr/bin/env python3
import sys
import subprocess
import os

def test_python_installation():
    print("=== TESTE DE INSTALAÇÃO DO PYTHON ===\n")
    
    # Versão do Python
    print(f"Python versão: {sys.version}")
    print(f"Executável: {sys.executable}")
    print(f"PATH: {sys.path[0]}")
    print()
    
    # Teste do pip
    try:
        import pip
        print(f"✅ Pip instalado: {pip.__version__}")
    except ImportError:
        print("❌ Pip não encontrado")
    
    # Teste de instalação de pacote
    print("\nTestando instalação de pacote...")
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--user", "requests"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Instalação de pacotes funcionando")
        else:
            print(f"❌ Erro na instalação: {result.stderr}")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # Teste de importação
    try:
        import requests
        print("✅ Importação funcionando")
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
    
    print("\n=== TESTE CONCLUÍDO ===")

if __name__ == "__main__":
    test_python_installation()
EOF

# Executar teste
python test_python.py
```

---

## 🛠️ PASSO 6: INSTALAÇÃO DAS DEPENDÊNCIAS DO PROJETO

### 6.1 Criar Ambiente Virtual (RECOMENDADO):
```bash
cd /c/Users/lukas/video_orchestrator

# Criar ambiente virtual
python -m venv venv

# Ativar (Git Bash)
source venv/Scripts/activate

# Ativar (PowerShell)
# venv\Scripts\Activate.ps1

# Ativar (CMD)  
# venv\Scripts\activate.bat
```

### 6.2 Instalar Dependências:
```bash
# Com ambiente virtual ativado
pip install --upgrade pip setuptools wheel

# Instalar dependências principais
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers
pip install opencv-python
pip install librosa
pip install sqlalchemy
pip install openai-whisper
pip install moviepy
pip install scikit-learn
pip install numpy pandas
pip install flask  # Para interface web opcional

# Ou usar o arquivo requirements.txt
pip install -r requirements.txt
```

### 6.3 Teste Final do Projeto:
```bash
# Com ambiente virtual ativado
python test_example.py
```

---

## 🚨 SOLUÇÃO DE PROBLEMAS COMUNS

### Problema: "python não é reconhecido"
**Solução:**
```bash
# Reiniciar terminal completamente
# Verificar PATH
echo $PATH | grep -i python

# Se não aparecer, adicionar manualmente
export PATH="/c/Python311:/c/Python311/Scripts:$PATH"
```

### Problema: "Permission denied" ao instalar pacotes
**Solução:**
```bash
# Instalar no modo usuário
pip install --user nome_do_pacote

# Ou usar ambiente virtual
python -m venv venv
source venv/Scripts/activate
pip install nome_do_pacote
```

### Problema: "Microsoft Visual C++ 14.0 is required"
**Solução:**
```bash
# Baixar e instalar:
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Ou instalar versões pré-compiladas
pip install --only-binary=all nome_do_pacote
```

### Problema: OpenCV não funciona
**Solução:**
```bash
pip uninstall opencv-python opencv-python-headless
pip install opencv-python-headless
# Ou
pip install opencv-contrib-python
```

---

## 🎯 SCRIPT AUTOMATIZADO DE INSTALAÇÃO

```bash
#!/bin/bash
# save as install_python_dependencies.sh

echo "=== INSTALAÇÃO AUTOMÁTICA DAS DEPENDÊNCIAS ==="

# Verificar se Python está instalado
if ! command -v python &> /dev/null; then
    echo "❌ Python não encontrado. Instale primeiro seguindo o guia."
    exit 1
fi

echo "✅ Python encontrado: $(python --version)"

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "Criando ambiente virtual..."
    python -m venv venv
fi

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source venv/Scripts/activate

# Atualizar pip
echo "Atualizando pip..."
python -m pip install --upgrade pip setuptools wheel

# Instalar dependências
echo "Instalando dependências..."
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers opencv-python librosa sqlalchemy
pip install openai-whisper moviepy scikit-learn numpy pandas flask

echo "✅ Instalação concluída!"
echo "Para ativar o ambiente virtual: source venv/Scripts/activate"
echo "Para testar: python test_example.py"
```

---

## ✅ CHECKLIST FINAL

- [ ] Python 3.11.x instalado
- [ ] `python --version` funciona
- [ ] `pip --version` funciona  
- [ ] PATH configurado corretamente
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] `python test_example.py` executa sem erro
- [ ] `python orchestrator.py --help` mostra ajuda

**Se todos os itens estão ✅, seu Python está configurado corretamente!**
