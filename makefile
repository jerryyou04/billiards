# CC = clang
# CFLAGS = -Wall -std=c99 -pedantic

# all: myprog

# clean:
# 	rm -f *.o *.so myprog

# libphylib.so: phylib.o
# 	$(CC) phylib.o -shared -o libphylib.so

# phylib.o: phylib.c phylib.h
# 	$(CC) $(CFLAGS) -c phylib.c -fPIC -o phylib.o

# main.o: main.c phylib.h
# 	$(CC) $(CFLAGS) -c main.c -o main.o

# myprog: main.o libphylib.so
# 	$(CC) main.o -L. -lphylib -lm -o myprog
CC = clang
CFLAGS = -Wall -std=c99 -pedantic -fPIC

all: _phylib.so

clean:
	rm -f *.o *.so phylib_wrap.* phylib.py 

libphylib.so: phylib.o
	$(CC) phylib.o -shared -o libphylib.so -lm

phylib.o: phylib.c phylib.h
	$(CC) $(CFLAGS) -c phylib.c -o phylib.o

phylib_wrap.c: phylib.i
	swig -python phylib.i

phylib_wrap.o: phylib_wrap.c
	$(CC) $(CFLAGS) -c phylib_wrap.c -I/usr/include/python3.11 -o phylib_wrap.o

_phylib.so: phylib_wrap.o libphylib.so
	$(CC) phylib_wrap.o -shared -o _phylib.so -L. -lphylib -L/usr/lib/python3.11 -lpython3.11
