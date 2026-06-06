# === Obsidian Image Optimizer (JPG -> WebP-in-JPG) ===
# Converts JPGs to WebP internally while keeping .jpg filenames
# Ensures Obsidian embeds never break

$AttachmentsFolder = "C:\Users\Trader\Documents\AJZStrategies_TradingJournal\Trading Journal\Attachments"
$LogFile = "$AttachmentsFolder\compression_log_$(Get-Date -Format yyyyMMdd).txt"

Add-Content $LogFile "=== WebP Compression Run $(Get-Date) ==="

Get-ChildItem -Path $AttachmentsFolder -Filter *.jpg -Recurse | ForEach-Object {
    $Original = $_.FullName
    $TempFile = "$($Original).tmp"

    # Convert JPG -> WebP (quality 75)
    magick "$Original" -quality 75 "$TempFile.webp"

    if (Test-Path "$TempFile.webp") {
        # Re-encode WebP back into a .jpg container (still tiny)
        magick "$TempFile.webp" "$TempFile.jpg"

        # Overwrite original
        Move-Item -Force "$TempFile.jpg" "$Original"

        # Cleanup
        Remove-Item "$TempFile.webp" -Force

        Add-Content $LogFile "Compressed: $Original"
    } else {
        Add-Content $LogFile "FAILED: $Original"
    }
}

Add-Content $LogFile "=== Completed ==="