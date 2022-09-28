move "C:\gui\outcome\P2P\hctr\*.*" "C:\gui\outcome\P2P\hctr\Backup\" 

rem coverage calculation
rem "C:\ATDI\HTZ warfare x64\HTZwx64.exe" "C:\HTZ PROJECT\INP.PRO" -ADMIN 1022 1 30

rem : P2P (layer 1) RF analysis. Building the connection Matrix
"C:\ATDI\HTZ warfare x64\HTZwx64.exe" "C:\HTZ PROJECT\INP.PRO" -ADMIN 1024 1000 "C:\gui\outcome\P2P\hctr\"

rem : Analysing the connection matrix and establish layer 3 routing, RF analysis and so on..
rem "C:\ATDI\HTZ warfare x64\Mesh\Mesh.exe" -i "C:\gui\outcome\p2p\*P2P.CSV" -t -120 -h 4
