param(
    [Parameter(Mandatory=$true)][string]$Pptx,
    [Parameter(Mandatory=$true)][string]$Manifest,
    [Parameter(Mandatory=$true)][string]$Output,
    [switch]$RunSlideshow,
    [switch]$CaptureScreenshots,
    [int]$ClickPauseMs = 700
)

$ErrorActionPreference = "Stop"

function Invoke-SafeValue {
    param([scriptblock]$Script)
    try { return & $Script } catch { return $null }
}

function Release-ComObjectSafe {
    param($Object)
    if ($null -ne $Object -and [System.Runtime.InteropServices.Marshal]::IsComObject($Object)) {
        try { [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($Object) } catch {}
    }
}

function Get-TriggerName {
    param($Value)
    $map = @{
        "-1" = "mixed"
        "0" = "none"
        "1" = "on-page-click"
        "2" = "with-previous"
        "3" = "after-previous"
        "4" = "on-shape-click"
        "5" = "on-media-bookmark"
    }
    $key = [string]$Value
    if ($map.ContainsKey($key)) { return $map[$key] }
    return "unknown:$key"
}

function Capture-PrimaryScreen {
    param([string]$Path)
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    try {
        $graphics.CopyFromScreen(
            $bounds.Location,
            [System.Drawing.Point]::Empty,
            $bounds.Size
        )
        $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
    }
    finally {
        $graphics.Dispose()
        $bitmap.Dispose()
    }
    return @{
        path = $Path
        sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
        width = $bounds.Width
        height = $bounds.Height
    }
}

$fullPptx = [System.IO.Path]::GetFullPath($Pptx)
$fullManifest = [System.IO.Path]::GetFullPath($Manifest)
$fullOutput = [System.IO.Path]::GetFullPath($Output)

if (-not (Test-Path -LiteralPath $fullPptx)) { throw "PPTX not found: $fullPptx" }
if (-not (Test-Path -LiteralPath $fullManifest)) { throw "Manifest not found: $fullManifest" }

$manifestObj = Get-Content -Raw -LiteralPath $fullManifest | ConvertFrom-Json
$hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $fullPptx).Hash.ToLowerInvariant()
$hashMatch = ($hash -eq ([string]$manifestObj.pptx_sha256).ToLowerInvariant())

$result = [ordered]@{
    version = "0.1"
    kind = "powerpoint-native-qa-evidence"
    timestamp_utc = [DateTime]::UtcNow.ToString("o")
    machine = [ordered]@{
        computer_name = $env:COMPUTERNAME
        os_version = [Environment]::OSVersion.VersionString
        powershell_version = $PSVersionTable.PSVersion.ToString()
        is_64_bit_process = [Environment]::Is64BitProcess
    }
    artifact = [ordered]@{
        path = $fullPptx
        sha256 = $hash
        expected_sha256 = [string]$manifestObj.pptx_sha256
        exact_hash_match = $hashMatch
    }
    powerpoint = [ordered]@{
        com_created = $false
        version = $null
        build = $null
        presentation_opened = $false
        slide_count = $null
    }
    slides = @()
    slideshow = [ordered]@{
        attempted = [bool]$RunSlideshow
        success = $false
        slides = @()
    }
    errors = @()
    claim_boundary = [ordered]@{
        native_application_parse_verified = $false
        native_click_execution_verified = $false
        visual_capture_created = $false
        visual_state_verified = $false
    }
}

