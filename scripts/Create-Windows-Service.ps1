# Run from an elevated command prompt
# https://docs.microsoft.com/en-us/aspnet/core/host-and-deploy/windows-service?view=aspnetcore-3.0

$cwd = (Get-Item -Path ".\").FullName

dotnet publish --configuration Release

sc create ElectionGuardService binPath="${cwd}\ElectionGuard.WebAPI\bin\Release\netcoreapp3.0\publish\ElectionGuard.WebAPI.exe"