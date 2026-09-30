import pandas as pd
from preprocessing import preprocess_data
from rule_validator import validate_rules
from duplicate_detector import detect_duplicates
from llm_validator import MockLLMValidator
from classifier import final_classification

def run_evaluation():
    print("--- BẮT ĐẦU SMARTCLEAN AI EVALUATION ---")
    
    # 1. Đọc Ground Truth
    try:
        gt_df = pd.read_csv("ground_truth.csv")
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file ground_truth.csv")
        return

    # Lưu lại cột expected_status để đối chiếu, sau đó bỏ nó ra khỏi data đưa vào pipeline
    expected_statuses = gt_df['expected_status'].tolist()
    process_df = gt_df.drop(columns=['expected_status'])
    
    # Khởi tạo Mock LLM (hoặc Real LLM sau này)
    llm = MockLLMValidator()
    
    # 2. Chạy Pipeline (Pass 0 & 1)
    df_clean = preprocess_data(process_df)
    df_dup = detect_duplicates(df_clean)
    
    results = []
    correct_count = 0
    
    # 3. Chạy từng record (Pass 2, 3, 4)
    for index, row in df_dup.iterrows():
        record_dict = row.drop('is_duplicate').to_dict()
        is_dup = row['is_duplicate']
        expected = expected_statuses[index]
        
        # Rule Engine
        rule_flags = validate_rules(record_dict)
        
        # LLM Engine (chỉ gọi nếu có lỗi và không phải duplicate)
        llm_res = None
        if rule_flags and not is_dup:
            llm_res = llm.validate(record_dict, rule_flags)
            
        # Decision Classifier
        actual_status, actual_issues = final_classification(rule_flags, is_dup, llm_res)
        
        # Đối chiếu kết quả
        is_match = (actual_status == expected)
        if is_match:
            correct_count += 1
            
        results.append({
            "Test_ID": f"TC{index+1:02d}",
            "Customer": record_dict.get('full_name', 'N/A'),
            "Expected": expected,
            "Actual": actual_status,
            "Match": "✅ PASS" if is_match else "❌ FAIL",
            "Issues_Found": actual_issues
        })
        
    # 4. In Báo Cáo Kết Quả
    print("\n--- CHI TIẾT 10 TEST SCENARIOS ---")
    res_df = pd.DataFrame(results)
    # Căn lề in ra terminal cho đẹp
    print(res_df.to_string(index=False))
    
    print("\n--- TỔNG KẾT METRICS ---")
    accuracy = (correct_count / len(gt_df)) * 100
    print(f"Tổng số Test Cases: {len(gt_df)}")
    print(f"Số cases đúng: {correct_count}")
    print(f"Accuracy (Độ chính xác phân loại): {accuracy:.2f}%")
    
    print("\n[TO BE TESTED] - Hallucination Rate & Latency cần đo lường khi sử dụng Real LLM thay cho MockLLM.")

if __name__ == "__main__":
    run_evaluation()