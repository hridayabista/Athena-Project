# core/tests/CMakeLists.txt
# Bring in Catch2 via FetchContent for testing
include(FetchContent)
FetchContent_Declare(
  catch2
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG v3.5.2
)
FetchContent_MakeAvailable(catch2)

add_executable(test_batcher test_batcher.cpp)
target_link_libraries(test_batcher PRIVATE athena_core Catch2::Catch2WithMain pthread)
add_test(NAME test_batcher COMMAND test_batcher)
