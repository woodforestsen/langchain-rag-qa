# RAG 知识库问答系统 — 压力测试执行脚本（Windows PowerShell）
# 用法: .\tests\load\run_tests.ps1 [场景]
#   场景: smoke | login | rag | mixed | short | all
#   示例: .\tests\load\run_tests.ps1 smoke   # 冒烟测试（10用户/1分钟）

param(
    [ValidateSet("smoke", "login", "rag", "mixed", "short", "all")]
    [string]$Scenario = "smoke"
)

$ErrorActionPreference = "Stop"
$HOST_URL = "http://127.0.0.1:8080"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$RESULTS_DIR = Join-Path $SCRIPT_DIR "results"
$DATA_DIR = Join-Path $SCRIPT_DIR "data"
$REPORTS_DIR = Join-Path $SCRIPT_DIR "reports"

# 确保目录存在
foreach ($dir in @($RESULTS_DIR, $DATA_DIR, $REPORTS_DIR)) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  RAG 知识库问答系统 — 压力测试" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  场景: $Scenario"
Write-Host "  目标: $HOST_URL"
Write-Host "  报告: $REPORTS_DIR"
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

function Start-SystemMonitor {
    param([int]$Duration, [string]$OutputName)
    $output = Join-Path $RESULTS_DIR $OutputName
    Write-Host "📊 启动系统监控: $output (${Duration}s)" -ForegroundColor Yellow
    $monitorScript = Join-Path $SCRIPT_DIR "monitor.py"
    $proc = Start-Process -FilePath "python" `
        -ArgumentList $monitorScript, "--duration", $Duration, "--output", $output `
        -NoNewWindow -PassThru
    return $proc
}

function Invoke-LocustTest {
    param(
        [string]$LocustFile,
        [int]$Users,
        [int]$SpawnRate,
        [int]$Duration,
        [string]$Tags = "",
        [string]$ReportName
    )

    $htmlReport = Join-Path $REPORTS_DIR "$ReportName.html"
    $csvPrefix = Join-Path $REPORTS_DIR $ReportName

    $args = @(
        "-f", (Join-Path $SCRIPT_DIR $LocustFile),
        "--headless",
        "--users", $Users,
        "--spawn-rate", $SpawnRate,
        "--run-time", "${Duration}s",
        "--host", $HOST_URL,
        "--html", $htmlReport,
        "--csv", $csvPrefix,
        "--loglevel", "WARNING"
    )

    if ($Tags) {
        $args += "--tags"
        $args += $Tags
    }

    Write-Host ""
    Write-Host "🚀 启动 Locust 压测: $ReportName" -ForegroundColor Green
    Write-Host "   并发: $Users | 孵化率: ${SpawnRate}/s | 时长: ${Duration}s"
    if ($Tags) { Write-Host "   标签: $Tags" }

    python -m locust @args

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $ReportName 完成 → $htmlReport" -ForegroundColor Green
    } else {
        Write-Host "❌ $ReportName 失败 (exit code: $LASTEXITCODE)" -ForegroundColor Red
    }
}

# ============================================================
# 执行场景
# ============================================================

