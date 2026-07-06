# Hướng Dẫn Nộp Bài - Lab #28: Full Platform Integration Sprint

## Yêu Cầu Nộp Bài

**Full AI infrastructure platform demo** - từ data ingestion đến model serving với full observability.

## Các Artifacts Cần Nộp

### 1. Source Code
- Folder `lab28/` hoàn chỉnh với tất cả files
- Tất cả integration scripts hoạt động
- Prefect flows đã deploy và schedule

### 2. Screenshots Demo
Chụp màn hình các bước:
- Prefect UI: http://localhost:4200 (flow đang chạy)
- API Gateway call: `curl http://localhost:8000/health`
- Grafana dashboard: http://localhost:3000

### 3. Kết Quả Smoke Tests
Chạy và chụp màn hình kết quả:
```bash
cd lab28
pytest smoke-tests/ -v
```
Kỳ vọng: 5/5 tests passing

### 4. Production Readiness Score
```bash
python scripts/production_readiness_check.py
```
Kỳ vọng: Score >80%

### 5. Documentation
- `README.md` giải thích cách:
  - Start platform: `docker compose up -d`
  - Deploy Prefect flows
  - Run smoke tests
  - Access dashboards (Grafana:3000, Prometheus:9090, Prefect:4200)

## Định Dạng Nộp Bài

Tạo Repo GitHub chứa:
```
lab28_submission_[student_id]
├── lab28/                    # Source code hoàn chỉnh
│   ├── docker-compose.yml
│   ├── prefect/flows/
│   ├── scripts/
│   ├── api-gateway/
│   └── monitoring/
├── screenshots/              # Screenshots demo
│   ├── prefect_ui.png
│   ├── api_gateway.png
│   └── grafana_dashboard.png
├── smoke_tests_results.png   # Screenshot kết quả pytest
├── production_readiness.png  # Screenshot readiness score
└── README.md                # Hướng dẫn setup
```

## Địa Điểm Nộp
Nộp link repo GitHub qua LMS

## Tiêu Chí Chấm Điểm

| Tiêu Chí | Trọng Số | Mô Tả |
|----------|----------|-------|
| Integration Completeness | 40% | Tất cả 10 integration points hoạt động, data flow end-to-end |
| Observability | 25% | Logs, metrics, traces hiển thị; alerts configured |
| Performance | 20% | Latency trong SLO; load tested; không có memory leaks |
| Architecture Quality | 15% | Clean separation, GitOps config, documented decisions |

## Các Vấn Đề Cần Tránh

- Config drift giữa các environments
- Thiếu error handling tại integration points
- Monitoring coverage không hoàn chỉnh
- Không có rollback strategy
- Demo không test trước khi nộp

## 5 Câu Hỏi Cần Trả Lời Khi Nộp

1. **Phân tích các trade-offs trong thiết kế kiến trúc AI platform của bạn. Bạn đã cân bằng giữa performance, reliability, và maintainability như thế nào?**
   - **Performance vs Cost**: Chuyển phần Embedding và LLM inference lên Kaggle GPU giúp giải phóng tài nguyên local và tiết kiệm chi phí phần cứng (cost efficiency), đánh đổi lại là độ trễ truyền tải qua mạng (tunnel latency) tăng thêm khoảng 50-100ms.
   - **Reliability vs Complexity**: Sử dụng Kafka + Prefect giúp luồng xử lý dữ liệu cực kỳ bền bỉ (hỗ trợ backpressure, auto-retry, buffering), nhưng đánh đổi lại là độ phức tạp trong vận hành hạ tầng (phải quản lý Kafka, Zookeeper, Orion DB, Redis).
   - **Maintainability**: Tách biệt rõ ràng các lớp dữ liệu (Kafka, Delta Lake), lưu trữ đặc trưng (Feast Redis), vector DB (Qdrant) và phục vụ (API Gateway). Thiết kế đóng gói container hóa hoàn toàn qua Docker Compose giúp dễ dàng bảo trì và nâng cấp từng service độc lập mà không ảnh hưởng tới toàn hệ thống.

