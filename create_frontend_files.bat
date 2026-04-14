@echo off
setlocal

REM ============================================
REM 创建前端目录和空文件（仅创建，不写内容）
REM 项目根目录：
REM D:\software\workspace\talent-market-sim
REM ============================================

set PROJECT_ROOT=D:\software\workspace\talent-market-sim
set FRONTEND_ROOT=%PROJECT_ROOT%\frontend\src

echo ============================================
echo 开始创建前端目录...
echo ============================================

if not exist "%FRONTEND_ROOT%\components\common" mkdir "%FRONTEND_ROOT%\components\common"
if not exist "%FRONTEND_ROOT%\components\config" mkdir "%FRONTEND_ROOT%\components\config"
if not exist "%FRONTEND_ROOT%\components\charts" mkdir "%FRONTEND_ROOT%\components\charts"
if not exist "%FRONTEND_ROOT%\components\result" mkdir "%FRONTEND_ROOT%\components\result"
if not exist "%FRONTEND_ROOT%\composables" mkdir "%FRONTEND_ROOT%\composables"
if not exist "%FRONTEND_ROOT%\utils" mkdir "%FRONTEND_ROOT%\utils"

echo.
echo ============================================
echo 开始创建前端空文件...
echo ============================================

type nul > "%FRONTEND_ROOT%\components\common\InfoTip.vue"
type nul > "%FRONTEND_ROOT%\components\common\FieldLabel.vue"

type nul > "%FRONTEND_ROOT%\components\config\BaseConfigPanel.vue"
type nul > "%FRONTEND_ROOT%\components\config\StudentConfigPanel.vue"
type nul > "%FRONTEND_ROOT%\components\config\SchoolConfigPanel.vue"
type nul > "%FRONTEND_ROOT%\components\config\EmployerConfigPanel.vue"
type nul > "%FRONTEND_ROOT%\components\config\ScenarioConfigPanel.vue"
type nul > "%FRONTEND_ROOT%\components\config\AdvancedConfigPanel.vue"
type nul > "%FRONTEND_ROOT%\components\config\LLMConfigPanel.vue"

type nul > "%FRONTEND_ROOT%\components\charts\EmploymentChart.vue"
type nul > "%FRONTEND_ROOT%\components\charts\VacancyChart.vue"

type nul > "%FRONTEND_ROOT%\components\result\SummaryCards.vue"
type nul > "%FRONTEND_ROOT%\components\result\MetricsTable.vue"
type nul > "%FRONTEND_ROOT%\components\result\RawResultViewer.vue"
type nul > "%FRONTEND_ROOT%\components\result\ExperimentHistory.vue"

type nul > "%FRONTEND_ROOT%\composables\useSimulation.js"

type nul > "%FRONTEND_ROOT%\utils\configDefaults.js"
type nul > "%FRONTEND_ROOT%\utils\fieldMeta.js"

echo.
echo ============================================
echo 前端目录和空文件创建完成。
echo ============================================

pause
endlocal