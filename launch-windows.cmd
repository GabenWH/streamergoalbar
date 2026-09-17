@echo off
setlocal

powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ^
"$ErrorActionPreference = 'Stop'; ^
  $root = $args[0]; ^
  $configFile = Join-Path $root 'userdata.json'; ^
  if (-not (Test-Path -LiteralPath $configFile)) { throw ('Missing configuration file: ' + $configFile) }; ^
  try { $config = Get-Content -LiteralPath $configFile -Raw | ConvertFrom-Json } catch { throw ('Could not read userdata.json: ' + $_.Exception.Message) }; ^
  foreach ($name in 'TARGET', 'CB_EVENTS_TOKEN', 'CB_USERNAME', 'CB_TITLE') { ^
    $property = $config.PSObject.Properties[$name]; ^
    if ($null -eq $property -or [string]::IsNullOrWhiteSpace([string]$property.Value)) { throw ('userdata.json requires a non-empty ' + $name) }; ^
    Set-Item -Path ('Env:' + $name) -Value ([string]$property.Value) ^
  }; ^
  & python (Join-Path $root 'server.py'); ^
  exit $LASTEXITCODE" "%~dp0"

exit /b %ERRORLEVEL%
