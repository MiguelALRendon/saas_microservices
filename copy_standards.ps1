$source = Join-Path $PSScriptRoot "DEVELOPMENT_STANDARDS.md"

$services = @(
    "auth_service",
    "branch_service",
    "catalogues_service",
    "inventory_service",
    "sales_service",
    "sistema_service",
    "supplier_service",
    "validation_service"
)

foreach ($service in $services) {
    $dest = Join-Path $PSScriptRoot "$service\DEVELOPMENT_STANDARDS.md"
    Copy-Item -Path $source -Destination $dest -Force
    Write-Host "Copiado en: $service" -ForegroundColor Green
}

Write-Host "`nListo. Standards actualizados en $($services.Count) servicios." -ForegroundColor Cyan
