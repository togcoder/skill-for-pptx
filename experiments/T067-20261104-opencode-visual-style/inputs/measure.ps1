param(
    [Parameter(Mandatory=$true)][string]$Pptx,
    [Parameter(Mandatory=$true)][string]$Out
)

$ErrorActionPreference = "Stop"
$pptxPath = (Resolve-Path $Pptx).Path
$app = New-Object -ComObject PowerPoint.Application
$sw = [Diagnostics.Stopwatch]::StartNew()
$pres = $app.Presentations.Open($pptxPath, $true, $false, $false)
$sw.Stop()
try {
    $slides = @()
    for ($i = 1; $i -le $pres.Slides.Count; $i++) {
        $slide = $pres.Slides.Item($i)
        $seq = $slide.TimeLine.MainSequence
        $effects = @()
        for ($e = 1; $e -le $seq.Count; $e++) {
            $eff = $seq.Item($e)
            $effects += [ordered]@{
                shape    = $eff.Shape.Name
                type     = $eff.EffectType
                duration = [math]::Round($eff.Timing.Duration, 3)
                trigger  = $eff.Timing.TriggerType
            }
        }
        $slides += [ordered]@{
            index         = $i
            shapes        = $slide.Shapes.Count
            effects       = $seq.Count
            effect_detail = $effects
            transition    = $slide.SlideShowTransition.EntryEffect
        }
    }
    $meta = [ordered]@{
        file      = [System.IO.Path]::GetFileName($pptxPath)
        bytes     = (Get-Item $pptxPath).Length
        slides    = $pres.Slides.Count
        open_ms   = $sw.ElapsedMilliseconds
        read_only = $pres.ReadOnly
        app       = $app.Version
        detail    = $slides
    }
    $json = $meta | ConvertTo-Json -Depth 6
    [System.IO.File]::WriteAllText($Out, $json, (New-Object System.Text.UTF8Encoding $false))
    $effectTotal = 0
    foreach ($s in $slides) { $effectTotal += $s.effects }
    Write-Output ("open_ms={0} slides={1} effects={2}" -f $meta.open_ms, $meta.slides,
        $effectTotal)
}
finally {
    $pres.Close()
    $app.Quit()
}
