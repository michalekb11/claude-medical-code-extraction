# Advanced Prompt Engineering for Medical Code Extraction
## Preverity Background & Goals
Preverity is a medical malpractice risk analytics company. We have over 80 billion lines of medical billing transactions covering ~80% of US medical providers. Our goal is to accurately assess the risk or probability of an incoming malpractice claim for physicians. The company began by selling this information to malpractice insurance carriers so that they can more accurately price the insurance premiums for providers and health systems. However, going forward, we aim to move into the health system space as well.

<p align="center">
  <img width="848" alt="image" src="https://github.com/michalekb11/claude-medical-code-extraction/assets/109704770/310817bf-c2ae-4712-a94f-6bc1d98d736b">
</p>

Health systems currently approach malpractice claims retroactively. They wait for an event to occur, then they try to settle the claim with the least possible amount of damage. Because of this, many self-insured health systems set aside billions of dollars to protect against malpractice events. Preverity wants to provide health systems with a proactive approach to reduce risk by allowing for visibility into their physicians' practicing behavior.

We are developing a solution for health systems that we call a Clinical Guidelines Engine (CGE). This is a conglomeration of many public rules that each define an adverse event that could happen in a medical setting. We can calculate the rate at which these events happen for each physician and compare them against the national benchmark. For example, a doctor may be 20 times the national average for "Accidental puncturation or laceration during a procedure." Each rule or "measure" is defined by a set of medical billing codes (procedure, diagnosis, and drug codes). Our goal is to quickly assemble measures that track the practicing behavior of our customers' physicians so that the health systems can mitigate risk before malpractice events occur.

## Agency for Healthcare Research and Quality (AHRQ)
AHRQ is an organization whose goal it is to make healthcare safer, more affordable, more accessible, and more. One thing they do is release Patient Safety Indicator (PSI) PDFs that describe rules/measures and the list the necessary medical billing codes for the rule. See some examples at this webpage: https://qualityindicators.ahrq.gov/measures/PSI_TechSpec

## Problem
Our goal is to automate the extraction the medical codes from these PDFs such that it is easy to undestand the rule's definition. Doing so would save our company hundreds of hours of manual extraction. To do this, we must understand the numerator and denominator of the rate that is described in the PDF. The PDFs define each part of the fraction using group codes. For example, the numerator consists of group code A1, and the denominator consists of group codes A1 and A2, where A1 and A2 represent large collections of individual medical billing codes.

Because the codes are not separated by a common regular expression, we cannot use regex to extract the codes. Instead, we will use a language model (here, it is Claude) to perform the extraction for us. However, even this method encounters challenges:
1. The text of the PDFs read in out of order. The group codes are read in after the individual medical codes. This makes it much harder for Claude to associate each individual code with the correct group code.

<p align="center">
  <img width="900" alt="image" src="https://github.com/michalekb11/claude-medical-code-extraction/assets/109704770/3a9f878f-f568-4ddd-a912-993feabe2eb8">
</p>
  
2. The layout of some pages is misleading to Claude. For example, appendix pages do not conform to the most common page layout.
<p align="center">
  <img width="929" alt="Screenshot 2023-11-27 at 3 48 36 PM" src="https://github.com/michalekb11/claude-medical-code-extraction/assets/109704770/997754f7-9b7d-4846-8b5b-7175e6547603">
</p>


## Current Approach
Due to these challenges, advanced prompt engineering is required to extract the codes into a structured format. 

The current solution is to ask Claude to iterate over each page multiple times. This has resulted in better performance than asking Claude to accomplih the task in just one prompt.
1. The first iteration asks Claude to identify the group codes on the page.
2. The second iteration asks Claude to use the group codes it found to extract each individual medical code and assign them to the correct group code.

Each of these prompts requires advanced prompt engineering to be effective. This is due to the pages being messy, complex, and inconsistent in format/appearance. The following prompt engineering patterns were used in both steps:
* **Persona pattern -** Ask the LLM to assume a particular role that would be beneficial for accomplishing the task. Think about who you would go to in the real world if you wanted advice on how to solve this problem.

