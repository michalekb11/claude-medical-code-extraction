# Import necessary libraries
import os
from langchain.document_loaders import PyPDFLoader
from langchain.llms.bedrock import Bedrock
from utils import bedrock
import pandas as pd
import streamlit as st
import tempfile
from utils.functions import extract_group_codes, extract_indiv_codes, convert_codes_to_df

def main():
    # Set up dashboard
    st.title("AHRQ PDF Code Extraction")
    st.divider()

    ###############
    # Input processing
    ###############
    # PDF file, page that the codes start on, infer group code boolean, output filename
    uploaded_file = st.file_uploader(f"**Upload a PDF file**", type=["pdf"])
    start_page = st.number_input(label=f"**Starting page for codes**", min_value=1, step=1)
    ffill_group_codes = st.checkbox(label=f"**Infer missing group codes through forward fill**", value=False)
    
    output_filename = st.text_input(label=f"**Output filename**", placeholder="test.csv").strip()
    if not output_filename:
        output_filename = 'test.csv'
    elif output_filename[-4:] != '.csv':
        output_filename = output_filename + '.csv'

    if uploaded_file is not None:
        # Write the temporary binary file
        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
        with open(temp_path, "wb") as temp_file:
            temp_file.write(uploaded_file.getvalue())

        # Load the temp file using langchain PDF loader
        loader = PyPDFLoader(temp_path)
        documents = loader.load()
        os.remove(temp_path)

        # Check that PDF was loaded successfully and gather correct pages
        if len(documents) > 0:
            start_index = start_page - 1
            documents = documents[start_index:]
            st.success("Pages successfully extracted.")

        ###############
        # Preparation
        ###############
        # Read prompt templates
        step1_title = 'multistep_1_v1.2'
        path_to_step1 = f'./prompts/{step1_title}.txt'
        with open(path_to_step1) as f:
            step1_prompt = f.read()

        step2_title = 'multistep_2_v1.2'
        path_to_step2 = f'./prompts/{step2_title}.txt'
        with open(path_to_step2) as f:
            step2_prompt = f.read()

        ###############
        # Extract codes
        ###############
        # If the user clicks the execute button... extract the codes
        if st.button("Extract codes"):
            #=============================================================================
            # This is where you would set up a connection to AWS Bedrock using credentials
            #=============================================================================

                # Set LLM parameters
            llm = Bedrock(
                #model_id="anthropic.claude-instant-v1",
                model_id="anthropic.claude-v2",
                client=boto3_bedrock,
                model_kwargs={"temperature":0.0,
                            "top_k":50,
                            "max_tokens_to_sample": 1500},
            )

            st.divider()
            st.subheader("Searching for group codes...")

            # Run step 1 - Find group codes
            group_code_responses = extract_group_codes(documents, step1_prompt, llm)
            group_codes = [resp['text'].strip() for resp in group_code_responses]

            # Print step 1 results to UI
            st.write(f"**Group codes found by LLM:**")
            unique_gc = []
            for resp in group_codes:
                gc_list = resp.split('\n')
                unique_gc.extend([gc.strip() for gc in gc_list])
            unique_gc = set(unique_gc)

            for gc in unique_gc:
                st.markdown("- " + gc)
            st.divider()

            # Run step 2 - Extract codes into pipe-separated list
            st.subheader("Extracting codes for each page...")
            st.write("This may take a few minutes.")
            indiv_code_responses = extract_indiv_codes(documents, group_codes, step2_prompt, llm)
            indiv_codes = [resp['text'].strip() for resp in indiv_code_responses]

            # Convert the codes on each page to data frame and save rows that are unsuccessfully parsed
            parsing_results_list = [convert_codes_to_df(response=resp, page_num=ind + start_page) for ind, resp in enumerate(indiv_codes)]

            # Find the rows that were unseuccessfully parsed. Print them to the UI if applicable
            unsuccessful_rows_list =  []
            for result in parsing_results_list: unsuccessful_rows_list.extend(result['unsuccessful_lines'])
            if unsuccessful_rows_list:
                st.write(f"**The following lines of the LLM's output could not be parsed into the following 3 parts: [group code, code, code description]:**")
                for line in unsuccessful_rows_list:
                    st.markdown("- " + line)

            # Find the dataframes full of codes
            df_codes_list = [result['codes'] for result in parsing_results_list]

            # Concatenate the data frames
            df_codes = pd.concat(df_codes_list).reset_index(drop=True)

            # Forward fill group codes when group code is "NA". This assumes a particular order to the both the pages and the codes on each page.
            df_codes['code_group'].replace('NA', pd.NA, inplace=True)
            if ffill_group_codes:
                num_gc_missing = df_codes['code_group'].isna().sum()
                df_codes['code_group'].ffill(inplace=True)
                num_missing_remaining = df_codes['code_group'].isna().sum()
                st.write(f"Group code was inferred through forward fill for {num_gc_missing} rows.")
                st.write(f"There are {num_missing_remaining} remaining group codes that are missing.")

            # Display the dataframe to user
            st.write(f"**Sample of up to 100 extracted codes:**")
            if len(df_codes) <= 100:
                st.dataframe(data=df_codes, hide_index=True, use_container_width=True)
            else:
                st.dataframe(data=df_codes.sample(100, random_state=11), hide_index=True, use_container_width=True)

            # Save to CSV file
            csv = df_codes.to_csv(index=False)
            st.download_button(label="Download as CSV", data=csv, file_name=output_filename, mime="text/csv")
    return

if __name__ == "__main__":
    main()