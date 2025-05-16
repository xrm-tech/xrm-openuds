Get-ChildItem -Recurse -File -Include *.py | 
Where-Object { 
    $_.FullName -notmatch '\\\.git|\\build|\\dart_tool|\\android\\app\\build|\\ios' 
} | 
ForEach-Object { 
    "`n`n=== Τΰιλ: $($_.FullName) ===`n" 
    Get-Content $_.FullName 
} | 
Out-File combined.txt