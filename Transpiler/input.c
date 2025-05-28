#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int fibonacci(int n) {
    if ((n <= 1)) {
        return n;
    }
    return (fibonacci((n - 1)) + fibonacci((n - 2)));
}

int main(void) {
    printf("%s\n", "Fibonacci Series:");
    for (int i = 0; (i < 10); i = (i + 1)) {
        printf("%d\n", fibonacci(i));
    }
    return 0;
}
