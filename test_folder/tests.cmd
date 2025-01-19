@echo off

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c all -p rel-base -fmt inline -o file -f results1.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c all -p rel-base -fmt inline -o file -f results1.txt
echo --
comp results1.txt PASSED\results1.txt /M
pause

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-only -p rel-base -fmt inline -o file -f results2.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-only -p rel-base -fmt inline -o file -f results2.txt
echo --
comp results2.txt PASSED\results2.txt /M
pause

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-1st-last-file -p rel-base -fmt inline -o file -f results3.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-1st-last-file -p rel-base -fmt inline -o file -f results3.txt
echo --
comp results3.txt PASSED\results3.txt /M
pause

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c files-only -p rel-base -fmt inline -o file -f results4.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c files-only -p rel-base -fmt inline -o file -f results4.txt
echo --
comp results4.txt PASSED\results4.txt /M
pause

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c all -p rel-base -fmt summary -o file -f results5.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c all -p rel-base -fmt summary -o file -f results5.txt
echo --
comp results5.txt PASSED\results5.txt /M
pause

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-only -p rel-base -fmt summary -o file -f results6.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-only -p rel-base -fmt summary -o file -f results6.txt
echo --
comp results6.txt PASSED\results6.txt /M
pause

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-1st-last-file -p rel-base -fmt summary -o file -f results7.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-1st-last-file -p rel-base -fmt summary -o file -f results7.txt
echo --
comp results7.txt PASSED\results7.txt /M
pause

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c files-only -p rel-base -fmt summary -o file -f results8.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c files-only -p rel-base -fmt summary -o file -f results8.txt
echo --
comp results8.txt PASSED\results8.txt /M
pause

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c all -p rel -fmt inline -o file -f results9.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c all -p rel -fmt inline -o file -f results9.txt
echo --
comp results9.txt PASSED\results9.txt /M
pause

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-only -p rel -fmt inline -o file -f resultsA.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-only -p rel -fmt inline -o file -f resultsA.txt
echo --
comp resultsA.txt PASSED\resultsA.txt /M
pause

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-1st-last-file -p rel -fmt inline -o file -f resultsB.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-1st-last-file -p rel -fmt inline -o file -f resultsB.txt
echo --
comp resultsB.txt PASSED\resultsB.txt /M
pause

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c files-only -p rel -fmt inline -o file -f resultsC.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c files-only -p rel -fmt inline -o file -f resultsC.txt
echo --
comp resultsC.txt PASSED\resultsC.txt /M
pause

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c all -p rel -fmt summary -o file -f resultsD.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c all -p rel -fmt summary -o file -f resultsD.txt
echo --
comp resultsD.txt PASSED\resultsD.txt /M
pause

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-only -p rel -fmt summary -o file -f resultsE.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-only -p rel -fmt summary -o file -f resultsE.txt
echo --
comp resultsE.txt PASSED\resultsE.txt /M
pause

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-1st-last-file -p rel -fmt summary -o file -f resultsF.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c dirs-1st-last-file -p rel -fmt summary -o file -f resultsF.txt
echo --
comp resultsF.txt PASSED\resultsF.txt /M
pause

..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c files-only -p rel -fmt summary -o file -f resultsG.txt
echo. 
echo ..\listall.py -d "." -s iname -o stdout -xd "*exclude*" -xd "PASSED" -xd "results*" -c files-only -p rel -fmt summary -o file -f resultsG.txt
echo --
comp resultsG.txt PASSED\resultsG.txt /M
pause