import streamlit as st
import pandas as pd
import json
from preprocessing import preprocess_data
from rule_validator import validate_rules
from duplicate_detector import detect_duplicates
from llm_validator import MockLLMValidator
from classifier import final_classification
from database import init_db, save_batch, load_records_by_status, update_record_decision

# Initialize System
init_db()
llm = MockLLMValidator()

st.set_page_config(page_title="SmartClean AI", layout="wide")
st.title("SmartClean AI - V1 Prototype")

# 1. FILE UPLOAD & PIPELINE EXECUTION
uploaded_file = st.file_uploader("Upload Customer Data (CSV/Excel)", type=['csv', 'xlsx'])

if uploaded_file and st.button("Run Data Pipeline"):
    with st.spinner("Processing data..."):
        # Load
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        # Pass 0: Preprocess
        df_clean = preprocess_data(df)
        
        # Pass 1: Duplicate Detection
        df_dup = detect_duplicates(df_clean)
        
        processed_records = []
        for _, row in df_dup.iterrows():
            record_dict = row.drop('is_duplicate').to_dict()
            is_dup = row['is_duplicate']
            
            # Pass 2: Rules
            rule_flags = validate_rules(record_dict)
            
            # Pass 3: AI Analysis (Only send problematic ones to save cost/time)
            llm_res = None
            if rule_flags and not is_dup:
                llm_res = llm.validate(record_dict, rule_flags)
            
            # Pass 4: Classification
            final_status, final_issues = final_classification(rule_flags, is_dup, llm_res)
            
            suggested = llm_res.suggested_corrections if llm_res else {}
            
            processed_records.append({
                "customer_id": record_dict["customer_id"],
                "original_data": record_dict,
                "status": final_status,
                "issues": final_issues,
                "suggested_corrections": suggested
            })
            
        # Save to SQLite state
        save_batch(pd.DataFrame(processed_records))
        st.success("Pipeline Execution Complete!")

# 2. DASHBOARD & HUMAN REVIEW INTERFACE
st.divider()
st.header("Human-in-the-loop (HITL) Review")

tabs = st.tabs(["NEEDS REVIEW", "DUPLICATE", "INVALID", "VALID", "EXPORT DB"])

with tabs[0]: # NEEDS REVIEW
    df_review = load_records_by_status("NEEDS_REVIEW")
    if not df_review.empty:
        st.write(f"Found {len(df_review)} records needing review.")
        for _, row in df_review.iterrows():
            orig_data = json.loads(row['original_data'])
            suggested = json.loads(row['suggested_corrections'])
            
            with st.expander(f"Review ID: {orig_data.get('customer_id')} - {orig_data.get('full_name')}"):
                st.warning(f"Issues: {json.loads(row['issues'])}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Original Data**")
                    st.json(orig_data)
                with col2:
                    st.write("**AI Suggestion**")
                    if suggested:
                        st.json(suggested)
                    else:
                        st.write("No AI suggestions available.")
                
                # HITL Actions
                action_col1, action_col2, action_col3, action_col4 = st.columns(4)
                if action_col1.button("Approve Suggestion", key=f"app_{row['id']}"):
                    merged = {**orig_data, **suggested}
                    update_record_decision(row['id'], merged, "APPROVED_AI_SUGGESTION", "VALID")
                    st.rerun()
                if action_col2.button("Keep Original", key=f"keep_{row['id']}"):
                    update_record_decision(row['id'], orig_data, "KEPT_ORIGINAL", "VALID")
                    st.rerun()
                if action_col3.button("Reject Data (Invalid)", key=f"rej_{row['id']}"):
                    update_record_decision(row['id'], orig_data, "REJECTED_BY_HUMAN", "INVALID")
                    st.rerun()
                # Edit flow can be expanded with text inputs
                
    else:
        st.success("No records need review.")

with tabs[1]: # DUPLICATE
    df_dup = load_records_by_status("DUPLICATE")
    st.dataframe(df_dup[['id', 'original_data', 'status']])

with tabs[2]: # INVALID
    df_inv = load_records_by_status("INVALID")
    st.dataframe(df_inv[['id', 'original_data', 'issues']])

with tabs[3]: # VALID
    df_val = load_records_by_status("VALID")
    st.dataframe(df_val[['id', 'final_data', 'action_taken']])

with tabs[4]: # EXPORT
    st.write("Export all VALID records ready for DB integration.")
    df_val = load_records_by_status("VALID")
    if not df_val.empty:
        # Flatten JSON for CSV export
        export_df = pd.json_normalize(df_val['final_data'].apply(json.loads))
        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Cleaned CSV", data=csv, file_name="cleaned_customers.csv", mime="text/csv")