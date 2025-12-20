$projectPath = "c:\PROJECTS\Git\EdgeCloudSim"
cd $projectPath

# Get all JAR files and build classpath
$jars = @(Get-ChildItem lib\*.jar | ForEach-Object { $_.FullName })
$classpath = "out;" + ($jars -join ";")

Write-Host "Running MainApp..."
Write-Host "Classpath: $classpath"

& "c:\DEV\Java\jdk-25\bin\java.exe" -cp $classpath "edu.boun.edgecloudsim.applications.energy_aware_scenario.MainApp" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Application exited with code: $LASTEXITCODE"
}
