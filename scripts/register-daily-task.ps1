# Registers (or replaces) the weekday 10:00 Task Scheduler job for pm-decision.
$ErrorActionPreference = "Stop"

$TaskName = "pm-decision-daily"
$TaskDescription = "Grava lancamentos pendentes do PM Decision (seg-sex as 10:00)."
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$RunnerPath = Join-Path $PSScriptRoot "run-daily.cmd"
$StartTime = "10:00"

if (-not (Test-Path -LiteralPath $RunnerPath)) {
    throw "Runner nao encontrado: $RunnerPath"
}

$Action = New-ScheduledTaskAction `
    -Execute $RunnerPath `
    -WorkingDirectory $ProjectRoot

$Trigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Monday, Tuesday, Wednesday, Thursday, Friday `
    -At $StartTime

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $TaskDescription `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Force | Out-Null

$Registered = Get-ScheduledTask -TaskName $TaskName
$Info = Get-ScheduledTaskInfo -TaskName $TaskName

Write-Host "Tarefa registrada: $($Registered.TaskName)"
Write-Host "Estado: $($Registered.State)"
Write-Host "Proximo horario: $($Info.NextRunTime)"
Write-Host "Runner: $RunnerPath"
