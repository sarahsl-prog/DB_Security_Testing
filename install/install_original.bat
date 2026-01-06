@echo off
REM ###########################################################################
REM Healthcare Security Research API - Installation Script (Windows)
REM
REM This script interactively configures the application by:
REM - Collecting host IP addresses and configuration settings
REM - Generating secure secret keys
REM - Creating .env files for both backend and frontend
REM - Setting up required directories
REM
REM Usage:
REM   install.bat
REM ###########################################################################

setlocal enabledelayedexpansion

REM Colors (using ANSI escape codes if supported)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "CYAN=[96m"
set "MAGENTA=[95m"
set "NC=[0m"

REM Script configuration
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"

REM ###########################################################################
REM Main Installation Flow
REM ###########################################################################

cls
call :print_banner

REM Check prerequisites
call :check_prerequisites
if errorlevel 1 goto :error_exit

REM Collect configuration from user
call :collect_configuration

REM Display summary and confirm
call :display_summary
if errorlevel 1 goto :cancelled_exit

REM Create configuration files
echo.
echo ========================================
echo Creating Configuration Files
echo ========================================
echo.
call :create_backend_env
call :create_frontend_env

REM Create directories
call :create_directories

REM Display next steps
call :display_next_steps

goto :end

REM ###########################################################################
REM Helper Functions
REM ###########################################################################

:print_banner
echo ================================================================
echo    Healthcare Security Research Platform - Installation
echo    Interactive Configuration Setup
echo ================================================================
echo.
goto :eof

