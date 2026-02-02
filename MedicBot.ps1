#Requires -RunAsAdministrator
# MedicBot - Robô de Manutenção do Computador (Médico + Bot)
# Uso: .\MedicBot.ps1  ou  .\MedicBot.ps1 -Steps "1,2,5,7"

param([string]$Steps = "", [switch]$Silent, [string]$DefenderScanType = "1")

$ErrorActionPreference = "SilentlyContinue"
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$logPath = Join-Path $scriptDir "MedicBot_log.txt"
$inicio = Get-Date

# Quais etapas executar (vazio = todas)
$stepsArray = @()
if ($Steps) {
    $stepsArray = $Steps -split "," | ForEach-Object { [int]$_.Trim() } | Where-Object { $_ -ge 1 -and $_ -le 14 }
}

# Total de etapas = selecionadas ou 14 se nenhuma especificada
$totalSteps = if ($stepsArray.Count -gt 0) { $stepsArray.Count } else { 14 }
$global:etapaContador = 0  # Contador de etapas executadas

function RodarEtapa { param([int]$n) if ($stepsArray.Count -eq 0) { return $true }; return $n -in $stepsArray }

function Log {
    param([string]$msg, [string]$tipo = "INFO")
    $linha = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [$tipo] $msg"
    Add-Content -Path $logPath -Value $linha -ErrorAction SilentlyContinue
    Write-Output $linha
}

# Controle de etapas para log organizado
$global:etapaAtual = 0
$global:etapaInicio = $null
$global:etapaNome = ""

function Iniciar-Etapa {
    param([int]$num, [string]$nome)
    $global:etapaContador++
    $global:etapaAtual = $global:etapaContador
    $global:etapaNome = $nome
    $global:etapaInicio = Get-Date
    Log "════════════════════════════════════════════════════════════"
    Log "  ETAPA $($global:etapaContador)/$totalSteps - $nome"
    Log "════════════════════════════════════════════════════════════"
    Log "Iniciando..."
}

function Finalizar-Etapa {
    param([string]$resultado = "OK")
    if ($global:etapaInicio) {
        $duracao = (Get-Date) - $global:etapaInicio
        $tempoStr = if ($duracao.TotalMinutes -ge 1) { "$([math]::Floor($duracao.TotalMinutes))min $($duracao.Seconds)s" } else { "$([math]::Round($duracao.TotalSeconds))s" }
        Log ">>> ETAPA $($global:etapaAtual)/$totalSteps CONCLUÍDA em $tempoStr" $resultado
    }
    Log ""
}

function Progresso-Etapa {
    param([string]$msg)
    Log "  ... $msg" "INFO"
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
        Log "${nome}: limpeza feita. Aproximadamente ${liberado} MB liberados." "OK"
        return $liberado
    } catch {
        Log "${nome}: erro - $_" "ERRO"
        return 0
    }
}

# Início
if (-not $Silent) { Clear-Host }
"" | Out-File $logPath -Force
Log "════════════════════════════════════════════════════════════"
Log "  MEDICBOT - INICIANDO MANUTENÇÃO"
Log "════════════════════════════════════════════════════════════"
Log ""

if (RodarEtapa 1) {
    Iniciar-Etapa 1 "Windows Temp"
    Limpar-Pasta -caminho "C:\Windows\Temp" -nome "Windows Temp"
    Finalizar-Etapa
}

if (RodarEtapa 2) {
    Iniciar-Etapa 2 "%TEMP% (Temp do usuário)"
    Limpar-Pasta -caminho $env:TEMP -nome "%TEMP%"
    Finalizar-Etapa
}

if (RodarEtapa 3) {
    Iniciar-Etapa 3 "Prefetch"
    Limpar-Pasta -caminho "C:\Windows\Prefetch" -nome "Prefetch"
    Finalizar-Etapa
}

