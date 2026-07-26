param(
    [string]$Action = "install"
)

$ErrorActionPreference = "Stop"
$TaskName = "PC Power Control Backend"
$Description = "Starts the PC Power Control REST server on system startup"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ExePath = Join-Path $ScriptDir "dist\PCPowerControl.exe"
$PythonwPath = Join-Path $ScriptDir "venv\Scripts\pythonw.exe"
$MainPyPath = Join-Path $ScriptDir "main.py"

if (Test-Path $ExePath) {
    $ProgramPath = $ExePath
    $Arguments = ""
} elseif (Test-Path $PythonwPath) {
    $ProgramPath = $PythonwPath
    $Arguments = "`"$MainPyPath`""
} else {
    Write-Host "ERROR: Neither PCPowerControl.exe nor venv found."
    Write-Host "Run build.py first or install dependencies."
    exit 1
}

switch ($Action) {
    "install" {
        Write-Host "Installing Task Scheduler entry: $TaskName"
        $TaskParams = @{
            TaskName = $TaskName
            Description = $Description
            Action = New-ScheduledTaskAction -Execute $ProgramPath -Argument $Arguments -WorkingDirectory $ScriptDir
            Trigger = @(
                New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
                New-ScheduledTaskTrigger -AtStartup
            )
            Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest -LogonType Interactive
            Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        }
        Register-ScheduledTask @TaskParams -Force
        Write-Host "SUCCESS: Task '$TaskName' installed."
        Write-Host "  Program: $ProgramPath"
        Write-Host "  Args: $Arguments"
        Write-Host "  Triggers: At logon, At startup"
        Start-ScheduledTask -TaskName $TaskName
        Write-Host "Task started."
    }
    "remove" {
        Write-Host "Removing Task Scheduler entry: $TaskName"
        Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Task '$TaskName' removed."
    }
    "status" {
        try {
            $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
            Write-Host "Task: $TaskName"
            Write-Host "State: $($task.State)"
            Write-Host "Path: $($task.TaskPath)"
        } catch {
            Write-Host "Task '$TaskName' not found."
        }
    }
    default {
        Write-Host "Usage: .\setup_task.ps1 [install|remove|status]"
    }
}
