// core/src/batcher.h
#pragma once
#include "dispatcher.h" // Now correctly includes the definition of Dispatcher and RequestPtr
#include <functional>
#include <thread>
#include <atomic>

class DynamicBatcher
{
public:
    // handler receives a vector of requests to process
    using Handler = std::function<void(const std::vector<RequestPtr> &)>;

    DynamicBatcher(std::shared_ptr<Dispatcher> dispatcher,
                   size_t max_batch_size,
                   std::chrono::milliseconds max_wait,
                   Handler handler);

    ~DynamicBatcher();

    void start();
    void stop();

private:
    void loop();

    std::shared_ptr<Dispatcher> dispatcher_;
    size_t max_batch_size_;
    std::chrono::milliseconds max_wait_;
    Handler handler_;
    std::thread thr_;
    std::atomic<bool> running_{false};
};