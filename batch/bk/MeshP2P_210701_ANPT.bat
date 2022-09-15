rem del  "C:\HTZ ANP Project\KML\*.KML"
rem del  "C:\HTZ ANP Project\KML\*.CSV"

rem coverage calculation
"C:\ATDI\HTZ warfare x64 Unicode\HTZwx64u.exe" "C:\HTZ ANP Project\SouthKorea_20m_ANPT.PRO" -ADMIN 1022 1 10

rem composite coverage export (dBm) - active sites only
rem "C:\ATDI\HTZ warfare x64 Unicode\HTZwx64u.exe" "C:\HTZ ANP Project\SouthKorea_20m_ANPT.PRO" -ADMIN 1005 1000 "C:\HTZ ANP Project\KML\"

rem : P2P (layer 1) RF analysis. Building the connection Matrix
"C:\ATDI\HTZ warfare x64 Unicode\HTZwx64u.exe" "C:\HTZ ANP Project\SouthKorea_20m_ANPT.PRO" -ADMIN 1024 1000 "C:\HTZ ANP Project\KML\"

rem : Analysing the connection matrix and establish layer 3 routing, RF analysis and so on..
"C:\ATDI\HTZ warfare x64 Unicode\Mesh.exe" -i "C:\HTZ ANP Project\KML\*P2P.CSV" -t -95 -h 4

rem : Search for nodes (Range Extenders) to interconnect isolated clusters - up to 5 nodes to search
"C:\ATDI\HTZ warfare x64 Unicode\HTZwx64u.exe" "C:\HTZ ANP Project\SouthKorea_20m_ANPT.PRO" -ADMIN 1025 5 "C:\HTZ ANP Project\KML\"

rem : Analysing the connection matrix and establish layer 3 routing, RF analysis and so on..
"C:\ATDI\HTZ warfare x64 Unicode\Mesh.exe" -i "C:\HTZ ANP Project\KML\*NODES.CSV" -t -95 -h 4

pause
