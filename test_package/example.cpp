#include <iostream>
#include <steam/steamnetworkingsockets.h>

int main()
{
    SteamDatagramErrMsg errMsg;
    if (!GameNetworkingSockets_Init(nullptr, errMsg)) {
        std::cerr << "GameNetworkingSockets_Init failed: " << errMsg << std::endl;
        return 1;
    }

    std::cout << "Started GameNetworkingSockets!" << std::endl;

    GameNetworkingSockets_Kill();
    return 0;
}
