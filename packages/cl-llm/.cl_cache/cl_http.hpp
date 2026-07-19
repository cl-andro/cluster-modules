// TRANSPILE ERROR
Syntax Error at line 4:30
        2 | // Wraps the native http_get/http_post functions
        3 | 
  >>    4 | fn get(url: string, headers: [string]) -> string:
       |                              ^
        5 |     return http_get(url, headers)
        6 | 
Expected: newline, name