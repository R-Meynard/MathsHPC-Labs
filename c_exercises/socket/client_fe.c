#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>

int main(){
    // Etape 1 : creer le socket
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if(sock < 0){
        perror("socket");
        return 1;
    }
    printf("Socket cree : %d\n", sock);
    return 0;
}