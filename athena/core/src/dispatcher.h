// core/src/dispatcher.h
#pragma once

#include <functional>
#include <memory>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <string>
#include <vector>

// Forward declaration
class Dispatcher;

struct Request
{
    int id;
    std::chrono::steady_clock::time_point deadline;
    std::string payload;
};

using RequestPtr = std::shared_ptr<Request>;

/**
 * @brief Handles dispatching and batching requests using a thread-safe queue.
 */
class Dispatcher
{
public:
    Dispatcher() = default; // Declaration of the default constructor

    // Public method declarations (signatures)
    void push_request(RequestPtr req);
    std::vector<RequestPtr> pop_batch(size_t max_size, std::chrono::milliseconds timeout);
    size_t size();

private:
    // Private members required for the implementation in dispatcher.cpp
    std::queue<RequestPtr> queue_;
    std::mutex mu_;
    std::condition_variable cv_;
};