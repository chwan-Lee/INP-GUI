rem back up
move "C:\gui\outcome\NODE\*.*" "C:\gui\outcome\NODE\Backup\" 

rem coverage calculation
"C:\ATDI\HTZ warfare x64\HTZwx64.exe" "C:\HTZ PROJECT\INP.PRO" -ADMIN 1022 1 30

rem : Search for nodes (Range Extenders) to interconnect isolated clusters - up to 5 nodes to search
"C:\ATDI\HTZ warfare x64\HTZwx64.exe" "C:\HTZ PROJECT\INP.PRO" -ADMIN 1025 4 "C:\gui\outcome\NODE"

rem : Analysing the connection matrix and establish layer 3 routing, RF analysis and so on..
rem "C:\ATDI\HTZ warfare x64\Mesh\Mesh.exe" -i "C:\gui\outcome\NODE\*NODES.CSV" -t -137 -h 4

