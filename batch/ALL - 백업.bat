rem del  "C:\gui\outcome\*.KML"
rem del  "C:\gui\outcome\*.CSV"

rem coverage calculation
"C:\ATDI\HTZ warfare x64\HTZwx64.exe" "C:\HTZ ANP Project\SouthKorea_20m_ANPT.PRO" -ADMIN 1022 1 30

rem : P2P (layer 1) RF analysis. Building the connection Matrix
"C:\ATDI\HTZ warfare x64\HTZwx64.exe" "C:\HTZ ANP Project\SouthKorea_20m_ANPT.PRO" -ADMIN 1024 1000 "C:\gui\outcome\"

rem : Analysing the connection matrix and establish layer 3 routing, RF analysis and so on..
"C:\ATDI\HTZ warfare x64\Mesh.exe" -i "C:\gui\outcome\*P2P.CSV" -t -100 -h 4

rem : Search for nodes (Range Extenders) to interconnect isolated clusters - up to 5 nodes to search
"C:\ATDI\HTZ warfare x64\HTZwx64.exe" "C:\HTZ ANP Project\SouthKorea_20m_ANPT.PRO" -ADMIN 1025 10 "C:\gui\outcome\"

rem : Analysing the connection matrix and establish layer 3 routing, RF analysis and so on..
"C:\ATDI\HTZ warfare x64\Mesh.exe" -i "C:\gui\outcome\*NODES.CSV" -t -100 -h 4

