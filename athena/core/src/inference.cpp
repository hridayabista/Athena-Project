// core/src/inference.cpp
#include "inference.h"
#include <thread>
#include <chrono>
#include <iostream>

void InferenceEngine::run_batch(const std::vector<RequestPtr> &batch)
{
    // Mock work to simulate inference latency that grows slightly with batch size
    int batch_size = static_cast<int>(batch.size());
    int base_ms = 2;     // base latency
    int per_item_ms = 1; // per-request cost
    int total_ms = base_ms + per_item_ms * batch_size;
    std::this_thread::sleep_for(std::chrono::milliseconds(total_ms));
    // print debug
    std::cout << "[InferenceEngine] processed batch size=" << batch_size << " took " << total_ms << "ms\n";
}
