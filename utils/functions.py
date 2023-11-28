from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import pandas as pd

def extract_group_codes(pages, prompt, llm):
    """Extract group codes from an AHRQ PSI PDF"""
    # Set up input list
    input_list = [{'document':page.page_content} for page in pages]
    # Set up prompt template
    prompt_template = PromptTemplate.from_template(prompt)
    # Create chain
    llm_chain= LLMChain(
        llm=llm,
        prompt=prompt_template
    )
    # Gather group code responses from llm
    responses = llm_chain.apply(input_list)
    return responses

def extract_indiv_codes(pages, group_codes, prompt, llm):
    """Extract individual codes from AHRQ PSI PDF"""
    # Set up input list
    input_list = [{'document':page.page_content, 'group_codes':group_codes[i]} for i, page in enumerate(pages)]
    # Set up prompt template
    prompt_template = PromptTemplate.from_template(prompt)
    # Create chain
    llm_chain= LLMChain(
        llm=llm,
        prompt=prompt_template
    )
    # Gather code pipe-separated list responses from llm
    responses = llm_chain.apply(input_list)
    return responses

def convert_codes_to_df(response, page_num=None):
    """Create a pandas dataframe using the LLM-extracted codes in pipe separated list. Save any rows that are not parsed correctly."""
    # Empty lists to store the results of trying to parse each line
    unsuccessful_rows = []
    successful_rows = []
    # Parse each line in LLM output 
    lines = response.split('\n')
    for line in lines:
        # There should be 3 parts (group code, code, and the code's description)
        parts = line.strip().split('|')
        if len(parts) != 3:
            unsuccessful_rows.append(line)
            continue
        if page_num:
            successful_rows.append({'page_num': page_num, 'code_group': parts[0], 'code': parts[1], 'description': parts[2]})
        else:
            successful_rows.append({'code_group': parts[0], 'code': parts[1], 'description': parts[2]})

    # Create a pandas DataFrame
    df = pd.DataFrame(successful_rows)
    # Create dictionary to return
    parsing_results = {
        'codes':df,
        'unsuccessful_lines':unsuccessful_rows
    }
    return parsing_results