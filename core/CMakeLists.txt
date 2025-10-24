cmake_minimum_required(VERSION 3.16)
project(athena_core VERSION 0.1 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(Threads REQUIRED)

add_library(athena_core SHARED src/dispatcher.cpp src/batcher.cpp src/inference.cpp)
target_include_directories(athena_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(athena_core PRIVATE Threads::Threads)

# tests
enable_testing()
add_subdirectory(tests)