2. **Trong kiến trúc hybrid (Local + Kaggle), bạn xử lý ngắt kết nối giữa local và Kaggle như thế nào? Có cơ chế fallback không?**
   - **Đọc/ghi dữ liệu (Ingestion)**: Dữ liệu thô luôn được lưu trữ an toàn trong hàng đợi của Kafka topic `data.raw`. Nếu kết nối tới Kaggle (Embedding) bị đứt, Prefect flow tạm dừng hoặc retry. Khi kết nối phục hồi, consumer tiếp tục consume từ offset trước đó, đảm bảo không mất mát dữ liệu (zero data loss).
   - **Luồng Inference (API Gateway)**: API Gateway áp dụng timeout (30s) và bắt các ngoại lệ kết nối. Khi mất kết nối tới vLLM hoặc Embedding trên Kaggle, hệ thống sẽ thực hiện fallback bằng cách trả về câu trả lời mặc định, câu trả lời từ bộ nhớ đệm (cache) trong Redis, hoặc đưa ra thông điệp thân thiện thay vì làm sập toàn bộ gateway.

3. **Giải thích cách event-driven architecture với Kafka giúp decouple các components trong AI platform của bạn.**
   - **Decouple hoàn toàn Ingestion và Processing**: Bộ phận thu thập dữ liệu (Producer) chỉ việc đẩy dữ liệu vào topic `data.raw` và kết thúc nhiệm vụ. Nó không cần biết khi nào dữ liệu được nhúng (embed), lưu trữ vào Qdrant hay Delta Lake ra sao.
   - **Quản lý Backpressure**: Giúp điều hòa tốc độ giữa bên sản xuất dữ liệu (tốc độ cao) và bên xử lý dữ liệu (tốc độ giới hạn bởi GPU/CPU).
   - **Hỗ trợ Multi-consumer**: Cho phép nhiều ứng dụng hạ nguồn cùng đăng ký tiêu thụ một nguồn dữ liệu thô cho các tác vụ khác nhau (ví dụ: Prefect lưu Delta Lake, Elasticsearch index dữ liệu, Spark phân tích thống kê) mà không cần chỉnh sửa mã nguồn của Producer.

4. **Bạn đã implement observability như thế nào? Logs, metrics, và traces được thu thập và visualized ra sao?**
   - **Metrics**: API Gateway tích hợp `prometheus-fastapi-instrumentator` để tự động expose metrics tại endpoint `/metrics`. Prometheus server thực hiện scrape định kỳ mỗi 15s và Grafana hiển thị biểu đồ thời gian thực (request rate, p95 latency, error rate).
   - **Logs**: Sử dụng cơ chế stdout/stderr logging tiêu chuẩn của Docker. Toàn bộ logs từ các container được lưu trữ tập trung và có thể dễ dàng kiểm tra bằng lệnh `docker compose logs`.
   - **Traces & Experiment Tracking**:
     - Traces được cấu hình truyền về nền tảng LangSmith để trực quan hóa chi tiết từng bước LLM invocation, latency và tokens sử dụng.
     - Model metadata, hyperparameters và latency của serving layer được ghi nhận chi tiết thông qua MLflow Tracking (lưu tại `./mlruns` hoặc DagsHub) hỗ trợ theo dõi phiên bản model.

5. **Nếu một service trong stack (ví dụ: Qdrant hoặc Kafka) bị crash, hệ thống của bạn sẽ xử lý như thế nào? Có graceful degradation không?**
   - **Qdrant bị crash**: API Gateway không thực hiện được vector search. Hệ thống sẽ áp dụng cơ chế graceful degradation bằng cách bỏ qua context retrieval hoặc lấy tài liệu thay thế từ Feast (Redis online store) qua khóa tài liệu (document ID) để gửi trực tiếp tới LLM, giữ cho ứng dụng vẫn phản hồi câu trả lời thay vì báo lỗi 500 sập hệ thống.
   - **Kafka bị crash**: Các script đẩy logs mới sẽ tạm dừng hoặc buffering cục bộ. Tuy nhiên, luồng inference chính (API Gateway gọi Qdrant và vLLM) vẫn hoạt động hoàn toàn bình thường do hai luồng này được decoupled hoàn toàn thông qua kiến trúc hướng sự kiện.
   - **Redis (Feast) bị crash**: Hệ thống có cơ chế fallback tự động truy vấn trực tiếp dữ liệu lịch sử từ các tệp parquet trong Delta Lake thay vì Redis online store.


## Câu Hỏi Thêm?
Liên hệ giảng viên qua LMS hoặc office hours.
