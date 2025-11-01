// core/src/grpc_server.cpp
#include "grpc_server.h"
#include "inference.pb.h"
#include "inference.grpc.pb.h"
#include <iostream>
#include <thread>
#include <chrono>

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;

Status InferenceServiceImpl::LoadModel(ServerContext *context, const athena::inference::ModelRef *req,
                                       athena::inference::LoadReply *reply)
{
    // TODO: integrate with core model manager / loader
    std::string msg = "stub: loaded " + req->model_name() + ":" + req->version();
    reply->set_ok(true);
    reply->set_message(msg);
    std::cout << "[gRPC] LoadModel: " << msg << std::endl;
    return Status::OK;
}

Status InferenceServiceImpl::UnloadModel(ServerContext *context, const athena::inference::ModelRef *req,
                                         athena::inference::LoadReply *reply)
{
    std::string msg = "stub: unloaded " + req->model_name() + ":" + req->version();
    reply->set_ok(true);
    reply->set_message(msg);
    std::cout << "[gRPC] UnloadModel: " << msg << std::endl;
    return Status::OK;
}

Status InferenceServiceImpl::GetModelStatus(ServerContext *context, const athena::inference::ModelRef *req,
                                            athena::inference::ModelStatusReply *reply)
{
    reply->set_model_name(req->model_name());
    reply->set_version(req->version());
    reply->set_status("not_loaded"); // stub
    return Status::OK;
}

Status InferenceServiceImpl::RunInference(ServerContext *context, const athena::inference::InferenceRequest *req,
                                          athena::inference::InferenceReply *reply)
{
    // Simple mock: copy inputs to outputs and sleep to simulate work
    for (int i = 0; i < req->inputs_size(); ++i)
    {
        reply->add_outputs(req->inputs(i));
    }
    reply->set_request_id(req->request_id());
    reply->set_latency_ms(1.0);
    reply->set_status("ok");
    std::cout << "[gRPC] RunInference for request: " << req->request_id() << " inputs=" << req->inputs_size() << "\n";
    return Status::OK;
}

void run_grpc_server(const std::string &listen_addr)
{
    InferenceServiceImpl service;
    ServerBuilder builder;
    builder.AddListeningPort(listen_addr, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);
    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "[gRPC] Server listening on " << listen_addr << std::endl;
    server->Wait();
}
