#Requires -RunAsAdministrator
# MediBot - Robô de Manutenção do Computador (Médico + Bot)
# Limpeza de disco, temp, prefetch, antivírus, desfragmentação, inicialização e mais.

$ErrorActionPreference = "SilentlyContinue"
$logPath = "$env:USERPROFILE\Desktop\conversa\MediBot_log.txt"
$inicio = Get-Date
$totalSteps = 14

function Log {
    param([string]$msg, [string]$tipo = "INFO")
    $linha = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$tipo] $msg"
    Add-Content -Path $logPath -Value $linha -ErrorAction SilentlyContinue
    Write-Host $linha
}

function Limpar-Pasta {
    param([string]$caminho, [string]$nome)
    if (-not (Test-Path $caminho)) {
        Log "Pasta não encontrada: $nome ($caminho)" "AVISO"
        return 0
    }
    try {
        $antes = (Get-ChildItem $caminho -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        Get-ChildItem $caminho -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        $depois = (Get-ChildItem $caminho -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $liberado = [math]::Round(($antes - $depois) / 1MB, 2)
        Log "$nome: limpeza feita. Aproximadamente ${liberado} MB liberados." "OK"
        return $liberado
    } catch {
        Log "$nome: erro - $_" "ERRO"
        return 0
    }
}

# Início
Clear-Host
"" | Out-File $logPath -Force
Log "========== MediBot - Início da manutenção ==========" "INFO"
Log ""

# 1. Temp do Windows (C:\Windows\Temp)
Log ">>> 1/$totalSteps - Limpando C:\Windows\Temp" "INFO"
Limpar-Pasta -caminho "C:\Windows\Temp" -nome "Windows Temp"
Log ""

# 2. Temp do usuário (%TEMP%)
Log ">>> 2/$totalSteps - Limpando %TEMP% (Temp do usuário)" "INFO"
Limpar-Pasta -caminho $env:TEMP -nome "%TEMP%"
Log ""

# 3. Prefetch
Log ">>> 3/$totalSteps - Limpando Prefetch" "INFO"
Limpar-Pasta -caminho "C:\Windows\Prefetch" -nome "Prefetch"
Log ""

# 4. Ferramenta de Remoção de Software Mal-intencionado (MRT)
Log ">>> 4/$totalSteps - Abrindo Ferramenta MRT (Microsoft)" "INFO"
try {
    Start-Process "mrt.exe" -Wait
    Log "MRT foi executado." "OK"
} catch {
    Log "MRT: não foi possível abrir. $_" "ERRO"
}
Log ""

# 5. Verificação do Windows Defender (antivírus)
Log ">>> 5/$totalSteps - Iniciando verificação rápida do Windows Defender..." "INFO"
$defender = "${env:ProgramFiles}\Windows Defender\MpCmdRun.exe"
if (Test-Path $defender) {
    try {
        & $defender -Scan -ScanType 1
        Log "Verificação rápida do Defender concluída." "OK"
    } catch {
        Log "Defender: erro ao executar. $_" "ERRO"
    }
} else {
    Log "Windows Defender não encontrado neste caminho." "AVISO"
}
Log ""

# 6. Desfragmentação / Otimização de unidades
Log ">>> 6/$totalSteps - Otimizando unidades (desfragmentação/TRIM)..." "INFO"
$drives = Get-Volume | Where-Object { $_.DriveLetter -and $_.DriveType -eq 'Fixed' }
foreach ($vol in $drives) {
    $letra = $vol.DriveLetter
    if (-not $letra) { continue }
    try {
        Optimize-Volume -DriveLetter $letra -Defrag -Verbose 2>&1 | Out-Null
        Log "Unidade ${letra}: otimização concluída." "OK"
    } catch {
        Log "Unidade ${letra}: $_" "AVISO"
    }
}
Log ""

# 7. Limpar Lixeira
Log ">>> 7/$totalSteps - Esvaziando Lixeira" "INFO"
try {
    Clear-RecycleBin -Force -ErrorAction Stop
    Log "Lixeira esvaziada." "OK"
} catch {
    Log "Lixeira: $_" "AVISO"
}
Log ""

# 8. Limpeza do Sistema (DISM - Component Store / atualizações antigas)
Log ">>> 8/$totalSteps - Limpeza do Sistema (DISM - atualizações antigas do Windows)..." "INFO"
Log "Isso pode levar alguns minutos e libera bastante espaço em disco." "INFO"
try {
    $dism = Get-Command Dism.exe -ErrorAction SilentlyContinue
    if ($dism) {
        & Dism.exe /online /Cleanup-Image /StartComponentCleanup 2>&1 | Out-Null
        Log "Limpeza do Component Store (DISM) concluída." "OK"
    } else {
        Log "DISM não encontrado." "AVISO"
    }
} catch {
    Log "DISM: $_" "AVISO"
}
Log ""

# 9. Limpeza de Disco (cleanmgr) - abre a janela para você usar "Limpar arquivos do sistema"
Log ">>> 9/$totalSteps - Abrindo Limpeza de Disco (cleanmgr)..." "INFO"
try {
    $driveC = (Get-Volume -DriveLetter C -ErrorAction SilentlyContinue).DriveLetter
    if ($driveC) {
        Start-Process "cleanmgr.exe" -ArgumentList "/d $driveC"
        Log "Limpeza de Disco aberta. Clique em 'Limpar arquivos do sistema' para limpeza completa." "OK"
    } else {
        Start-Process "cleanmgr.exe"
        Log "Limpeza de Disco aberta." "OK"
    }
} catch {
    Log "Limpeza de Disco: $_" "ERRO"
}
Log ""

# 10. Programas que iniciam com o Windows
Log ">>> 10/$totalSteps - Programas de inicialização..." "INFO"
try {
    Start-Process "ms-settings:startup"
    Log "Configurações de inicialização abertas. Desative programas desnecessários." "OK"
    $startups = @(Get-CimInstance Win32_StartupCommand -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name)
    if ($startups.Count -gt 0) {
        Log "Programas que iniciam com o Windows (amostra):" "INFO"
        $startups | Select-Object -First 20 | ForEach-Object { Log "  - $_" "INFO" }
        if ($startups.Count -gt 20) { Log "  ... e mais $($startups.Count - 20) itens. Veja em Configurações > Aplicativos > Inicialização." "INFO" }
    }
} catch {
    Log "Inicialização: $_" "AVISO"
}
Log ""

# 11. Limpar cache DNS
Log ">>> 11/$totalSteps - Limpando cache DNS..." "INFO"
try {
    ipconfig /flushdns 2>&1 | Out-Null
    Log "Cache DNS limpo. Conexões de rede podem ficar mais estáveis." "OK"
} catch {
    Log "DNS: $_" "AVISO"
}
Log ""

# 12. Cache de miniaturas (thumbcache)
Log ">>> 12/$totalSteps - Limpando cache de miniaturas..." "INFO"
$thumbPath = "$env:LOCALAPPDATA\Microsoft\Windows\Explorer"
if (Test-Path $thumbPath) {
    try {
        $thumbFiles = Get-ChildItem $thumbPath -Filter "thumbcache_*.db" -File -ErrorAction SilentlyContinue
        $count = 0
        foreach ($f in $thumbFiles) {
            Remove-Item $f.FullName -Force -ErrorAction SilentlyContinue
            $count++
        }
        Log "Cache de miniaturas: $count arquivo(s) removido(s)." "OK"
    } catch {
        Log "Miniaturas: $_" "AVISO"
    }
} else {
    Log "Pasta de miniaturas não encontrada." "AVISO"
}
Log ""

# 13. Relatórios de erro do Windows (Windows Error Reporting)
Log ">>> 13/$totalSteps - Limpando relatórios de erro do Windows (WER)..." "INFO"
$werPath = "$env:LOCALAPPDATA\Microsoft\Windows\WER"
if (Test-Path $werPath) {
    try {
        $antesWer = (Get-ChildItem $werPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        Get-ChildItem $werPath -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        $depoisWer = (Get-ChildItem $werPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $liberadoWer = [math]::Round(($antesWer - $depoisWer) / 1MB, 2)
        Log "Relatórios de erro (WER): aproximadamente ${liberadoWer} MB liberados." "OK"
    } catch {
        Log "WER: $_" "AVISO"
    }
} else {
    Log "Pasta WER não encontrada." "AVISO"
}
Log ""

# 14. Cache do Delivery Optimization (atualizações)
Log ">>> 14/$totalSteps - Limpando cache do Delivery Optimization..." "INFO"
$doPath = "$env:SystemRoot\ServiceProfiles\NetworkService\AppData\Local\Microsoft\Windows\DeliveryOptimization\Cache"
if (Test-Path $doPath) {
    try {
        $antesDo = (Get-ChildItem $doPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        Get-ChildItem $doPath -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        $depoisDo = (Get-ChildItem $doPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $liberadoDo = [math]::Round(($antesDo - $depoisDo) / 1MB, 2)
        Log "Delivery Optimization: aproximadamente ${liberadoDo} MB liberados." "OK"
    } catch {
        Log "Delivery Optimization: $_" "AVISO"
    }
} else {
    Log "Cache do Delivery Optimization não encontrado ou já vazio." "AVISO"
}

# Fim
$fim = Get-Date
$duracao = $fim - $inicio
Log ""
Log "========== MediBot - Fim da manutenção ==========" "INFO"
Log "Tempo total: $($duracao.ToString('mm\:ss'))" "INFO"
Log "Log salvo em: $logPath" "INFO"
Write-Host ""
Write-Host "Pressione qualquer tecla para sair..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
