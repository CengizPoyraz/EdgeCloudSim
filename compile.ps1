$projectPath = "c:\PROJECTS\Git\EdgeCloudSim"
cd $projectPath

# Create output directory
New-Item -ItemType Directory -Path "out" -Force | Out-Null
Write-Host "Created/verified out directory"

# Get all JAR files and build classpath
$jars = Get-ChildItem lib\*.jar | ForEach-Object { $_.FullName }
$classpath = $jars -join ";"
Write-Host "Classpath built with $($jars.Count) JARs"

# Get all Java sources
$sources = @(Get-ChildItem -Recurse src\*.java | ForEach-Object { $_.FullName })
Write-Host "Found $($sources.Count) Java source files"

# Compile
Write-Host "Starting compilation..."
& "c:\DEV\Java\jdk-25\bin\javac.exe" -d out -cp $classpath $sources 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "Compilation successful!"
} else {
    Write-Host "Compilation failed with exit code: $LASTEXITCODE"
    exit 1
}