switch ($Scenario) {
    "smoke" {
        # 冒烟测试：验证脚本正确性，低并发短时间
        Write-Host "🔥 冒烟测试：10 用户 / 1 分钟" -ForegroundColor Magenta
        Invoke-LocustTest -LocustFile "locustfile_short.py" -Users 10 -SpawnRate 3 -Duration 60 -ReportName "smoke_test"
    }

    "login" {
        # 场景 1：登录压测
        $duration = 120
        $monitor = Start-SystemMonitor -Duration $duration -OutputName "system_login.csv"
        Invoke-LocustTest -LocustFile "locustfile.py" -Users 100 -SpawnRate 20 -Duration $duration -Tags "auth_only" -ReportName "login_100users"
        Stop-Process -Id $monitor.Id -Force -ErrorAction SilentlyContinue
    }

    "rag" {
        # 场景 2：RAG 问答压测
        $duration = 300
        $monitor = Start-SystemMonitor -Duration $duration -OutputName "system_rag.csv"
        Invoke-LocustTest -LocustFile "locustfile.py" -Users 100 -SpawnRate 5 -Duration $duration -Tags "rag_chat" -ReportName "ragchat_100users"
        Stop-Process -Id $monitor.Id -Force -ErrorAction SilentlyContinue
    }

    "mixed" {
        # 场景 3：混合场景
        $duration = 300
        $monitor = Start-SystemMonitor -Duration $duration -OutputName "system_mixed.csv"
        Invoke-LocustTest -LocustFile "locustfile.py" -Users 100 -SpawnRate 3 -Duration $duration -Tags "mixed_flow" -ReportName "mixed_100users"
        Stop-Process -Id $monitor.Id -Force -ErrorAction SilentlyContinue
    }

    "short" {
        # 短请求压测
        $duration = 180
        $monitor = Start-SystemMonitor -Duration $duration -OutputName "system_short.csv"
        Invoke-LocustTest -LocustFile "locustfile_short.py" -Users 100 -SpawnRate 20 -Duration $duration -ReportName "short_100users"
        Stop-Process -Id $monitor.Id -Force -ErrorAction SilentlyContinue
    }

    "all" {
        # 全部场景阶梯执行
        Write-Host "🚀 执行全部压测场景" -ForegroundColor Magenta

        # Step 1: 冒烟
        Invoke-LocustTest -LocustFile "locustfile_short.py" -Users 10 -SpawnRate 3 -Duration 30 -ReportName "st01_smoke"

        # Step 2: 短请求 50并发
        $monitor = Start-SystemMonitor -Duration 120 -OutputName "system_short.csv"
        Invoke-LocustTest -LocustFile "locustfile_short.py" -Users 100 -SpawnRate 20 -Duration 120 -ReportName "st02_short_100users"
        Stop-Process -Id $monitor.Id -Force -ErrorAction SilentlyContinue

        # Step 3: RAG 问答 50并发
        $monitor = Start-SystemMonitor -Duration 180 -OutputName "system_rag_50.csv"
        Invoke-LocustTest -LocustFile "locustfile.py" -Users 50 -SpawnRate 5 -Duration 180 -Tags "rag_chat" -ReportName "st03_rag_50users"
        Stop-Process -Id $monitor.Id -Force -ErrorAction SilentlyContinue

        # Step 4: RAG 问答 100并发
        $monitor = Start-SystemMonitor -Duration 300 -OutputName "system_rag_100.csv"
        Invoke-LocustTest -LocustFile "locustfile.py" -Users 100 -SpawnRate 5 -Duration 300 -Tags "rag_chat" -ReportName "st04_rag_100users"
        Stop-Process -Id $monitor.Id -Force -ErrorAction SilentlyContinue

        # Step 5: 混合场景 100并发
        $monitor = Start-SystemMonitor -Duration 300 -OutputName "system_mixed.csv"
        Invoke-LocustTest -LocustFile "locustfile.py" -Users 100 -SpawnRate 3 -Duration 300 -Tags "mixed_flow" -ReportName "st05_mixed_100users"
        Stop-Process -Id $monitor.Id -Force -ErrorAction SilentlyContinue

        Write-Host ""
        Write-Host "=" * 60 -ForegroundColor Cyan
        Write-Host "  ✅ 全部压测场景完成！" -ForegroundColor Green
        Write-Host "=" * 60 -ForegroundColor Cyan
        Write-Host "  报告目录: $REPORTS_DIR"
        Write-Host "  结果目录: $RESULTS_DIR"
        Write-Host "=" * 60 -ForegroundColor Cyan
    }
}

Write-Host ""
Write-Host "📁 报告文件:" -ForegroundColor Yellow
Get-ChildItem $REPORTS_DIR -Filter "*.html" | Sort-Object LastWriteTime -Descending | ForEach-Object {
    Write-Host "  → $($_.Name) ($('{0:yyyy-MM-dd HH:mm:ss}' -f $_.LastWriteTime))"
}
