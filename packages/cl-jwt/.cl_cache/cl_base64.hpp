// Cluster Auto-Generated C++ Code (Module)
#pragma once
#include "cluster_stdlib.hpp"
#include <memory>
#include <sstream>
#include <type_traits>
#include <format>

namespace cl_base64 {
inline string encode(string data) {
    string result = "";
    static const char chars[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    std::string in = data;
    std::string out;
    int val = 0, valb = -6;
    for (unsigned char c : in) { val = (val << 8) + c; valb += 8; while (valb >= 0) { out.push_back(chars[(val >> valb) & 0x3F]); valb -= 6; } }
    if (valb > -6) out.push_back(chars[((val << 8) >> (valb + 8)) & 0x3F]);
    while (out.size() % 4) out.push_back('=');
    result = out;
    return result;
}

inline string decode(string data) {
    string result = "";
    std::string in = data;
    std::string out;
    std::vector<int> T(256, -1);
    for (int i = 0; i < 64; i++) T["ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"[i]] = i;
    int val = 0, valb = -8;
    for (unsigned char c : in) { if (T[c] == -1) break; val = (val << 6) + T[c]; valb += 6; if (valb >= 0) { out.push_back(char((val >> valb) & 0xFF)); valb -= 8; } }
    result = out;
    return result;
}

}
