move "C:\gui\outcome\COV\*.*" "C:\gui\outcome\COV\Backup\" 

rem move "C:\gui\outcome\p2p\*.*" "C:\gui\outcome\p2p\Backup\" 

rem move "C:\gui\outcome\node\*.*" "C:\gui\outcome\node\Backup\"

rem coverage calculation
"C:\ATDI\HTZ warfare x64\HTZwx64.exe" "C:\HTZ PROJECT\INP.PRO" -ADMIN 1018 0 1000

rem coverage calculation site by site export
"C:\ATDI\HTZ warfare x64\HTZwx64.exe" "C:\HTZ PROJECT\INP.PRO" -ADMIN 1005 1000 "C:\gui\outcome\COV\"