> "Human: You are an expert medical coder with knowledge of procedure (ICD-10-PCS, CPT, HCPCS), diagnosis (ICD-10-CM, ICD-11), drug (NDC), revenue codes, and more. More importantly, you are familiar with public PDFs from the Agency for Healthcare Research and Quality (AHRQ) that define Public Safety Indicators (PSI). Below, you will find examples of full pages from these PDF documents. These pages list medical codes which are typically represented by alphanumeric strings..."

* **Template pattern (output customization) -** Provide a specified output format that the LLM should adhere to. This allows the output to be parsed easier (and in this case, converted to a CSV).

> "Your final answer should follow the output format below:  
[group code]|[code1]|[code1 description]  
[group code]|[code2]|[code2 description]  
etc..."

* **Few-shot prompting (with example augmentation) -** Show the LLM multiple examples of the input you will provide as well as the correct answer that should be returned. Here, the prompt includes 8-10 diverse examples of full pages from AHRQ PDFs as well as the correct output to assist in Claude's in-context learning. Additionally, some of the examples are the raw text, and some examples are cleaned text to help Claude learn what the important information is in each example.

> "Example page: AHRQ QI ICD-10-CM/PCS Specification v2023  
PSI 08 In-Hospital Fall-Associated Fracture Rate  
qualityindicators.ahrq.gov  
Joint prosthesis associated fracture diagnosis codes: (PROSFXID)  
M96661 Fracture of femur following insertion of orthopedic implant, joint prosthesis, or bone plate, right leg  
M9701XA Periprosthetic fracture around internal prosthetic right hip joint, initial encounter  
M96662 Fracture of femur following insertion of orthopedic implant, joint prosthesis, or bone plate, left leg  
M9702XA Periprosthetic fracture around internal prosthetic left hip joint, initial encounter  
M96669 Fracture of femur following insertion of orthopedic implant, joint prosthesis, or bone plate, unspecified leg  
August 2023 3 of 109  
> Example group codes: PROSFXID - Joint prosthesis associated fracture diagnosis codes  

> Assistant: PROSFXID|M96661|Fracture of femur following insertion of orthopedic implant, joint prosthesis, or bone plate, right leg  
PROSFXID|M9701XA|Periprosthetic fracture around internal prosthetic right hip joint, initial encounter  
PROSFXID|M96662|Fracture of femur following insertion of orthopedic implant, joint prosthesis, or bone plate, left leg  
PROSFXID|M9702XA|Periprosthetic fracture around internal prosthetic left hip joint, initial encounter  
PROSFXID|M96669|Fracture of femur following insertion of orthopedic implant, joint prosthesis, or bone plate, unspecified leg"

## Effectiveness
This solution has an accuracy of 73.2% on a manually created validation set. However, note that the model will get large chunks of codes wrong at a time. For example, if Claude gets 1 code incorrect on a page, it often gets all of them wrong on the page. 

Claude seems to be fairly reliable when it comes to rewriting the text exactly as it appears on the original page. The aspect of the extraction that the model struggles most with is the assignment of each individual code to the correct group code, likely because of the text ordering issues when the PDF is read in.

## Critical Analysis
Answer one or more of the following questions: What is the impact of this project? What does it reveal or suggest? What is the next step?

**Impact:** The current solution is not perfect, but it performs well enough to be able to save the company many hours of manual code extraction. This will assist in generating measures for CGE much faster, allowing Preverity to expand more rapidly into the health system space.

**Persisting issues:** The model still makes mistakes on some pages. Most often, this is due to text being read in out of order. If we were able to solve this issue, we would be able to achieve a much higher accuracy and consistency.

**Next steps:**
* Investigate whether we can fix the text order issue using the Adobe tool that converts PDFs to other file formats such as text files.
* If converting to a text file appears promising, adjust the prompts slightly to accomodate inputs that look slightly different. Then, reevaluate the results.
* If Adobe can convert PDFs to HTML files in a consistent manner across PDFs, try webscraping the codes using the HTML. This would eliminate the need for a LLM (reducing costs, saving time, and potentially providing more reliable results).

## Resources
Preverity website
* https://preverity.com/

AHRQ Patient Safety Indicators
* https://qualityindicators.ahrq.gov/measures/PSI_TechSpec


