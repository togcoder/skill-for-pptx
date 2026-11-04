param([Parameter(Mandatory=$true)][string]$Manifest)
$ErrorActionPreference = "Stop"
$items = Get-Content -Raw -LiteralPath $Manifest | ConvertFrom-Json
$app = New-Object -ComObject PowerPoint.Application
try {
    foreach ($item in $items) {
        $pres = $app.Presentations.Open($item.pptx, $true, $false, $false)
        try {
            $pres.Slides.Item([int]$item.slide).Export($item.out, "PNG", 1920, 1080)
            Write-Output $item.out
        } finally { $pres.Close() }
    }
} finally {
    $app.Quit()
    [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
