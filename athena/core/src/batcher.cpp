// core/src/batcher.cpp
#include "batcher.h"
#include <chrono>
#include <iostream>

DynamicBatcher::DynamicBatcher(std::shared_ptr<Dispatcher> dispatcher,
                               size_t max_batch_size,
                               std::chrono::milliseconds max_wait,
                               Handler handler)
    : dispatcher_(dispatcher),
      max_batch_size_(max_batch_size),
      max_wait_(max_wait),
      handler_(handler)
{
}

DynamicBatcher::~DynamicBatcher()
{
    stop();
}

void DynamicBatcher::start()
{
    running_ = true;
    thr_ = std::thread(&DynamicBatcher::loop, this);
}

void DynamicBatcher::stop()
{
    if (running_)
    {
        running_ = false;
        if (thr_.joinable())
            thr_.join();
    }
}

void DynamicBatcher::loop()
{
    while (running_)
    {
        // pop up to max_batch_size_, but wait up to max_wait_ for items.
        std::vector<RequestPtr> batch = dispatcher_->pop_batch(max_batch_size_, max_wait_);
        if (!batch.empty())
        {
            // For now, just call handler directly
            handler_(batch);
        }
        // small sleep to avoid tight loop if nothing
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
}
