# Bandwidth Coloring Problem (BCP) – SAT Encodings & Exact Baselines (BTL số 2)

Dự án Bài tập lớn số 2 môn **Các Vấn Đề Hiện Đại trong Khoa Học Máy Tính (HK I 2026–2027)** – **Đề tài số 4: Bandwidth Coloring Problem (BCP)** trên bộ dữ liệu chuẩn **33 instances GEOM**.

- **Tài liệu gốc (Paper)**: Daniel Faber, Adalat Jabrayilov, and Petra Mutzel, *"SAT Encoding of Partial Ordering Models for Graph Coloring Problems"*, SAT 2024 ([docs/1 - 4 - Graph Coloring Problems and Bandwidth Coloring Problem.pdf](docs/1%20-%204%20-%20Graph%20Coloring%20Problems%20and%20Bandwidth%20Coloring%20Problem.pdf)).
- **Kế hoạch & Phân công 3 thành viên**: [Ke_Hoach_Trien_Khai_BTL2_BCP_Nhom_3_Thanh_Vien.docx](Ke_Hoach_Trien_Khai_BTL2_BCP_Nhom_3_Thanh_Vien.docx).

## Cấu trúc thư mục

```text
BCP/
├── data/
│   └── GEOM/                        # Đầy đủ 33 file dữ liệu GEOM (GEOM20..GEOM120b)
├── docs/                            # Bài báo gốc SAT 2024
├── src/
│   ├── common/                      # [Dùng chung] Đọc dữ liệu, Greedy H(G), kiểm tra nghiệm, BaseSolver
│   ├── sat_pairwise/                # [Thành viên 1] ASS-S-B + AMO (Pairwise, SeqCounter, Binary, Commander, Product)
│   ├── sat_order/                   # [Thành viên 2] POP-S-B & POPH-S-B (Order Encoding)
│   └── exact_baselines/             # [Thành viên 3] ILP (Gurobi, CPLEX MIP) & CP (CPLEX CP, OR-Tools CP-SAT)
├── scripts/
│   ├── run_benchmark.py             # Script kiểm tra dataset và chạy thực nghiệm tự động
│   └── plot_cnsplots.py             # [Thành viên 3] Vẽ biểu đồ bằng thư viện cnsplots
├── results/
│   ├── raw_logs/                    # Kết quả CSV/JSON
│   ├── tables/                      # Bảng tổng hợp LaTeX (Table 3 & Table 5)
│   └── figures/                     # Biểu đồ xuất từ cnsplots
└── report/                          # Báo cáo khoa học LaTeX mẫu Elsevier (cas-sc.cls)
```

## Hướng dẫn chạy thử nhanh

1. **Kiểm tra toàn bộ 33 instances GEOM và cận trên Greedy $H(G)$**:
   ```bash
   python3 scripts/run_benchmark.py --check-dataset
   ```

2. **Chạy thử nghiệm SAT solver (cần môi trường có `python-sat`)**:
   ```bash
   # Chạy Order Encoding (POP-S-B) với Incremental SAT trên 5 instances đầu:
   /home/trandien/Documents/GitHub/SudokuSolver/.venv/bin/python scripts/run_benchmark.py --method POP-S-B --mode incremental --limit 5

   # Chạy Assignment Encoding (ASS-S-B) với Multi-shot SAT trên 5 instances đầu:
   /home/trandien/Documents/GitHub/SudokuSolver/.venv/bin/python scripts/run_benchmark.py --method ASS-S-B --mode multi-shot --amo seqcounter --limit 5
   ```
