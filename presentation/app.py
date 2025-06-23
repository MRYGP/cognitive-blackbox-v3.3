# cognitive-blackbox/presentation/app.py
# (The only change is in the main() function)
# ... (all other functions like load_and_parse_case, initialize_state, render_... remain the same as the last working version)

# ... [KEEP ALL THE CODE FROM THE PREVIOUS WORKING VERSION OF APP.PY, FROM LINE 1 TO THE START OF main()] ...

def main():
    """Main function to run the application."""
    st.set_page_config(page_title=AppConfig.PAGE_TITLE, page_icon=AppConfig.PAGE_ICON, layout="wide")
    
    initialize_state()

    # --- THE FINAL FIX IS HERE: Explicit AI Engine Initialization ---
    # We explicitly call the initialize method here, in the main app flow,
    # ensuring st.secrets is ready.
    if st.session_state.engine.initialize():
        # Only proceed if the AI engine is successfully initialized
        if st.session_state.view == "act" and st.session_state.case_id:
            if st.session_state.case_obj is None or st.session_state.case_obj.id != st.session_state.case_id:
                st.session_state.case_obj = load_and_parse_case(st.session_state.case_id)
        
        if st.session_state.view == "selection":
            render_case_selection()
        elif st.session_state.view == "act":
            render_act_view()
    else:
        # If AI engine fails to initialize, show a clear error message.
        st.error("AI引擎初始化失败。请检查您的Streamlit Secrets中是否正确配置了GEMINI_API_KEY。")
        st.info(f"错误详情: {st.session_state.engine.error_message}")


if __name__ == "__main__":
    main()

# (You need to include the full content of render_case_selection and render_act_view and other functions from the last version)
