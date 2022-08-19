rem del  "C:\HTZ ANP Project\KML\*.KML"
rem del  "C:\HTZ ANP Project\KML\*.CSV"

rem coverage calculation
rem "C:\ATDI\HTZ warfare x64\HTZwx64.exe" "C:\HTZ ANP Project\SouthKorea_20m_ANPT.PRO" -ADMIN 1008 1 1000

rem composite coverage export (dBm) - active sites only
"C:\ATDI\HTZ warfare x64\HTZwx64.exe" "C:\HTZ ANP Project\SouthKorea_20m_ANPT.PRO" -ADMIN 1005 1000 "C:\HTZ ANP Project\KML\"

rem : P2P (layer 1) RF analysis. Building the connection Matrix
"C:\ATDI\HTZ warfare x64\HTZwx64.exe" "C:\HTZ ANP Project\SouthKorea_20m_ANPT.PRO" -ADMIN 1024 1000 "C:\HTZ ANP Project\KML\"

rem : Analysing the connection matrix and establish layer 3 routing, RF analysis and so on..
"C:\ATDI\HTZ warfare x64\Mesh\Mesh.exe" -i "C:\HTZ ANP Project\KML\*P2P.CSV" -t -100 -h 5

rem : Search for nodes (Range Extenders) to interconnect isolated clusters - up to 5 nodes to search
"C:\ATDI\HTZ warfare x64\HTZwx64.exe" "C:\HTZ ANP Project\SouthKorea_20m_ANPT.PRO" -ADMIN 1025 4 "C:\HTZ ANP Project\KML\"

rem : Analysing the connection matrix and establish layer 3 routing, RF analysis and so on..
"C:\ATDI\HTZ warfare x64\Mesh\Mesh.exe" -i "C:\HTZ ANP Project\KML\*NODES.CSV" -t -100 -h 5