if (RodarEtapa 4) {
    Iniciar-Etapa 4 "MRT (Ferramenta de Remoção de Malware)"
    $timeoutMinutos = 10
    Progresso-Etapa "Executando verificação (timeout ${timeoutMinutos}min)..."
    try {
        $proc = Start-Process "mrt.exe" -ArgumentList "/Q" -NoNewWindow -PassThru -ErrorAction SilentlyContinue
        if ($proc) {
            $terminou = $proc.WaitForExit($timeoutMinutos * 60 * 1000)
            if (-not $terminou) {
                try { $proc.Kill() } catch { }
                Log "MRT: timeout após ${timeoutMinutos}min." "AVISO"
            } else {
                Log "MRT executado com sucesso." "OK"
            }
        }
    } catch {
        Log "MRT: $_" "AVISO"
    }
    Finalizar-Etapa
}

if (RodarEtapa 5) {
    $scanType = 1; if ($DefenderScanType -eq "2") { $scanType = 2 }
    $tipoNome = if ($scanType -eq 2) { "COMPLETA" } else { "RÁPIDA" }
    Iniciar-Etapa 5 "Antivírus Windows (verificação $tipoNome)"
    $defender = "${env:ProgramFiles}\Windows Defender\MpCmdRun.exe"
    if (Test-Path $defender) {
        Progresso-Etapa "Verificação $tipoNome em andamento (pode demorar vários minutos)..."
        try {
            & $defender -Scan -ScanType $scanType
            Log "Verificação $tipoNome concluída." "OK"
        } catch {
            Log "Erro ao executar: $_" "ERRO"
        }
    } else {
        Log "Windows Defender não encontrado." "AVISO"
    }
    Finalizar-Etapa
}

if (RodarEtapa 6) {
    Iniciar-Etapa 6 "Desfragmentação / TRIM"
    $timeoutMinutos = 10  # Timeout por unidade
    $drives = Get-Volume | Where-Object { $_.DriveLetter -and $_.DriveType -eq 'Fixed' }
    $totalDrives = ($drives | Measure-Object).Count
    $driveNum = 0
    foreach ($vol in $drives) {
        $letra = $vol.DriveLetter
        if (-not $letra) { continue }
        $driveNum++
        Progresso-Etapa "Otimizando unidade ${letra}: ($driveNum de $totalDrives) - timeout ${timeoutMinutos}min..."
        try {
            $job = Start-Job -ScriptBlock { param($l) Optimize-Volume -DriveLetter $l -Defrag 2>&1 | Out-Null } -ArgumentList $letra
            $terminou = Wait-Job $job -Timeout ($timeoutMinutos * 60)
            if ($terminou) {
                Log "  Unidade ${letra}: OK" "OK"
            } else {
                Stop-Job $job -ErrorAction SilentlyContinue
                Log "  Unidade ${letra}: timeout após ${timeoutMinutos}min." "AVISO"
            }
            Remove-Job $job -Force -ErrorAction SilentlyContinue
        } catch {
            Log "  Unidade ${letra}: $_" "AVISO"
        }
    }
    Finalizar-Etapa
}

if (RodarEtapa 7) {
    Iniciar-Etapa 7 "Lixeira"
    try {
        Clear-RecycleBin -Force -ErrorAction Stop
        Log "Lixeira esvaziada." "OK"
    } catch {
        Log "Lixeira vazia ou erro: $_" "AVISO"
    }
    Finalizar-Etapa
}

if (RodarEtapa 8) {
    Iniciar-Etapa 8 "DISM (Limpeza de atualizações antigas)"
    $timeoutMinutos = 15
    Progresso-Etapa "Analisando Component Store (timeout ${timeoutMinutos}min)..."
    try {
        $dism = Get-Command Dism.exe -ErrorAction SilentlyContinue
        if ($dism) {
            $proc = Start-Process "Dism.exe" -ArgumentList "/online", "/Cleanup-Image", "/StartComponentCleanup" -WindowStyle Hidden -PassThru -ErrorAction SilentlyContinue
            if ($proc) {
                $terminou = $proc.WaitForExit($timeoutMinutos * 60 * 1000)
                if (-not $terminou) {
                    try { $proc.Kill() } catch { }
                    Log "DISM: timeout após ${timeoutMinutos}min." "AVISO"
                } else {
                    Log "Limpeza do Component Store concluída." "OK"
                }
            }
        } else {
            Log "DISM não encontrado." "AVISO"
        }
    } catch {
        Log "DISM: $_" "AVISO"
    }
    Finalizar-Etapa
}

