// core/src/server.cpp
#include "dispatcher.h"
#include "batcher.h"
#include "inference.h"
#include <memory>
#include <iostream>
#include <thread>
#include <chrono>
#include "grpc_server.h"

int main()
{
    // Initialize core components: Dispatcher manages the request queue.
    auto dispatcher = std::make_shared<Dispatcher>();
    InferenceEngine engine;

    // Initialize and configure the batcher thread (the worker).
    DynamicBatcher batcher(dispatcher,
                           /*max_batch_size=*/16,
                           std::chrono::milliseconds(10),
                           [&](const std::vector<RequestPtr> &batch)
                           {
                               // Processing function called by the batcher thread.
                               engine.run_batch(batch);
                           });

    batcher.start();

    // Start the gRPC server in a separate thread.
    std::thread grpc_thread([]
                            { run_grpc_server("0.0.0.0:50051"); });

    std::cout << "Server setup complete. Waiting for gRPC server to terminate.\n";

    // Wait for the gRPC thread to finish. This call blocks main() indefinitely.
    // The server must be externally signaled for graceful shutdown.
    grpc_thread.join();

    // NOTE: For proper exit, a signal handler should be implemented to stop
    // the gRPC server and call batcher.stop() before exiting.

    std::cout << "Server finished\n";
    return 0;
}