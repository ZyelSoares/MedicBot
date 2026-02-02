# DiagnosticStartup.ps1 - Rode como Administrador para ver o estado atual do registro de inicialização UWP
# Use: .\DiagnosticStartup.ps1   (na pasta do MedicBot)
$base = "HKCU:\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\SystemAppData"
Write-Host "=== Caminho AppModel (UWP) ===" -ForegroundColor Cyan
if (Test-Path $base) {
    Write-Host "OK: Caminho existe: $base" -ForegroundColor Green
    Get-ChildItem -Path $base -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        $pkg = $_.PSChildName
        Get-ChildItem -Path $_.FullName -Directory -ErrorAction SilentlyContinue | ForEach-Object {
            $task = $_.PSChildName
            try {
                $state = (Get-ItemProperty -Path $_.FullName -Name "State" -ErrorAction Stop).State
                $userOnce = $null
                try { $userOnce = (Get-ItemProperty -Path $_.FullName -Name "UserEnabledStartupOnce" -ErrorAction Stop).UserEnabledStartupOnce } catch { }
                $status = if ($state -eq 1) { "DESATIVADO" } elseif ($state -eq 2) { "HABILITADO" } else { "State=$state" }
                Write-Host "  $pkg / $task -> State=$state ($status) UserEnabledStartupOnce=$userOnce"
            } catch {
                Write-Host "  $pkg / $task -> (erro ao ler: $_)" -ForegroundColor Yellow
            }
        }
    }
} else {
    Write-Host "FALTA: Caminho nao existe: $base" -ForegroundColor Red
}
Write-Host ""
Write-Host "=== StartupApproved\Run (apps classicos) ===" -ForegroundColor Cyan
$runApproval = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
if (Test-Path $runApproval) {
    Get-ItemProperty -Path $runApproval -ErrorAction SilentlyContinue | Get-Member -MemberType NoteProperty | Where-Object { $_.Name -notmatch "^(PSPath|PSParentPath|PSChildName|PSDrive|PSProvider)$" } | ForEach-Object {
        $name = $_.Name
        try {
            $val = (Get-ItemProperty -Path $runApproval -Name $name -ErrorAction Stop).$name
            $firstByte = if ($val -is [byte[]] -and $val.Length -ge 1) { $val[0] } else { "?" }
            $status = if ($firstByte -eq 3) { "DESATIVADO" } elseif ($firstByte -eq 2) { "HABILITADO" } else { "byte=$firstByte" }
            Write-Host "  $name -> $status"
        } catch { Write-Host "  $name -> (erro)" -ForegroundColor Yellow }
    }
} else {
    Write-Host "Chave Run nao existe." -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Fim do diagnostico. Rode a etapa 10 do MedicBot e execute este script de novo para comparar." -ForegroundColor Gray
