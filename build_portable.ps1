param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BuildRoot = Join-Path $ProjectRoot "build_portable"
$WorkRoot = Join-Path $BuildRoot "work"
$DistRoot = Join-Path $BuildRoot "dist"
$SpecRoot = Join-Path $BuildRoot "spec"
$ReleaseRoot = Join-Path $ProjectRoot "release"
$PortableRoot = Join-Path $ReleaseRoot "Good-GYM-Portable"
$ZipPath = Join-Path $ReleaseRoot "Good-GYM-Portable.zip"
$AssetsDir = Join-Path $ProjectRoot "assets"
$ModelsDir = Join-Path $ProjectRoot "models"
$ExercisesFile = Join-Path $ProjectRoot "data\exercises.json"

function Assert-InProject([string]$Path) {
    $resolvedParent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $resolvedParent)) {
        New-Item -ItemType Directory -Force -Path $resolvedParent | Out-Null
    }
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $rootPath = [System.IO.Path]::GetFullPath($ProjectRoot)
    if (-not $fullPath.StartsWith($rootPath, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to touch path outside project: $fullPath"
    }
}

Assert-InProject $BuildRoot
Assert-InProject $PortableRoot
Assert-InProject $ZipPath

if (Test-Path -LiteralPath $BuildRoot) {
    Remove-Item -LiteralPath $BuildRoot -Recurse -Force
}
if (Test-Path -LiteralPath $PortableRoot) {
    Remove-Item -LiteralPath $PortableRoot -Recurse -Force
}
if (Test-Path -LiteralPath $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}

New-Item -ItemType Directory -Force -Path $BuildRoot, $ReleaseRoot | Out-Null

$args = @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--windowed",
    "--onedir",
    "--name", "Good-GYM",
    "--distpath", $DistRoot,
    "--workpath", $WorkRoot,
    "--specpath", $SpecRoot,
    "--add-data", "$AssetsDir;assets",
    "--add-data", "$ModelsDir;models",
    "--add-data", "$ExercisesFile;data",
    "--hidden-import", "PyQt5.QtMultimedia",
    "--hidden-import", "rtmlib.tools.solution.wholebody",
    "--hidden-import", "rtmlib.tools.object_detection.yolox",
    "--hidden-import", "rtmlib.tools.pose_estimation.rtmpose",
    "--exclude-module", "torch",
    "--exclude-module", "torchvision",
    "--exclude-module", "torchaudio",
    "--exclude-module", "tensorflow",
    "--exclude-module", "paddle",
    "--exclude-module", "transformers",
    "--exclude-module", "matplotlib",
    "--exclude-module", "pandas",
    "--exclude-module", "sklearn",
    "--exclude-module", "librosa",
    "--exclude-module", "onnx",
    "--exclude-module", "onnx.reference"
)

$iconPath = Join-Path $ProjectRoot "assets\Logo.ico"
if (Test-Path -LiteralPath $iconPath) {
    $args += @("--icon", $iconPath)
}

$args += "run.py"

Push-Location $ProjectRoot
try {
    & $Python @args
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed with exit code $LASTEXITCODE"
    }

    $AppDir = Join-Path $DistRoot "Good-GYM"
    if (-not (Test-Path -LiteralPath (Join-Path $AppDir "Good-GYM.exe"))) {
        throw "PyInstaller did not produce Good-GYM.exe"
    }

    $ExternalDataDir = Join-Path $AppDir "data"
    New-Item -ItemType Directory -Force -Path $ExternalDataDir | Out-Null
    Copy-Item -LiteralPath (Join-Path $ProjectRoot "data\exercises.json") -Destination $ExternalDataDir -Force

    New-Item -ItemType Directory -Force -Path $PortableRoot | Out-Null
    Copy-Item -LiteralPath $AppDir -Destination $PortableRoot -Recurse -Force

    $ArchiveSource = Join-Path $PortableRoot "Good-GYM"
    $Compressed = $false
    for ($Attempt = 1; $Attempt -le 3 -and -not $Compressed; $Attempt++) {
        try {
            Start-Sleep -Seconds 2
            Compress-Archive -LiteralPath $ArchiveSource -DestinationPath $ZipPath -Force
            $Compressed = $true
        }
        catch {
            if ($Attempt -eq 3) {
                throw
            }
            Write-Warning "Archive attempt $Attempt failed. Retrying..."
        }
    }

    Write-Host "Portable folder: $PortableRoot"
    Write-Host "Portable zip: $ZipPath"
}
finally {
    Pop-Location
}
