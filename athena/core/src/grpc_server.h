// core/src/grpc_server.h
#pragma once
#include <memory>
#include <string>
#include <vector>
#include <grpcpp/grpcpp.h>
#include "inference.grpc.pb.h"

class InferenceServiceImpl final : public athena::inference::InferenceService::Service
{
public:
    InferenceServiceImpl() = default;

    grpc::Status LoadModel(grpc::ServerContext *context, const athena::inference::ModelRef *req,
                           athena::inference::LoadReply *reply) override;

    grpc::Status UnloadModel(grpc::ServerContext *context, const athena::inference::ModelRef *req,
                             athena::inference::LoadReply *reply) override;

    grpc::Status GetModelStatus(grpc::ServerContext *context, const athena::inference::ModelRef *req,
                                athena::inference::ModelStatusReply *reply) override;

    grpc::Status RunInference(grpc::ServerContext *context, const athena::inference::InferenceRequest *req,
                              athena::inference::InferenceReply *reply) override;
};

// helper to run server
void run_grpc_server(const std::string &listen_addr = "0.0.0.0:50051");
