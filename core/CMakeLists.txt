cmake_minimum_required(VERSION 3.16)
project(athena_core LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# library
add_library(athena_core SHARED
  src/dispatcher.cpp
  src/batcher.cpp
  src/inference.cpp
)

target_include_directories(athena_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_compile_options(athena_core PRIVATE -Wall -Wextra -Wpedantic)

# Example server binary (for local manual testing)
add_executable(server src/server.cpp)
target_link_libraries(server PRIVATE athena_core pthread)

# Tests
enable_testing()
add_subdirectory(tests)
