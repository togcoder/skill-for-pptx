param(
    [Parameter(Mandatory=$true)][string]$Pptx,
    [Parameter(Mandatory=$true)][string]$OutDir,
    [int]$SecondsPerSlide = 9
)
# Opens the exact deck in desktop PowerPoint (read-only, no window), dumps the
# main sequence as PowerPoint itself parsed it, then renders an MP4 with
# Presentation.CreateVideo so motion can be inspected frame by frame.
$ErrorActionPreference = "Stop"
$Pptx = (Resolve-Path $Pptx).Path
New-Item -ItemType Directory -Force $OutDir | Out-Null
$OutDir = (Resolve-Path $OutDir).Path
$app = New-Object -ComObject PowerPoint.Application
try {
    $pres = $app.Presentations.Open($Pptx, -1, 0, 0)
    $slides = @()
    foreach ($slide in $pres.Slides) {
        $effects = @()
        foreach ($e in $slide.TimeLine.MainSequence) {
            $t = $e.Timing
            $effects += [ordered]@{
                shape = $e.Shape.Name; effect_type = [int]$e.EffectType; exit = [int]$e.Exit
                trigger = [int]$t.TriggerType; delay_s = [double]$t.TriggerDelayTime; duration_s = [double]$t.Duration
                repeat_count = [double]$t.RepeatCount; until_end_of_slide = [int]$t.RepeatDuration
                auto_reverse = [int]$t.AutoReverse
            }
        }
        $slides += [ordered]@{ index = $slide.SlideIndex; effects = $effects }
    }
    $info = [ordered]@{ powerpoint_version = $app.Version; build = $app.Build; pptx = $Pptx; slides = $slides }
    $info | ConvertTo-Json -Depth 6 | Out-File -Encoding utf8 (Join-Path $OutDir "native_sequence.json")

    $video = Join-Path $OutDir "native_render.mp4"
    $pres.CreateVideo($video, $false, $SecondsPerSlide, 720, 30, 85)
    while ($pres.CreateVideoStatus -eq 1 -or $pres.CreateVideoStatus -eq 2) { Start-Sleep -Milliseconds 500 }
    "video status: $($pres.CreateVideoStatus)"
    $pres.Close()
}
finally {
    $app.Quit()
    [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)
}
