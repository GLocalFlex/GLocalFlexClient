 #!/bin/bash

for i in {1..5}
#load .env file
source ../env
do
    python3 main.py buy -r 10 -s 0 --host $HOST -u $USERNAME -p $PASSWORD --log&
    python3 main.py sell  -r 10 -s 0 --host $HOST -u $USERNAME -p $PASSWORD --log&
done