if (RodarEtapa 9) {
    Iniciar-Etapa 9 "Limpeza de Disco (cleanmgr)"
    $timeoutMinutos = 5  # Timeout de 5 minutos por unidade
    try {
        $cachePath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VolumeCaches"
        if (Test-Path $cachePath) {
            Progresso-Etapa "Configurando opções de limpeza..."
            Get-ChildItem $cachePath -ErrorAction SilentlyContinue | ForEach-Object {
                Set-ItemProperty -Path $_.PSPath -Name "StateFlags0001" -Value 2 -Type DWord -ErrorAction SilentlyContinue
            }
            Log "  Opções configuradas." "OK"
        }
        $drives = Get-Volume | Where-Object { $_.DriveLetter -and $_.DriveType -eq 'Fixed' }
        $totalDrives = ($drives | Measure-Object).Count
        $driveNum = 0
        foreach ($vol in $drives) {
            $letra = $vol.DriveLetter
            if (-not $letra) { continue }
            $driveNum++
            Progresso-Etapa "Limpando unidade ${letra}: ($driveNum de $totalDrives) - timeout ${timeoutMinutos}min..."
            $proc = Start-Process "cleanmgr.exe" -ArgumentList "/d $letra", "/sagerun:1" -WindowStyle Hidden -PassThru -ErrorAction SilentlyContinue
            if ($proc) {
                $terminou = $proc.WaitForExit($timeoutMinutos * 60 * 1000)  # Timeout em milissegundos
                if (-not $terminou) {
                    try { $proc.Kill() } catch { }
                    Log "  Unidade ${letra}: timeout após ${timeoutMinutos}min (pulando)." "AVISO"
                } else {
                    Log "  Unidade ${letra}: limpeza concluída." "OK"
                }
            }
        }
        if (-not $drives) { Log "Nenhuma unidade fixa encontrada." "AVISO" }
    } catch {
        Log "Limpeza de Disco: $_" "AVISO"
    }
    Finalizar-Etapa
}

