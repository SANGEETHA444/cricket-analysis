# Get MongoDB installation directory
$mongoPath = "C:\Program Files\MongoDB\Server\6.0\bin\mongod.exe"

# Check if MongoDB exists
if (-not (Test-Path $mongoPath)) {
    Write-Host "MongoDB not found at expected location. Please check installation path."
    exit 1
}

# Start MongoDB
Write-Host "Starting MongoDB..."
Start-Process -FilePath $mongoPath -ArgumentList "--dbpath C:\data\db" -NoNewWindow

# Wait for MongoDB to start
Start-Sleep -Seconds 5

# Check MongoDB connection
try {
    $mongo = New-Object -ComObject "MongoDB.Driver.MongoClient" -ArgumentList "mongodb://localhost:27017"
    $mongo.GetServer().GetDatabase("admin").RunCommand("{ping:1}")
    Write-Host "MongoDB connection successful"
} catch {
    Write-Host "Failed to connect to MongoDB: $_"
    exit 1
}

exit 0
