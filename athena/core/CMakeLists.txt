cmake_minimum_required(VERSION 3.16)
project(athena_core LANGUAGES CXX)

# --------------------------------------------------------------------------
# Global configuration
# --------------------------------------------------------------------------
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# --------------------------------------------------------------------------
# Dependencies: Protobuf + gRPC
# --------------------------------------------------------------------------
find_package(Protobuf REQUIRED)
find_package(gRPC CONFIG REQUIRED)
find_package(Threads REQUIRED)

# --------------------------------------------------------------------------
# Proto file configuration
# --------------------------------------------------------------------------
set(PROTO_FILE ${CMAKE_SOURCE_DIR}/../proto/inference.proto)
get_filename_component(PROTO_DIR ${PROTO_FILE} DIRECTORY)

# Generated files
set(PROTO_PB_SRCS ${CMAKE_CURRENT_BINARY_DIR}/inference.pb.cc)
set(PROTO_PB_HDRS ${CMAKE_CURRENT_BINARY_DIR}/inference.pb.h)
set(PROTO_GRPC_SRCS ${CMAKE_CURRENT_BINARY_DIR}/inference.grpc.pb.cc)
set(PROTO_GRPC_HDRS ${CMAKE_CURRENT_BINARY_DIR}/inference.grpc.pb.h)

# Locate protoc and grpc_cpp_plugin
if(NOT Protobuf_PROTOC_EXECUTABLE)
    message(FATAL_ERROR "protoc not found! Ensure protobuf-compiler is installed.")
endif()

find_program(GRPC_CPP_PLUGIN_EXECUTABLE grpc_cpp_plugin
    PATHS /usr/local/bin /usr/bin
)
if(NOT GRPC_CPP_PLUGIN_EXECUTABLE)
    message(FATAL_ERROR "grpc_cpp_plugin not found. Please install gRPC development tools.")
endif()

# --------------------------------------------------------------------------
# Custom commands for code generation
# --------------------------------------------------------------------------
add_custom_command(
    OUTPUT ${PROTO_PB_SRCS} ${PROTO_PB_HDRS}
    COMMAND ${Protobuf_PROTOC_EXECUTABLE}
    ARGS --proto_path=${PROTO_DIR}
         --cpp_out=${CMAKE_CURRENT_BINARY_DIR}
         ${PROTO_FILE}
    DEPENDS ${PROTO_FILE}
    COMMENT "Generating C++ Protobuf sources from ${PROTO_FILE}"
)

add_custom_command(
    OUTPUT ${PROTO_GRPC_SRCS} ${PROTO_GRPC_HDRS}
    COMMAND ${Protobuf_PROTOC_EXECUTABLE}
    ARGS --proto_path=${PROTO_DIR}
         --grpc_out=${CMAKE_CURRENT_BINARY_DIR}
         --plugin=protoc-gen-grpc=${GRPC_CPP_PLUGIN_EXECUTABLE}
         ${PROTO_FILE}
    DEPENDS ${PROTO_FILE}
    COMMENT "Generating C++ gRPC sources from ${PROTO_FILE}"
)

# --------------------------------------------------------------------------
# Library target: athena_core
# --------------------------------------------------------------------------
add_library(athena_core SHARED
    src/dispatcher.cpp
    src/batcher.cpp
    src/inference.cpp
    ${PROTO_PB_SRCS}
    ${PROTO_PB_HDRS}
)

target_include_directories(athena_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/src
    ${CMAKE_CURRENT_BINARY_DIR}
    ${PROTO_DIR}
    ${Protobuf_INCLUDE_DIRS}
)

target_link_libraries(athena_core PRIVATE
    gRPC::grpc++
    gRPC::gpr
    ${Protobuf_LIBRARIES}
    Threads::Threads
    pthread
)

target_compile_options(athena_core PRIVATE -Wall -Wextra -Wpedantic)

# --------------------------------------------------------------------------
# Executable target: server
# --------------------------------------------------------------------------
add_executable(server
    src/server.cpp
    src/grpc_server.cpp
    ${PROTO_GRPC_SRCS}
    ${PROTO_GRPC_HDRS}
)

target_include_directories(server PRIVATE
    ${CMAKE_CURRENT_BINARY_DIR}
    ${PROTO_DIR}
)

target_link_libraries(server PRIVATE
    athena_core
    gRPC::grpc++
    ${Protobuf_LIBRARIES}
)

# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------
enable_testing()
add_subdirectory(tests)