if (RodarEtapa 10) {
    Iniciar-Etapa 10 "Programas de Inicialização"
    Progresso-Etapa "Analisando programas de inicialização..."
    try {
        # WHITELIST: só NÃO desativamos o que for crítico (Windows/sistema/segurança). Todo o resto (Xbox, Copilot, Lightshot, etc.) é desativado.
        # Preservar: pasta Windows, Program Files\Microsoft (Win32), Defender, Office, System32, Security Health, CtfMon (teclado), MsMpEng/WdNiss.
        # NÃO preservar: WindowsApps\Microsoft.* em geral (Xbox, Copilot, etc. podem ser desativados).
        $preservePattern = "\\windows\\|\\program files\\microsoft|windows defender|\\microsoft office|\\system32\\|\\syswow64\\|securityhealth|windows security|ctfmon|security health|msmpeng|wdniss"
        # Binário "desativado" igual ao Task Manager: byte 0 = 3, bytes 4-11 = timestamp
        $disabledBytes = [byte[]]::new(12)
        $disabledBytes[0] = 3
        [System.BitConverter]::GetBytes([datetime]::UtcNow.ToFileTime()).CopyTo($disabledBytes, 4)
        $totalDisabled = 0

        # ---- Run, Run32 e StartupFolder via Win32_StartupCommand (mesmo que Task Manager) ----
        $all = Get-CimInstance Win32_StartupCommand -ErrorAction SilentlyContinue
        foreach ($item in $all) {
            $cmdNorm = ($item.Command -replace '"', "").ToLowerInvariant()
            $nameNorm = ($item.Name -replace "\.exe.*$", "").ToLowerInvariant()
            if ($cmdNorm -match $preservePattern -or $nameNorm -match "securityhealth|windows.?security|ctfmon|security health") {
                Log "  Mantido (sistema): $($item.Name)" "INFO"
                continue
            }
            $approvalPath = $null
            $approvalName = $null
            $loc = $item.Location
            if ($loc -match "RunOnce|RunServices") { continue }
            if ($loc -match "HKCU|HKEY_CURRENT_USER") {
                if ($loc -match "CurrentVersion\\Run$") {
                    $approvalPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
                    $approvalName = $item.Name
                }
            } elseif ($loc -match "HKLM|HKEY_LOCAL_MACHINE") {
                if ($loc -match "CurrentVersion\\Run$") {
                    if ($loc -match "Wow6432Node") {
                        $approvalPath = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run32"
                    } else {
                        $approvalPath = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
                    }
                    $approvalName = $item.Name
                }
            } elseif ($loc -eq "Startup" -or $loc -eq "Common Startup") {
                $sid = $item.UserSID
                if ($sid) {
                    $approvalPath = "Registry::HKEY_USERS\$sid\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder"
                    $approvalName = $item.Command
                }
            }
            if (-not $approvalPath -or -not $approvalName) { continue }
            if (-not (Test-Path $approvalPath)) {
                try { New-Item -Path $approvalPath -Force | Out-Null } catch { continue }
            }
            try {
                Set-ItemProperty -LiteralPath $approvalPath -Name $approvalName -Value $disabledBytes -Type Binary -Force -ErrorAction Stop
                $totalDisabled++
                Log "  Desativado: $($item.Name)" "OK"
            } catch {
                Log "  Ignorado: $($item.Name) - $_" "AVISO"
            }
        }

        # ---- Fallback: enumerar Run/Run32 direto (caso WMI não devolva o mesmo nome do registro) ----
        $runMaps = @(
            @{ Run = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"; Approval = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run" },
            @{ Run = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run"; Approval = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run" },
            @{ Run = "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Run"; Approval = "HKLM:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run32" }
        )
        foreach ($rm in $runMaps) {
            if (-not (Test-Path $rm.Run)) { continue }
            try {
                $props = Get-ItemProperty -Path $rm.Run -ErrorAction Stop
                foreach ($p in $props.PSObject.Properties) {
                    if ($p.Name -match "^(PSPath|PSParentPath|PSChildName|PSDrive|PSProvider)$") { continue }
                    $cmd = $p.Value
                    if (-not $cmd) { continue }
                    $cmdNorm = ($cmd -replace '"', "").ToLowerInvariant()
                    $nameNorm = ($p.Name -replace "\.exe.*$", "").ToLowerInvariant()
                    if ($cmdNorm -match $preservePattern -or $nameNorm -match "securityhealth|windows.?security|ctfmon") { continue }
                    if (-not (Test-Path $rm.Approval)) { New-Item -Path $rm.Approval -Force | Out-Null }
                    try {
                        $cur = Get-ItemProperty -Path $rm.Approval -Name $p.Name -ErrorAction Stop
                        if ($cur -and $cur.($p.Name) -is [byte[]] -and $cur.($p.Name).Length -ge 1 -and $cur.($p.Name)[0] -eq 3) { continue }
                    } catch { }
                    try {
                        Set-ItemProperty -Path $rm.Approval -Name $p.Name -Value $disabledBytes -Type Binary -Force -ErrorAction Stop
                        $totalDisabled++
                        Log "  Desativado (Run): $($p.Name)" "OK"
                    } catch { }
                }
            } catch { }
        }

        # ---- StartupFolder: atalhos .lnk — marcar como desativado no registro (valor = caminho do .lnk) ----
        $startupFolder = [Environment]::GetFolderPath("Startup")
        $sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
        $folderApproval = "Registry::HKEY_USERS\$sid\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\StartupFolder"
        if ((Test-Path $startupFolder) -and $sid) {
            if (-not (Test-Path $folderApproval)) { try { New-Item -Path $folderApproval -Force | Out-Null } catch { } }
            $shell = New-Object -ComObject WScript.Shell -ErrorAction SilentlyContinue
            if ($shell) {
                Get-ChildItem -Path $startupFolder -Filter "*.lnk" -File -ErrorAction SilentlyContinue | ForEach-Object {
                    $fullPath = $_.FullName
                    try {
                        $shortcut = $shell.CreateShortcut($fullPath)
                        $target = $shortcut.TargetPath
                        if (-not $target) { return }
                        $targetNorm = $target.ToLowerInvariant()
                        if ($targetNorm -match $preservePattern) {
                            Log "  Mantido (pasta): $($_.Name)" "INFO"
                            return
                        }
                        try {
                            Set-ItemProperty -LiteralPath $folderApproval -Name $fullPath -Value $disabledBytes -Type Binary -Force -ErrorAction Stop
                            $totalDisabled++
                            Log "  Desativado (pasta): $($_.Name)" "OK"
                        } catch {
                            Set-ItemProperty -LiteralPath $folderApproval -Name $target -Value $disabledBytes -Type Binary -Force -ErrorAction SilentlyContinue
                            if ($?) { $totalDisabled++; Log "  Desativado (pasta): $($_.Name)" "OK" }
                        }
                    } catch { }
                }
                [System.Runtime.Interopservices.Marshal]::ReleaseComObject($shell) | Out-Null
            }
        }

        # ---- UWP/Store (Xbox, Copilot, Vincular ao celular, etc.): desativar todos exceto whitelist ----
        # State: 1=Desativado, 2=Habilitado. UserEnabledStartupOnce: 0=evita re-habilitar.
        $uwpStateDisabled = 1
        $uwpPreserve = "securityhealth|windows\.security|windows\.defender|microsoft\.windows\.secure"
        $uwpDisabled = @{}
        $regBase = "HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\SystemAppData"
        function Set-UwpStartupDisabled {
            param([string]$pkgName, [string]$taskId)
            $keyPath = "HKCU:\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\SystemAppData\$pkgName\$taskId"
            $regPath = "$regBase\$pkgName\$taskId"
            $ok = $false
            try {
                $null = & reg add "$regPath" /v State /t REG_DWORD /d 1 /f 2>&1
                if ($LASTEXITCODE -eq 0) { $ok = $true }
                $null = & reg add "$regPath" /v UserEnabledStartupOnce /t REG_DWORD /d 0 /f 2>&1
                if ($LASTEXITCODE -eq 0) { $ok = $true }
            } catch { }
            if (-not $ok) {
                try {
                    if (-not (Test-Path $keyPath)) { New-Item -Path $keyPath -Force -ErrorAction Stop | Out-Null }
                    Set-ItemProperty -LiteralPath $keyPath -Name "State" -Value 1 -Type DWord -Force -ErrorAction Stop
                    Set-ItemProperty -LiteralPath $keyPath -Name "UserEnabledStartupOnce" -Value 0 -Type DWord -Force -ErrorAction Stop
                    $ok = $true
                } catch {
                    Log "  UWP falha: $pkgName - $_" "AVISO"
                }
            }
            return $ok
        }
        foreach ($base in @("HKCU:\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\SystemAppData", "HKCU:\Software\Microsoft\Windows\CurrentVersion\AppModel\SystemAppData")) {
            if (-not (Test-Path $base)) { continue }
            try {
                Get-ChildItem -Path $base -Directory -ErrorAction SilentlyContinue | ForEach-Object {
                    $pkgName = $_.PSChildName
                    if ($pkgName -match $uwpPreserve) { return }
                    if ($uwpDisabled[$pkgName]) { return }
                    Get-ChildItem -Path $_.FullName -Directory -ErrorAction SilentlyContinue | ForEach-Object {
                        $taskId = $_.PSChildName
                        if (Set-UwpStartupDisabled -pkgName $pkgName -taskId $taskId) {
                            if (-not $uwpDisabled[$pkgName]) { $uwpDisabled[$pkgName] = $true; $totalDisabled++; Log "  Desativado (UWP): $pkgName" "OK" }
                        }
                    }
                }
            } catch { }
        }
        Get-AppxPackage -ErrorAction SilentlyContinue | Where-Object { $_.PackageFamilyName -and $_.InstallLocation -and ($_.PackageFamilyName -notmatch $uwpPreserve) } | ForEach-Object {
            $pkg = $_
            $pkgName = $pkg.PackageFamilyName
            if ($uwpDisabled[$pkgName]) { return }
            $taskIds = @()
            try {
                $manifestPath = Join-Path $pkg.InstallLocation "AppxManifest.xml"
                if (Test-Path $manifestPath) {
                    [xml]$xml = Get-Content $manifestPath -Raw -ErrorAction SilentlyContinue
                    $nodes = $xml.SelectNodes("//*[local-name()='StartupTask']/@TaskId")
                    foreach ($n in $nodes) { $taskIds += $n.Value }
                }
            } catch { }
            foreach ($taskId in $taskIds) {
                if (-not $taskId) { continue }
                if (Set-UwpStartupDisabled -pkgName $pkgName -taskId $taskId) {
                    if (-not $uwpDisabled[$pkgName]) { $uwpDisabled[$pkgName] = $true; $totalDisabled++; Log "  Desativado (UWP): $pkgName" "OK" }
                }
            }
        }

        if ($totalDisabled -gt 0) {
            Log "$totalDisabled programa(s) desativado(s)." "OK"
        } else {
            Log "Nenhum programa extra a desativar." "OK"
        }
    } catch {
        Log "Erro: $_" "AVISO"
    }
    Finalizar-Etapa
}

