// Cluster Auto-Generated C++ Code (Module)
#pragma once
#include "cluster_stdlib.hpp"
#include <memory>
#include <sstream>
#include <type_traits>
#include <format>

namespace cl_json {
inline string parse(string text) {
    return json_parse(text);
}

inline string get_item(string d, string key) {
    return json_get(d, key);
}

inline string stringify(string obj) {
    return to_text(obj);
}

inline string pretty(string d) {
    return d;
}

}
