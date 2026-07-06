import mlflow
import os

os.environ["MLFLOW_ALLOW_FILE_STORE"] = "true"
mlflow.set_tracking_uri("file:./mlruns")

mlflow.set_experiment("lab28-integration")

with mlflow.start_run(run_name="vllm-serving-v1"):
    mlflow.log_param("model", "Qwen/Qwen2.5-7B-Instruct-GPTQ-Int4")
    mlflow.log_param("max_model_len", 4096)
    mlflow.log_metric("gpu_memory_utilization", 0.85)
    mlflow.log_metric("avg_latency_ms", 450)
    mlflow.set_tag("serving_url", os.environ.get("VLLM_NGROK_URL", "http://localhost:8001"))
    mlflow.set_tag("status", "production")
    mlflow.set_tag("environment", "local-hybrid")

print("Integration 6+7 OK: MLflow local log completed")
