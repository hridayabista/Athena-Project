// core/tests/test_batcher.cpp
#define CATCH_CONFIG_RUNNER
#include <catch2/catch_all.hpp>
#include "../src/dispatcher.h"
#include "../src/batcher.h"
#include "../src/inference.h"
#include <memory>
#include <atomic>

TEST_CASE("batcher groups up to max size", "[batcher]")
{
    auto dispatcher = std::make_shared<Dispatcher>();
    std::atomic<int> processed_batches{0};
    std::atomic<int> total_processed{0};

    DynamicBatcher batcher(dispatcher, 4, std::chrono::milliseconds(50),
                           [&](const std::vector<RequestPtr> &batch)
                           {
                               processed_batches.fetch_add(1);
                               total_processed.fetch_add(static_cast<int>(batch.size()));
                           });

    batcher.start();

    // push 10 requests quickly
    for (int i = 0; i < 10; i++)
    {
        auto r = std::make_shared<Request>();
        r->id = i;
        r->deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(100);
        dispatcher->push_request(r);
    }

    // wait for processing
    std::this_thread::sleep_for(std::chrono::milliseconds(300));
    batcher.stop();

    REQUIRE(total_processed.load() == 10);
    REQUIRE(processed_batches.load() >= 3); // 4+4+2 => 3 batches expected
}

int main(int argc, char *argv[])
{
    return Catch::Session().run(argc, argv);
}
