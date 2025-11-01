// core/src/dispatcher.cpp
#include "dispatcher.h"
#include <stdexcept>

// NOTE: Dispatcher::Dispatcher() = default; is defined in the header.

/**
 * @brief Adds a request to the queue and notifies a waiting thread.
 */
void Dispatcher::push_request(RequestPtr r)
{
    {
        // Renamed from 'push' to 'push_request' to match the header
        std::lock_guard<std::mutex> lk(mu_);
        queue_.push(r);
    }
    cv_.notify_one();
}

/**
 * @brief Pops up to max_items from the queue, waiting up to the timeout.
 */
std::vector<RequestPtr> Dispatcher::pop_batch(size_t max_items, std::chrono::milliseconds timeout)
{
    std::unique_lock<std::mutex> lk(mu_);

    // Wait until queue is non-empty or timeout expires
    if (queue_.empty())
    {
        cv_.wait_for(lk, timeout, [&]
                     { return !queue_.empty(); });
    }

    std::vector<RequestPtr> out;
    auto start = std::chrono::steady_clock::now();

    // Collect items until queue is empty, max_items is reached, or effective timeout occurs
    while (!queue_.empty() && out.size() < max_items)
    {
        out.push_back(queue_.front());
        queue_.pop();

        // Simple deadline check (kept the original logic for consistency)
        if (std::chrono::steady_clock::now() - start > timeout)
            break;
    }
    return out;
}

/**
 * @brief Returns the current size of the request queue.
 */
size_t Dispatcher::size()
{
    std::lock_guard<std::mutex> lk(mu_);
    return queue_.size();
}