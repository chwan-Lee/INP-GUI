rem cleanup
del  "3- Output\*.KMZ"
del  "3- Output\*.TIF"
del  "3- Output\*.TFW"
del  "3- Output\*.PRJ"
del  "3- Output\*.csv"

rem coverage calculation
"C:\ATDI\HTZ communications x64 Unicode\HTZcx64u.exe" "Auto_UNI.PRO" -ADMIN 1008 1 1000

rem composite coverage export (dBm) - active sites only
"C:\ATDI\HTZ communications x64 Unicode\HTZcx64u.exe" "Auto_UNI.PRO" -ADMIN 1005 1000 "C:\HTZ API Project\Project\3- Output"

rem best server (Use generic signal)
"C:\ATDI\HTZ communications x64 Unicode\HTZcx64u.exe" "Auto_UNI.PRO" -ADMIN 1003 1000  "C:\HTZ API Project\Project\3- Output"

rem Overlap - active sites only (Use generic signal)
"C:\ATDI\HTZ communications x64 Unicode\HTZcx64u.exe" "Auto_UNI.PRO" -ADMIN 1001 1000 "C:\HTZ API Project\Project\3- Output"

rem Load project and perform Combined Overlapping Map. Activated: STATUS_ELEMENT=0, De-activated: STATUS_ELEMENT=3
"C:\ATDI\HTZ communications x64 Unicode\HTZcx64u.exe" "Auto_UNI.PRO" -ADMIN 1021 1000 "C:\HTZ API Project\Project\3- Output"
