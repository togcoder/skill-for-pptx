param(
    [Parameter(Mandatory=$true)][string]$Output,
    [string]$Manifest
)
# T027: ask desktop PowerPoint to author every built-in animation effect
# (MsoAnimEffect, entrance + exit variants) on its own slide and save the
# deck, so the exact timing XML PowerPoint writes can be harvested.
$ErrorActionPreference = "Stop"
[void][System.Reflection.Assembly]::LoadWithPartialName("Microsoft.Office.Interop.PowerPoint")
$enum = [Microsoft.Office.Interop.PowerPoint.MsoAnimEffect]
$Output = [System.IO.Path]::GetFullPath($Output)
if (-not $Manifest) { $Manifest = [System.IO.Path]::ChangeExtension($Output, ".json") }
$app = New-Object -ComObject PowerPoint.Application
$rows = @()
try {
    $pres = $app.Presentations.Add(0)
    $pres.PageSetup.SlideWidth = 960; $pres.PageSetup.SlideHeight = 540
    foreach ($name in [Enum]::GetNames($enum)) {
        if ($name -eq "msoAnimEffectCustom") { continue }
        $value = [int][Enum]::Parse($enum, $name)
        foreach ($exit in @($false, $true)) {
            $slide = $pres.Slides.Add($pres.Slides.Count + 1, 12)  # ppLayoutBlank
            $shape = $slide.Shapes.AddShape(1, 380, 200, 200, 140)
            $shape.Name = "Target"
            $shape.TextFrame.TextRange.Text = "Sample text line one`rline two"
            $row = [ordered]@{ slide = $slide.SlideIndex; name = $name; value = $value; exit = $exit; ok = $false }
            try {
                $eff = $slide.TimeLine.MainSequence.AddEffect($shape, $value, 0, 1)
                if ($exit) {
                    $eff.Exit = -1
                    if ($eff.Exit -ne -1) { throw "no exit variant" }
                }
                $row.ok = $true
                $row.duration_s = [double]$eff.Timing.Duration
                $row.effect_type = [int]$eff.EffectType
            } catch {
                $row.error = $_.Exception.Message
                $slide.Delete()
                $row.slide = $null
            }
            if ($row.ok -or -not $exit) { $rows += $row }
        }
    }
    $pres.SaveAs($Output)
    $pres.Close()
    [ordered]@{ powerpoint_version = $app.Version; build = $app.Build; effects = $rows } |
        ConvertTo-Json -Depth 4 | Out-File -Encoding utf8 $Manifest
    "saved $Output ($(@($rows | Where-Object { $_.ok }).Count) effects)"
}
finally {
    $app.Quit()
    [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)
}
