$envFile = '.env'
$vars = @{}
Get-Content $envFile | ForEach-Object {
  if ($_ -match '^\s*#' -or $_ -match '^\s*$') { return }
  $parts = $_ -split '=',2
  if ($parts.Count -eq 2) { $vars[$parts[0].Trim()] = $parts[1].Trim().Trim('"') }
}
$dbHost = $vars['CATALOG_MYSQL_HOST']; if (-not $dbHost) { $dbHost = $vars['MYSQL_HOST'] }
$dbPort = $vars['CATALOG_MYSQL_PORT']; if (-not $dbPort) { $dbPort = $vars['MYSQL_PORT'] }
$dbUser = $vars['CATALOG_MYSQL_USER']; if (-not $dbUser) { $dbUser = $vars['MYSQL_USER'] }
$dbPass = $vars['CATALOG_MYSQL_PASSWORD']; if (-not $dbPass) { $dbPass = $vars['MYSQL_PASSWORD'] }
$dbName = 'bhasin_7001_new'
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$out = "exports/${dbName}_skip2_${ts}.sql"
$log = "exports/${dbName}_skip2_${ts}.log"
$dumpExe = 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe'
& $dumpExe --single-transaction --quick --skip-lock-tables --default-character-set=utf8mb4 --routines --triggers --events --ignore-table=${dbName}.address_allowed_center --ignore-table=${dbName}.testwarning --ignore-table=${dbName}.test_warning -h $dbHost -P $dbPort -u $dbUser "-p$dbPass" $dbName > $out 2> $log
"done: $out" | Out-File -FilePath ($out + '.done.txt') -Encoding ascii