if (RodarEtapa 11) {
    Iniciar-Etapa 11 "Cache DNS"
    try {
        ipconfig /flushdns 2>&1 | Out-Null
        Log "Cache DNS limpo." "OK"
    } catch {
        Log "DNS: $_" "AVISO"
    }
    Finalizar-Etapa
}

if (RodarEtapa 12) {
    Iniciar-Etapa 12 "Cache de Miniaturas"
    $thumbPath = "$env:LOCALAPPDATA\Microsoft\Windows\Explorer"
    if (Test-Path $thumbPath) {
        try {
            $thumbFiles = Get-ChildItem $thumbPath -Filter "thumbcache_*.db" -File -ErrorAction SilentlyContinue
            $count = 0
            foreach ($f in $thumbFiles) {
                Remove-Item $f.FullName -Force -ErrorAction SilentlyContinue
                $count++
            }
            Log "$count arquivo(s) de cache removido(s)." "OK"
        } catch {
            Log "Erro: $_" "AVISO"
        }
    } else {
        Log "Pasta não encontrada." "AVISO"
    }
    Finalizar-Etapa
}

if (RodarEtapa 13) {
    Iniciar-Etapa 13 "Relatórios de Erro (WER)"
    $werPath = "$env:LOCALAPPDATA\Microsoft\Windows\WER"
    if (Test-Path $werPath) {
        try {
            $antesWer = (Get-ChildItem $werPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            Get-ChildItem $werPath -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
            $depoisWer = (Get-ChildItem $werPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            $liberadoWer = [math]::Round(($antesWer - $depoisWer) / 1MB, 2)
            Log "~${liberadoWer} MB liberados." "OK"
        } catch {
            Log "Erro: $_" "AVISO"
        }
    } else {
        Log "Pasta não encontrada." "AVISO"
    }
    Finalizar-Etapa
}

if (RodarEtapa 14) {
    Iniciar-Etapa 14 "Delivery Optimization"
    $doPath = "$env:SystemRoot\ServiceProfiles\NetworkService\AppData\Local\Microsoft\Windows\DeliveryOptimization\Cache"
    if (Test-Path $doPath) {
        try {
            $antesDo = (Get-ChildItem $doPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            Get-ChildItem $doPath -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
            $depoisDo = (Get-ChildItem $doPath -Recurse -File -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
            $liberadoDo = [math]::Round(($antesDo - $depoisDo) / 1MB, 2)
            Log "~${liberadoDo} MB liberados." "OK"
        } catch {
            Log "Erro: $_" "AVISO"
        }
    } else {
        Log "Cache não encontrado ou vazio." "AVISO"
    }
    Finalizar-Etapa
}

# Fim
$fim = Get-Date
$duracao = $fim - $inicio
$tempoTotal = if ($duracao.TotalMinutes -ge 1) { "$([math]::Floor($duracao.TotalMinutes))min $($duracao.Seconds)s" } else { "$([math]::Round($duracao.TotalSeconds))s" }
Log ""
Log "════════════════════════════════════════════════════════════"
Log "  MANUTENÇÃO CONCLUÍDA"
Log "════════════════════════════════════════════════════════════"
Log "Tempo total: $tempoTotal" "OK"
Log "Log salvo em: $logPath" "INFO"
if (-not $Silent) {
    Write-Host ""
    Write-Host "Pressione qualquer tecla para sair..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
