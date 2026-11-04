param(
    [Parameter(Mandatory=$true)][string]$Pptx,
    [Parameter(Mandatory=$true)][string]$Out
)
$ErrorActionPreference = "Stop"
$app = New-Object -ComObject PowerPoint.Application
$pres = $app.Presentations.Open((Resolve-Path $Pptx).Path, -1, 0, 0)
$result = [ordered]@{
    file = (Resolve-Path $Pptx).Path
    powerpoint = [string]$app.Version
    slides = @()
}
try {
    foreach ($slide in $pres.Slides) {
        $effects = @()
        foreach ($e in $slide.TimeLine.MainSequence) {
            $effects += [ordered]@{
                shape = $e.Shape.Name
                effect_type = [int]$e.EffectType
                trigger = [int]$e.Timing.TriggerType
                duration_s = [double]$e.Timing.Duration
                delay_s = [double]$e.Timing.TriggerDelayTime
            }
        }
        $result.slides += [ordered]@{
            index = $slide.SlideIndex
            effects = $effects.Count
            animation = $effects
        }
    }
} finally {
    $pres.Close(); $app.Quit()
    [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
$result | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 $Out
Write-Output "$($result.file): $(($result.slides | ForEach-Object { $_.effects }) -join ', ') effects"