:print_success
echo [92m[OK][0m %~1
goto :eof

:print_error
echo [91m[ERROR][0m %~1
goto :eof

:print_warning
echo [93m[WARNING][0m %~1
goto :eof

:print_info
echo [94m[INFO][0m %~1
goto :eof

:check_prerequisites
echo ========================================
echo Checking Prerequisites
echo ========================================
echo.

set "prereq_ok=1"

REM Check Python
where python >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    call :print_success "Python installed: !PYTHON_VERSION!"
) else (
    call :print_error "Python not found. Please install Python 3.8 or higher."
    set "prereq_ok=0"
)

REM Check if directories exist
if exist "%BACKEND_DIR%" (
    call :print_success "Backend directory found"
) else (
    call :print_error "Backend directory not found: %BACKEND_DIR%"
    set "prereq_ok=0"
)

if exist "%FRONTEND_DIR%" (
    call :print_success "Frontend directory found"
) else (
    call :print_error "Frontend directory not found: %FRONTEND_DIR%"
    set "prereq_ok=0"
)

echo.

if "%prereq_ok%"=="0" (
    call :print_error "Prerequisites check failed. Please fix the issues above."
    exit /b 1
)

exit /b 0

:collect_configuration
echo ========================================
echo Configuration Wizard
echo ========================================
echo.
echo This wizard will guide you through configuring the application.
echo Press Enter to accept default values shown in brackets [default].
echo.

REM Backend/Frontend Host
echo [?] What is the IP address where the backend API will run?
echo [INFO] This is typically the IP of the machine running the Flask backend.
set "default_backend_host=192.168.100.20"
set /p "BACKEND_HOST=[?] Backend API Host [!default_backend_host!]: "
if "!BACKEND_HOST!"=="" set "BACKEND_HOST=!default_backend_host!"

REM Backend Port
echo.
echo [?] What port should the backend API listen on?
set "default_backend_port=5000"
set /p "BACKEND_PORT=[?] Backend API Port [!default_backend_port!]: "
if "!BACKEND_PORT!"=="" set "BACKEND_PORT=!default_backend_port!"

REM Database Host
echo.
echo [?] What is the IP address of your PostgreSQL database server?
set "default_db_host=192.168.100.30"
set /p "DB_HOST=[?] Database Host [!default_db_host!]: "
if "!DB_HOST!"=="" set "DB_HOST=!default_db_host!"

REM Database Port
echo.
echo [?] What port is PostgreSQL running on?
set "default_db_port=5432"
set /p "DB_PORT=[?] Database Port [!default_db_port!]: "
if "!DB_PORT!"=="" set "DB_PORT=!default_db_port!"

REM Database Name
echo.
echo [?] What is the name of your PostgreSQL database?
set "default_db_name=healthcare_security"
set /p "DB_NAME=[?] Database Name [!default_db_name!]: "
if "!DB_NAME!"=="" set "DB_NAME=!default_db_name!"

REM Database User
echo.
echo [?] What is the PostgreSQL username?
set "default_db_user=healthcare_user"
set /p "DB_USER=[?] Database User [!default_db_user!]: "
if "!DB_USER!"=="" set "DB_USER=!default_db_user!"

REM Database Password
echo.
echo [?] What is the PostgreSQL password?
set /p "DB_PASSWORD=[?] Database Password: "

REM LLM Host
echo.
echo [?] What is the IP address of your Ollama LLM service?
set "default_llm_host=192.168.100.1"
set /p "LLM_HOST=[?] LLM Service Host [!default_llm_host!]: "
if "!LLM_HOST!"=="" set "LLM_HOST=!default_llm_host!"

REM LLM Port
echo.
echo [?] What port is Ollama running on?
set "default_llm_port=11434"
set /p "LLM_PORT=[?] LLM Service Port [!default_llm_port!]: "
if "!LLM_PORT!"=="" set "LLM_PORT=!default_llm_port!"

REM LLM Model
echo.
echo [?] What Ollama model should be used?
set "default_llm_model=llama3.1-sql:latest"
set /p "LLM_MODEL=[?] LLM Model [!default_llm_model!]: "
if "!LLM_MODEL!"=="" set "LLM_MODEL=!default_llm_model!"

REM Email Domain
echo.
echo [?] What domain should be used for user email addresses?
echo [INFO] Example: hospital.com will create emails like admin@hospital.com
set "default_email_domain=hospital.com"
set /p "EMAIL_DOMAIN=[?] Email Domain [!default_email_domain!]: "
if "!EMAIL_DOMAIN!"=="" set "EMAIL_DOMAIN=!default_email_domain!"

REM Security Mode
echo.
echo [?] Which security mode would you like to start with?
echo [INFO]   1. vulnerable - Demonstrates security vulnerabilities (for research)
echo [INFO]   2. secure     - All security features enabled
set /p "security_choice=[?] Select mode (1 or 2) [1]: "
if "!security_choice!"=="" set "security_choice=1"
if "!security_choice!"=="1" set "SECURITY_MODE=vulnerable"
if "!security_choice!"=="2" set "SECURITY_MODE=secure"

REM Generate secret keys
echo.
echo [INFO] Generating secure secret keys...
call :generate_secret_key SECRET_KEY
call :generate_secret_key JWT_SECRET_KEY
call :print_success "Secure keys generated"

goto :eof

:generate_secret_key
REM Generate a secure random key using Python
for /f "tokens=*" %%i in ('python -c "import secrets; print(secrets.token_urlsafe(32))" 2^>nul') do (
    set "%~1=%%i"
    goto :eof
)
REM Fallback if Python method fails
set "%~1=change_this_in_production_%RANDOM%%RANDOM%%RANDOM%"
goto :eof

:display_summary
echo.
echo ========================================
echo Configuration Summary
echo ========================================
echo.
echo Network Configuration:
echo   Backend API:        %BACKEND_HOST%:%BACKEND_PORT%
echo   Database Server:    %DB_HOST%:%DB_PORT%
echo   LLM Service:        %LLM_HOST%:%LLM_PORT%
echo.
echo Database Configuration:
echo   Database Name:      %DB_NAME%
echo   Database User:      %DB_USER%
echo   Database Password:  ***********
echo.
echo Application Configuration:
echo   Email Domain:       %EMAIL_DOMAIN%
echo   LLM Model:          %LLM_MODEL%
echo   Security Mode:      %SECURITY_MODE%
echo.

set /p "confirm=[?] Continue with this configuration? (Y/N): "
if /i not "!confirm!"=="Y" (
    call :print_warning "Installation cancelled by user."
    exit /b 1
)
exit /b 0

:create_backend_env
echo [INFO] Creating backend\.env file...

(
echo # Backend API Configuration
echo # Changed to 0.0.0.0 to bind to all network interfaces
echo # Use 127.0.0.1 for localhost only, or specific IP if needed
echo API_HOST=0.0.0.0
echo API_PORT=%BACKEND_PORT%
echo FLASK_ENV=development
echo FLASK_DEBUG=False
echo.
echo # Database Configuration
echo DB_HOST=%DB_HOST%
echo DB_PORT=%DB_PORT%
echo DB_NAME=%DB_NAME%
echo DB_USER=%DB_USER%
echo DB_PASSWORD=%DB_PASSWORD%
echo.
echo # LLM Service Configuration
echo LLM_HOST=%LLM_HOST%
echo LLM_PORT=%LLM_PORT%
echo LLM_MODEL=%LLM_MODEL%
echo LLM_TIMEOUT=30
echo LLM_MAX_RETRIES=3
echo.
echo # Security Configuration
echo SECURITY_MODE=%SECURITY_MODE%
echo SECRET_KEY=%SECRET_KEY%
echo JWT_SECRET_KEY=%JWT_SECRET_KEY%
echo JWT_EXPIRES_HOURS=24
echo.
echo # Logging Configuration
echo LOG_LEVEL=INFO
echo LOG_FILE=logs/healthcare_security.log
echo AUDIT_LOG_FILE=logs/security_audit.log
echo.
echo # CORS Configuration
echo CORS_ORIGINS=*
echo.
echo # Query and Rate Limiting
echo MAX_QUERY_RESULTS=1000
echo QUERY_TIMEOUT=30
echo RATE_LIMIT_PER_MINUTE=60
echo CACHE_TTL=300
echo.
echo # Domain Configuration
echo EMAIL_DOMAIN=%EMAIL_DOMAIN%
echo API_BASE_URL=http://%BACKEND_HOST%:%BACKEND_PORT%
echo.
echo # Development Environment
echo DEVELOPMENT_DB_HOST=%DB_HOST%
echo DEVELOPMENT_LLM_HOST=%LLM_HOST%
echo.
echo # Testing Environment
echo TESTING_DB_HOST=%DB_HOST%
echo TESTING_LLM_HOST=%LLM_HOST%
echo TESTING_API_URL=http://localhost:%BACKEND_PORT%
) > "%BACKEND_DIR%\.env"

if exist "%BACKEND_DIR%\.env" (
    call :print_success "Backend .env file created"
) else (
    call :print_error "Failed to create backend .env file"
    exit /b 1
)
goto :eof

:create_frontend_env
echo [INFO] Creating frontend\.env file...

(
echo # Backend API Configuration
echo VITE_BACKEND_HOST=%BACKEND_HOST%
echo VITE_BACKEND_PORT=%BACKEND_PORT%
echo BACKEND_HOST=%BACKEND_HOST%
echo BACKEND_PORT=%BACKEND_PORT%
echo.
echo # Database Configuration ^(for reference only - frontend doesn't connect directly^)
echo DB_HOST=%DB_HOST%
echo DB_PORT=%DB_PORT%
echo DB_NAME=%DB_NAME%
echo DB_USER=%DB_USER%
echo DB_PASSWORD=%DB_PASSWORD%
echo.
echo # LLM Service Configuration ^(for reference only - frontend doesn't connect directly^)
echo LLM_HOST=%LLM_HOST%
echo LLM_PORT=%LLM_PORT%
echo LLM_MODEL=%LLM_MODEL%
echo.
echo # Security Configuration
echo SECURITY_MODE=%SECURITY_MODE%
echo SECRET_KEY=%SECRET_KEY%
echo JWT_SECRET_KEY=%JWT_SECRET_KEY%
echo.
echo # Logging ^(for reference only - actual logs are in backend^)
echo LOG_LEVEL=INFO
echo LOG_FILE=logs/healthcare_security.log
echo AUDIT_LOG_FILE=logs/security_audit.log
echo.
echo # Domain Configuration
echo EMAIL_DOMAIN=%EMAIL_DOMAIN%
) > "%FRONTEND_DIR%\.env"

if exist "%FRONTEND_DIR%\.env" (
    call :print_success "Frontend .env file created"
) else (
    call :print_error "Failed to create frontend .env file"
    exit /b 1
)
goto :eof

:create_directories
echo [INFO] Creating required directories...

REM Backend directories
if not exist "%BACKEND_DIR%\logs" mkdir "%BACKEND_DIR%\logs"
if not exist "%BACKEND_DIR%\tests\test_reports" mkdir "%BACKEND_DIR%\tests\test_reports"

REM Frontend directories
if not exist "%FRONTEND_DIR%\tests\reports" mkdir "%FRONTEND_DIR%\tests\reports"

call :print_success "Directories created"
goto :eof

:display_next_steps
echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
call :print_success "Configuration files have been created successfully."
echo.
echo Next Steps:
echo.
echo 1. Set up the PostgreSQL database:
echo    cd backend
echo    python -m venv venv
echo    venv\Scripts\activate
echo    pip install -r requirements.txt
echo    python database.py  # Initialize database and create tables
echo.
echo 2. Start the backend server:
echo    cd backend
echo    venv\Scripts\activate
echo    python app.py
echo.
echo 3. Set up the frontend:
echo    cd frontend
echo    npm install
echo    npm run dev
echo.
echo 4. Access the application:
echo    Frontend: http://localhost:5173 (or Vite's assigned port)
echo    Backend:  http://%BACKEND_HOST%:%BACKEND_PORT%
echo.
echo 5. Default login credentials:
echo    Username: admin
echo    Password: password123
echo.
call :print_warning "IMPORTANT SECURITY NOTES:"
echo    * Change default passwords in production
echo    * Secure your .env files (they contain sensitive data)
echo    * Review CORS settings for production deployment
echo    * Consider using HTTPS in production
echo.
echo [INFO] For more information, see the README.md file.
goto :eof

:error_exit
echo.
call :print_error "Installation failed. Please check the errors above."
pause
exit /b 1

:cancelled_exit
echo.
pause
exit /b 0

:end
echo.
pause
exit /b 0
