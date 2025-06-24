import streamlit as st
import requests
import pandas as pd
from streamlit_modal import Modal
from io import BytesIO

st.set_page_config(layout="wide", page_title="DataTool")

tab1, tab2 = st.tabs(["Jobs", "Config"])

with tab1:  
    # st.title("DataTool")
    if 'job_id' not in st.session_state:
        st.session_state.job_id = 0
    if 'job_counter' not in st.session_state:
        st.session_state.job_counter = 0
    if 'job_subcounter' not in st.session_state:
        st.session_state.job_subcounter = 0   
    if 'progress_line' not in st.session_state:
        st.session_state.progress_line = 0      
    if 'dfhead' not in st.session_state:
        st.session_state.dfhead = pd.DataFrame()
    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame()
    if 'uploader' not in st.session_state:
        st.session_state.uploader = pd.DataFrame()        
    if 'show_popup' not in st.session_state:
        st.session_state.show_popup = False
      

    with st.form("create_job_form"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            description = st.text_input("Description", placeholder="Description of the Job")
        with col2:
            object_id = st.text_input("Object ID", placeholder="Object ID")
        with col3:
            created_by = st.text_input("Created By", placeholder="Created By")

        
        with col4:
            st.write("")
            st.write("")
            if st.form_submit_button("Create Job"):
                # Validate all fields are filled
                if not all([description, object_id, created_by]):
                    st.error("Please fill in all fields")
                else:
                    # spinner while making the API call
                    with st.spinner("Creating Job..."):
                        try:
                            
                            payload = {
                                "description": description,
                                "object_id": object_id,
                                "created_by": created_by
                            }
                            
                            
                            api_url = "http://127.0.0.1:8000/jobs/"
                            
                            
                            response = requests.post(api_url, json=payload)
                            
                            
                            if response.status_code == 201:
                                st.toast("API call successful!", icon="✅")
                                # st.json(response.json())  # Display the response
                                st.session_state.job_id = response.json()["job_id"]
                            else:
                                st.error(f"API call failed with status code: {response.status_code}")
                                st.write(f"Response: {response.text}")
                        
                        except requests.exceptions.RequestException as e:
                            st.error(f"An error occurred: {str(e)}")

    # with st.form("job_form"):
    jcol1, jcol2 = st.columns([3,1])
    acol1, acol2, acol3, acol4, acol5, acol6, acol7 = st.columns([1,1,3,1,1,1,1])
    with acol1:
        job_id = st.number_input("Job ID", value=st.session_state.job_id)
    with acol2:
        if st.button("Get Job"):
        # job_id = 16
            # st.session_state.job_id = job_id
            job_data = requests.get("http://127.0.0.1:8000/jobs/readfull/{}".format(job_id))
            if job_data.status_code == 200:
                steps = job_data.json()
                steps1 = job_data.json()
                steps1.pop("steps")
                # print(steps1)
                st.session_state.dfhead = pd.DataFrame([steps1])
                # print(steps["steps"])
                df = pd.DataFrame(steps["steps"])
                # print('Length: ',len(df))
                count = (df['status'] == 'completed').sum()
                # print('Completed: ',count)
                st.session_state.progress_line = count / len(df)
                st.session_state.df = df
            else:
                st.session_state.dfhead = pd.DataFrame()
                st.session_state.df = pd.DataFrame()
                st.session_state.progress_line = 0
                st.toast("Failed to fetch data")
        # st.write("")
        # st.write("")
        if st.button("Activate"):
            job_data = requests.post("http://127.0.0.1:8000/jobs/{}/activate".format(job_id))
            if job_data.status_code >= 200 and job_data.status_code < 300:
                st.toast("Job Activated")
            else:
                st.error("Failed to fetch data")
    with acol3:
        if len(st.session_state.dfhead) > 0 \
                and st.session_state.dfhead.iloc[0]["status"] != "completed" \
                and st.session_state.dfhead.iloc[0]["status"] != "created":
                st.session_state.uploader = False
        else :
            st.session_state.uploader = True
        uploaded_file = st.file_uploader("Choose files for the Job", 
                                            disabled= st.session_state.uploader, type=None)

    with acol4:
        st.write("")
        st.write("")
        if st.button("Upload"):
            try:
                print(uploaded_file)
                print(st.session_state.job_id)
                print(job_id)
                if uploaded_file != None and ( st.session_state.job_id > 0 or job_id > 0): #st.form_submit_button("Upload"):
                    print("aaaaaa")
                    job_id_folder = st.session_state.job_id if st.session_state.job_id > 0 else job_id
                    payload =   {
                                    "folder": f'Job-{job_id_folder}',
                                    "file": uploaded_file.name
                                }
                    presigned_url = requests.post('http://127.0.0.1:8000/uploadurl', json=payload)
                    print(presigned_url.json())
                    response = requests.put(
                        presigned_url.json(),
                        data=uploaded_file.getvalue(),
                        headers={
                            "x-ms-blob-type": "BlockBlob",
                            "Content-Type": uploaded_file.type
                        }
                    )
                    if response.status_code == 201:
                        st.toast("Upload successful!", icon="✅")
                    else:
                        print(response.text)
                        st.toast(f"Upload failed: {response.text}", icon="❌")  
            except Exception as e:
                st.error(f"Error: {str(e)}")                    
    with acol5:
        job_counter = st.number_input("Job Counter", value=st.session_state.job_counter, key="job_counter")
    with acol6:
        job_subcounter = st.number_input("Job Subcounter", value=st.session_state.job_subcounter, key="job_subcounter")
    with acol7:
        modal = Modal(
                "Demo Modal", 
                key="demo-modal1",
                
                # Optional
                padding=20,    # default value
                max_width=744  # default value
            )
        # st.write("")
        # st.write("")
        if st.button("Complete"):
            # print(job_id, job_counter, job_subcounter)
            if (job_id > 0) and (job_counter > 0) and (job_subcounter > 0):
                job_data = requests.post("http://127.0.0.1:8000/jobs/{}/counter/{}/subcounter/{}/complete".format(job_id, job_counter, job_subcounter))
                if job_data.status_code >= 200 and job_data.status_code < 300:
                    st.toast("Job Marked Complete", icon="✅")  
                else:
                    st.toast("Failed to fetch data", icon="❌") 
            else:
                st.toast("Please enter valid Job, JobCounter, JobSubCounter")
        open_modal = st.button("Download")
        if open_modal:
            modal.open()

        if modal.is_open():
            with modal.container():
                print(job_id, job_counter, job_subcounter, st.session_state.job_counter)
                result = st.session_state.df.loc[
                    (st.session_state.df["job_id"] == job_id) & 
                    (st.session_state.df["job_counter"] == job_counter) & 
                    (st.session_state.df["job_subcounter"] == job_subcounter), 
                    "step_id"
                ]
                if result.values.size > 0:
                    print(result.values[0])
                    items = [{"file":"Apple", "url":"apple.com"}, {"file": "Banana", "url":"banana.com"},{"file": "Cherry", "url":"cherry.com"},{"file": "Date", "url":"date.com"},{"file": "Elderberry", "url":"Elderberry.com"}]

                    payload =   {
                                "folder": f"Job-{job_id}/Step-{job_counter}-{job_subcounter}-{result.values[0]}", 
                                "file": "dummy"
                                }
                    # f'Job-{st.session_state.job_id}',
                    presigned_url = requests.post('http://127.0.0.1:8000/downloadurl', json=payload)
                    print(presigned_url.json())

                    items_url = presigned_url.json()
                    for item in items_url:
                        st.markdown("[" + item["file"] + "](" + item["url"] + ")")
        

    st.dataframe(st.session_state.dfhead)
    progress_bar = st.progress(st.session_state.progress_line)
    st.dataframe(st.session_state.df)
    
with tab2:
    st.title("Config")  
    col1, col2 = st.columns(2)
    with col1:
        object_id = st.text_input("Object ID", placeholder="Object ID")
    with col2:
        st.write("")
        st.write("")
        if st.button("Get Object"):
            object_data = requests.get("http://127.0.0.1:8000/links/object/{}".format(object_id))
            st.session_state.df_object = pd.DataFrame(object_data.json())

    if 'df_object' not in st.session_state:
        st.session_state.df_object = pd.DataFrame()
            

    st.dataframe(st.session_state.df_object)
