param(
    [Parameter(Mandatory=$true)][string]$Pptx,
    [Parameter(Mandatory=$true)][string]$OutDir,
    [int]$Width = 1920,
    [int]$Height = 1080
)

$ErrorActionPreference = "Stop"
$pptxPath = (Resolve-Path $Pptx).Path
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$outPath = (Resolve-Path $OutDir).Path

$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open($pptxPath, $true, $false, $false)
try {
    for ($i = 1; $i -le $pres.Slides.Count; $i++) {
        $file = Join-Path $outPath ("slide-{0:D2}.png" -f $i)
        $pres.Slides.Item($i).Export($file, "PNG", $Width, $Height)
        Write-Output $file
    }
    $pdf = Join-Path $outPath ([System.IO.Path]::GetFileNameWithoutExtension($pptxPath) + ".pdf")
    $pres.SaveAs($pdf, 32)
    Write-Output $pdf
}
finally {
    $pres.Close()
    $app.Quit()
}