if (-not $hashMatch) {
    $result.errors += "Exact PPTX SHA-256 does not match the QA manifest."
    $parent = Split-Path -Parent $fullOutput
    if ($parent -and -not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
    $result | ConvertTo-Json -Depth 30 | Set-Content -Encoding UTF8 -LiteralPath $fullOutput
    exit 2
}

$ppt = $null
$presentation = $null
$slideShowWindow = $null
$view = $null

try {
    $isWindows = ([Environment]::OSVersion.Platform -eq [PlatformID]::Win32NT)
    if (-not $isWindows) {
        throw "Microsoft PowerPoint COM probe requires Windows."
    }

    $ppt = New-Object -ComObject PowerPoint.Application
    $result.powerpoint.com_created = $true
    $result.powerpoint.version = Invoke-SafeValue { [string]$ppt.Version }
    $result.powerpoint.build = Invoke-SafeValue { [string]$ppt.Build }

    # msoTrue=-1, msoFalse=0. Open read-only with a window so slideshow APIs are available.
    $ppt.Visible = -1
    $presentation = $ppt.Presentations.Open($fullPptx, -1, 0, -1)
    $result.powerpoint.presentation_opened = $true
    $result.powerpoint.slide_count = [int]$presentation.Slides.Count

    for ($slideIndex=1; $slideIndex -le $presentation.Slides.Count; $slideIndex++) {
        $slide = $presentation.Slides.Item($slideIndex)
        $slideRecord = [ordered]@{
            index = $slideIndex
            name = Invoke-SafeValue { [string]$slide.Name }
            effect_count = 0
            effects = @()
            transition = [ordered]@{
                entry_effect = Invoke-SafeValue { [int]$slide.SlideShowTransition.EntryEffect }
                duration_seconds = Invoke-SafeValue { [double]$slide.SlideShowTransition.Duration }
                advance_on_click = Invoke-SafeValue { [int]$slide.SlideShowTransition.AdvanceOnClick }
                advance_on_time = Invoke-SafeValue { [int]$slide.SlideShowTransition.AdvanceOnTime }
                advance_time_seconds = Invoke-SafeValue { [double]$slide.SlideShowTransition.AdvanceTime }
            }
            sequence_error = $null
        }

        try {
            $sequence = $slide.TimeLine.MainSequence
            $count = [int]$sequence.Count
            $slideRecord.effect_count = $count

            for ($effectIndex=1; $effectIndex -le $count; $effectIndex++) {
                $effect = $sequence.Item($effectIndex)
                $shape = Invoke-SafeValue { $effect.Shape }
                $timing = Invoke-SafeValue { $effect.Timing }
                $triggerValue = if ($null -ne $timing) {
                    Invoke-SafeValue { [int]$timing.TriggerType }
                } else { $null }

                $behaviorTypes = @()
                $behaviorCount = Invoke-SafeValue { [int]$effect.Behaviors.Count }
                if ($null -ne $behaviorCount) {
                    for ($behaviorIndex=1; $behaviorIndex -le $behaviorCount; $behaviorIndex++) {
                        $behavior = Invoke-SafeValue { $effect.Behaviors.Item($behaviorIndex) }
                        if ($null -ne $behavior) {
                            $behaviorTypes += Invoke-SafeValue { [int]$behavior.Type }
                        }
                        Release-ComObjectSafe $behavior
                    }
                }

                $chartUnitEffect = $null
                if ($null -ne $shape) {
                    $chartUnitEffect = Invoke-SafeValue { [int]$shape.AnimationSettings.ChartUnitEffect }
                }

                $slideRecord.effects += [ordered]@{
                    index = $effectIndex
                    display_name = Invoke-SafeValue { [string]$effect.DisplayName }
                    effect_type = Invoke-SafeValue { [int]$effect.EffectType }
                    exit = Invoke-SafeValue { [int]$effect.Exit }
                    shape_id = if ($null -ne $shape) { Invoke-SafeValue { [int]$shape.Id } } else { $null }
                    shape_name = if ($null -ne $shape) { Invoke-SafeValue { [string]$shape.Name } } else { $null }
                    chart_unit_effect = $chartUnitEffect
                    behavior_types = $behaviorTypes
                    timing = [ordered]@{
                        trigger_type = $triggerValue
                        trigger_name = if ($null -ne $triggerValue) { Get-TriggerName $triggerValue } else { $null }
                        duration_seconds = if ($null -ne $timing) { Invoke-SafeValue { [double]$timing.Duration } } else { $null }
                        trigger_delay_seconds = if ($null -ne $timing) { Invoke-SafeValue { [double]$timing.TriggerDelayTime } } else { $null }
                        auto_reverse = if ($null -ne $timing) { Invoke-SafeValue { [int]$timing.AutoReverse } } else { $null }
                        repeat_count = if ($null -ne $timing) { Invoke-SafeValue { [double]$timing.RepeatCount } } else { $null }
                        rewind_at_end = if ($null -ne $timing) { Invoke-SafeValue { [int]$timing.RewindAtEnd } } else { $null }
                    }
                }

                Release-ComObjectSafe $timing
                Release-ComObjectSafe $shape
                Release-ComObjectSafe $effect
            }
            Release-ComObjectSafe $sequence
        }
        catch {
            $slideRecord.sequence_error = $_.Exception.Message
        }

        $result.slides += $slideRecord
        Release-ComObjectSafe $slide
    }

    $result.claim_boundary.native_application_parse_verified = (
        $result.powerpoint.presentation_opened -and
        ([int]$result.powerpoint.slide_count -eq [int]$manifestObj.slide_count)
    )

    if ($RunSlideshow) {
        $settings = $presentation.SlideShowSettings
        $slideShowWindow = $settings.Run()
        Start-Sleep -Milliseconds 500
        $view = $slideShowWindow.View

        $captureDir = $null
        if ($CaptureScreenshots) {
            $captureDir = Join-Path (Split-Path -Parent $fullOutput) "powerpoint-qa-captures"
            New-Item -ItemType Directory -Path $captureDir -Force | Out-Null
        }

        foreach ($expectedSlide in $manifestObj.slides) {
            $index = [int]$expectedSlide.index
            # ResetSlide=msoTrue so each slide starts from its authored pre-animation state.
            $view.GotoSlide($index, -1)
            Start-Sleep -Milliseconds 250
            # msoClickStateBeforeAutomaticAnimations = -1.
            $view.GotoClick(-1)
            Start-Sleep -Milliseconds 150

            $nativeClickCount = [int]$view.GetClickCount()
            $slideShowRecord = [ordered]@{
                index = $index
                expected_click_count = [int]$expectedSlide.expected_click_count
                native_click_count = $nativeClickCount
                initial_click_index = [int]$view.GetClickIndex()
                clicks = @()
            }

            if ($CaptureScreenshots) {
                $prePath = Join-Path $captureDir ("slide{0:D2}-click00.png" -f $index)
                $slideShowRecord.pre_click_capture = Capture-PrimaryScreen $prePath
            }

            for ($click=1; $click -le $nativeClickCount; $click++) {
                $before = [int]$view.GetClickIndex()
                $view.GotoClick($click)
                Start-Sleep -Milliseconds $ClickPauseMs
                $after = [int]$view.GetClickIndex()
                $clickRecord = [ordered]@{
                    click = $click
                    before_index = $before
                    after_index = $after
                    index_matches = ($after -eq $click)
                }
                if ($CaptureScreenshots) {
                    $capturePath = Join-Path $captureDir ("slide{0:D2}-click{1:D2}.png" -f $index,$click)
                    $clickRecord.capture = Capture-PrimaryScreen $capturePath
                }
                $slideShowRecord.clicks += $clickRecord
            }

            $result.slideshow.slides += $slideShowRecord
        }

        $result.slideshow.success = $true
        $allClickCountsMatch = $true
        $allIndicesMatch = $true
        foreach ($row in $result.slideshow.slides) {
            if ($row.native_click_count -ne $row.expected_click_count) {
                $allClickCountsMatch = $false
            }
            foreach ($clickRow in $row.clicks) {
                if (-not $clickRow.index_matches) { $allIndicesMatch = $false }
            }
        }
        $result.claim_boundary.native_click_execution_verified = (
            $result.claim_boundary.native_application_parse_verified -and
            $allClickCountsMatch -and
            $allIndicesMatch
        )
        $result.claim_boundary.visual_capture_created = [bool]$CaptureScreenshots

        Release-ComObjectSafe $settings
    }
}
catch {
    $result.errors += $_.Exception.Message
}
finally {
    if ($null -ne $view) {
        try { $view.Exit() } catch {}
    }
    Release-ComObjectSafe $view
    Release-ComObjectSafe $slideShowWindow
    if ($null -ne $presentation) {
        try { $presentation.Close() } catch {}
    }
    Release-ComObjectSafe $presentation
    if ($null -ne $ppt) {
        try { $ppt.Quit() } catch {}
    }
    Release-ComObjectSafe $ppt

    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()

    $parent = Split-Path -Parent $fullOutput
    if ($parent -and -not (Test-Path $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }
    $result | ConvertTo-Json -Depth 30 | Set-Content -Encoding UTF8 -LiteralPath $fullOutput
}

if ($result.errors.Count -gt 0) { exit 1 }
if (-not $result.claim_boundary.native_application_parse_verified) { exit 3 }
if ($RunSlideshow -and -not $result.claim_boundary.native_click_execution_verified) { exit 4 }
exit 0
