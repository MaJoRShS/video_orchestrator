@echo off
REM Script automatizado de instalação das dependências do Python
REM Execute este arquivo depois de instalar o Python 3.11

echo ===================================
echo  INSTALACAO AUTOMATICA PYTHON
echo ===================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python nao encontrado!
    echo Instale o Python 3.11 primeiro seguindo o guia PYTHON_INSTALLATION_GUIDE.md
    pause
    exit /b 1
)

echo ✅ Python encontrado:
python --version
echo.

REM Verificar se pip está funcionando
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Pip nao encontrado!
    echo Reinstale o Python marcando a opcao 'Add to PATH'
    pause
    exit /b 1
)

echo ✅ Pip encontrado:
pip --version
echo.

REM Criar ambiente virtual se não existir
if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Erro ao criar ambiente virtual
        pause
        exit /b 1
    )
    echo ✅ Ambiente virtual criado
) else (
    echo ✅ Ambiente virtual já existe
)
echo.

REM Ativar ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Erro ao ativar ambiente virtual
    pause
    exit /b 1
)
echo ✅ Ambiente virtual ativado
echo.

REM Atualizar pip
echo Atualizando pip...
python -m pip install --upgrade pip setuptools wheel
echo.

REM Instalar dependências principais
echo Instalando PyTorch (CPU only)...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
echo.

echo Instalando bibliotecas de ML/AI...
pip install transformers
pip install openai-whisper
pip install scikit-learn
echo.

echo Instalando bibliotecas de processamento...
pip install opencv-python
pip install librosa
pip install moviepy
echo.

echo Instalando bibliotecas de dados...
pip install sqlalchemy
pip install numpy pandas
echo.

echo Instalando dependencias web (opcional)...
pip install flask
echo.

REM Teste final
echo ===================================
echo  TESTANDO INSTALACAO
echo ===================================
echo.

echo Testando imports básicos...
python -c "import torch; print('✅ PyTorch:', torch.__version__)"
python -c "import cv2; print('✅ OpenCV:', cv2.__version__)"
python -c "import whisper; print('✅ Whisper instalado')"
python -c "import sklearn; print('✅ Scikit-learn:', sklearn.__version__)"
python -c "import sqlalchemy; print('✅ SQLAlchemy:', sqlalchemy.__version__)"

echo.
echo ===================================
echo  INSTALACAO CONCLUIDA!
echo ===================================
echo.
echo Para usar o sistema:
echo 1. Ativar ambiente virtual: venv\Scripts\activate.bat
echo 2. Testar sistema: python test_example.py
echo 3. Processar videos: python orchestrator.py process "C:\caminho\para\videos"
echo 4. Buscar conteudo: python orchestrator.py search --query "termo"
echo.
echo Pressione qualquer tecla para continuar...
pause >nul
