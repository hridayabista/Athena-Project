// core/src/server.cpp
#include "dispatcher.h"
#include "batcher.h"
#include "inference.h"
#include <memory>
#include <iostream>
#include <thread>
#include <chrono> // Best practice to include all standard library components used

int main()
{
    // Initialize core components
    auto dispatcher = std::make_shared<Dispatcher>();
    InferenceEngine engine;

    // Initialize and configure the batcher thread
    DynamicBatcher batcher(dispatcher,
                           /*max_batch_size=*/16,
                           std::chrono::milliseconds(10),
                           [&](const std::vector<RequestPtr> &batch)
                           {
                               // This lambda is the processing function that the batcher calls
                               engine.run_batch(batch);
                           });

    batcher.start();

    // enqueue some test requests at different rates
    for (int i = 0; i < 100; i++)
    {
        auto req = std::make_shared<Request>();
        req->id = i;
        req->payload = "hello";
        req->deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(50);

        // FIX: Renamed 'push' to 'push_request' to match dispatcher.h
        dispatcher->push_request(req);

        std::this_thread::sleep_for(std::chrono::milliseconds(2));
    }

    // Allow time for the batcher to process remaining requests
    std::this_thread::sleep_for(std::chrono::seconds(2));

    batcher.stop();
    std::cout << "Server finished\n";
    return 0;
}