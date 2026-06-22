# This script copies the project into the target GitHub repository directory structure and commits locally.
param(
    [string]$TargetRepoUrl = 'https://github.com/PadmanabhanGit/DSA0513-QueryProcessing.git',
    [string]$TargetFolder = 'AI_Query_Optimizer'
)

# Usage: .\upload_to_target_repo.ps1

$cwd = Get-Location
$parent = Split-Path -Parent $cwd

# Clone target repo to a temp folder
$tmp = Join-Path $env:TEMP "target-repo-$(Get-Random)"
git clone $TargetRepoUrl $tmp

# Create folder and copy files
$dest = Join-Path $tmp $TargetFolder
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Write-Host "Copying files to $dest"
Copy-Item -Path "$cwd\*" -Destination $dest -Recurse -Force

cd $tmp
git add $TargetFolder
git commit -m "Add AI_Query_Optimizer app" -a | Out-Null
Write-Host "Committed changes. Now push to remote or open a PR as needed."
Write-Host "If you don't have write access to main, create a branch, push, and open a PR."

Write-Host "To push now run: git push origin main (or push a new branch)"