 #!/bin/bash

#python3 main.py buy -r 10 -s 0 --log&
#python3 main.py sell  -r 10 -s 0 --log&

#python3 main_threading.py buy -r 30 -s 0 --log&
#python3 main_threading.py sell  -r 30 -s 0 --log&

for i in {1..10}
do
    python3 main.py buy -r 10 -s 0 --log&
    python3 main.py sell  -r 10 -s 0 --log&
done


#if number of loops is about >8, SSL errors appear

# for i in {1..5}
# do
#     python3 main_threading.py buy -r 5 -s 0 --log&
#     python3 main_threading.py sell  -r 5 -s 0 --log&
# done
