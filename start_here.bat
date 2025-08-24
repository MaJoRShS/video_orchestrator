@echo off
REM SCRIPT DE INÍCIO - ORQUESTRADOR DE VÍDEOS
REM Execute este arquivo primeiro para verificar e configurar tudo

title Orquestrador de Videos - Configuracao Inicial
color 0A

echo.
echo   ███████████████████████████████████████████████
echo   ██                                           ██
echo   ██    ORQUESTRADOR DE IAs PARA VIDEOS        ██
echo   ██    Configuracao e Instalacao Inicial      ██
echo   ██                                           ██
echo   ███████████████████████████████████████████████
echo.

REM Verificar se Python está instalado
echo 🔍 Verificando instalacao do Python...
python --version >nul 2>&1

if %errorlevel% neq 0 (
    echo.
    echo ❌ PYTHON NAO ENCONTRADO!
    echo.
    echo 📋 ACOES NECESSARIAS:
    echo 1. Baixe Python 3.11 de: https://www.python.org/downloads/
    echo 2. Durante instalacao, marque "Add Python to PATH"  
    echo 3. Escolha "Install for all users"
    echo 4. Execute novamente este script
    echo.
    echo 📖 Para ajuda detalhada, abra: PYTHON_INSTALLATION_GUIDE.md
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado!
python --version

REM Verificar pip
echo.
echo 🔍 Verificando pip...
pip --version >nul 2>&1

if %errorlevel% neq 0 (
    echo ❌ Pip nao encontrado! Execute o diagnostico para mais detalhes.
    echo python diagnose_python.py
    pause
    exit /b 1
)

echo ✅ Pip encontrado!
pip --version

REM Menu principal
:MENU
echo.
echo ═══════════════════════════════════════════════
echo                  MENU PRINCIPAL
echo ═══════════════════════════════════════════════
echo.
echo 1. 🔧 Instalar todas as dependencias automaticamente
echo 2. 🩺 Diagnosticar problemas do Python  
echo 3. 🧪 Testar sistema (sem instalar dependencias)
echo 4. 🚀 Usar sistema (processar videos)
echo 5. 🔍 Buscar videos ja processados
echo 6. 📊 Ver resumo do conteudo processado
echo 7. 🌐 Iniciar interface web
echo 8. 📖 Abrir guia de instalacao
echo 9. ❌ Sair
echo.
set /p choice="Escolha uma opcao (1-9): "

if "%choice%"=="1" goto INSTALL
if "%choice%"=="2" goto DIAGNOSE
if "%choice%"=="3" goto TEST
if "%choice%"=="4" goto PROCESS
if "%choice%"=="5" goto SEARCH
if "%choice%"=="6" goto SUMMARY
if "%choice%"=="7" goto WEB
if "%choice%"=="8" goto GUIDE
if "%choice%"=="9" goto EXIT

echo Opcao invalida! Tente novamente.
pause
goto MENU

:INSTALL
echo.
echo 🔧 Iniciando instalacao automatica...
call install_dependencies.bat
pause
goto MENU

:DIAGNOSE
echo.
echo 🩺 Executando diagnostico do Python...
python diagnose_python.py
pause
goto MENU

:TEST
echo.
echo 🧪 Testando sistema...
python test_example.py
pause
goto MENU

:PROCESS
echo.
echo 🚀 PROCESSAR VIDEOS
echo.
set /p video_dir="Digite o caminho da pasta com videos: "
if "%video_dir%"=="" (
    echo Caminho nao informado.
    pause
    goto MENU
)

echo.
echo Processando videos em: %video_dir%
echo (Isso pode demorar dependendo da quantidade de videos)
echo.

REM Ativar ambiente virtual se existir
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python orchestrator.py process "%video_dir%" --recursive
pause
goto MENU

:SEARCH
echo.
echo 🔍 BUSCAR VIDEOS
echo.
echo Escolha o tipo de busca:
echo 1. Busca por texto
echo 2. Busca por categoria  
echo 3. Busca por palavras-chave
echo.
set /p search_type="Opcao (1-3): "

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

if "%search_type%"=="1" (
    set /p query="Digite o termo de busca: "
    python orchestrator.py search --query "!query!"
) else if "%search_type%"=="2" (
    echo Categorias: educacao, entretenimento, noticias, esportes, tecnologia, culinaria, musica, gaming, tutorial, documentario, adulto, outros
    set /p category="Digite a categoria: "
    python orchestrator.py search --category "!category!"
) else if "%search_type%"=="3" (
    set /p keywords="Digite palavras-chave (separadas por virgula): "
    python orchestrator.py search --keywords "!keywords!"
) else (
    echo Opcao invalida.
)

pause
goto MENU

:SUMMARY
echo.
echo 📊 RESUMO DO CONTEUDO
echo.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python orchestrator.py summary
pause
goto MENU

:WEB
echo.
echo 🌐 Iniciando interface web...
echo A interface sera aberta em: http://localhost:5000
echo Pressione Ctrl+C para parar o servidor.
echo.

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

python web_interface.py
pause
goto MENU

:GUIDE
echo.
echo 📖 Abrindo guia de instalacao...
start PYTHON_INSTALLATION_GUIDE.md
goto MENU

:EXIT
echo.
echo Ate logo! 👋
echo.
exit /b 0
