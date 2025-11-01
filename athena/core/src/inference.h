// core/src/inference.h
#pragma once
#include "dispatcher.h"
#include <vector>

class InferenceEngine
{
public:
    InferenceEngine() = default;
    // simulate running inference on a batch (synchronous)
    void run_batch(const std::vector<RequestPtr> &batch);
};
