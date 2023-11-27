# Advanced Prompt Engineering for Medical Code Extraction
Two-minute overview providing context, stating the problem the project is addressing, characterising the approach, and giving a brief account of how the problem was addressed.


## Preverity Background & Goals
Preverity is a medical malpractice risk analytics company. We have over 80 billion lines of medical billing transactions covering ~80% of US medical providers. Our goal is to accurately assess the risk or probability of an incoming malpractice claim for physicians. The company began by selling this information to malpractice insurance carriers so that they can more accurately price the insurance premiums for providers and health systems. However, going forward, we aim to move into the health system space as well.

Health systems currently attack malpractice claims retroactively. They wait for an event to occur, then they try to settle the claim with the least possible amount of damage. Because of this, many self-insured health systems set aside billions of dollars to protect against malpractice events. Preverity wants to provide health systems with a proactive approach to reduce risk by allowing for visibility into their physicians' behavior.

We are developing a solution for health systems that we call a Clinical Guidelines Engine (CGE). This is a conglomeration of many public rules that the describe the rates at which adverse events occurs per each physician. For example, a given doctor may be 20 times the national average for "Accidental puncturation or laceration during a procedure." Each rule or "measure" is defined by a set of medical billing codes (procedure, diagnosis, and drug codes). Our goal is to quickly assemble measures that track the practicing behavior of our customers' physicians so that the health systems can mitigate risk before malpractice events occur.

## Agency for Healthcare Research and Quality (AHRQ)
AHRQ is an organization whose goal it is to make healthcare safer, more affordable, more accessible, and more. One thing they do is release Patient Safety Indicator (PSI) PDFs that describe rules/measures and the list the necessary medical billing codes for the rule. See some examples at this webpage:
* https://qualityindicators.ahrq.gov/measures/PSI_TechSpec

## Problem
Our goal is to automate the extraction the medical codes from these PDFs such that it is easy to undestand the rule's definition. Doing so would save our company hundreds of hours of manual extraction. To do this, we must understand the numerator and denominator of the rate that is described in the PDF. The PDFs define each part of the fraction using group codes. For example, the numerator consists of group code A1, and the denominator consists of group codes A1 and A2, where A1 and A2 represent large collections of individual medical billing codes.

Because the codes are not separated by a common regular expression, we cannot use regex to extract the codes. Instead, we will use a language model (Claude in this case) to perform the extraction for us. However, even this method encounters challenges:
1. The text of the PDFs read in out of order. The group codes are read in after the individual medical codes. This makes it much harder for Claude to associate each individual code with the correct group code.

picture
  
2. The layout of some pages is misleading to Claude. For example, appendix pages do not conform to the most common page layout.
<p align="center">
  <img width="680" alt="Screenshot 2023-11-27 at 3 24 45 PM" src="https://github.com/michalekb11/claude-medical-code-extraction/assets/109704770/ead7c886-4937-4b91-b9ef-66f27ee71046">
</p>

## Current Approach
Due to these challenges, advanced prompt engineering is required to extract the codes into a structured format. 

**Current solution:** Two steps where claude iterates over previous output. First is find group cdoes, 2nd is extract codes. Each step uses the following prompt engineering paterns to effectively accomplish the subtasks:
* Persona pattern
* Few shot prompting (with example augmentation)
* Template pattern for output customization

This solution scores ___ on a manually created validation set (this is because it gets a whole page wrong).

## Code Demonstration
Jupyter notebook demonstration

## Live Demo
Streamlit

## Critical Analysis
Answer one or more of the following questions: What is the impact of this project? What does it reveal or suggest? What is the next step?

**Impact:** Will be able to generate measures much faster for CGE, allowing the company to expand more rapidly into the health system space.

**Persisting issues:** Does not work correctly on all pages. A human would have to review the output. If only text order problem was solved... we would be able to achieve a much higher accuracy...

**Next steps:** Can we fix issue of text order as it is read into python? Tried using Adobe tool that converts PDFs to text files, HTML, word documents, and more. This (for the most part) fixes the text order problem. Here are the potential solutions going forward:
* Now, we can modify our prompt to act on pages we know will have correct text order, and check accuracy.
* If the Adobe tool creates HTML files the same each time, there is a possibility to webscrape the codes instead of using Claude. This would save time (webscraping much faster than calling Claude), money (costs money to call Claude), and has the potential to be more accuract (no hallucinations in webscraping).

## Resources
Prepare links of where to go to get more information (other papers, models, blog posts (e.g. papers with code)). Use at least 5?

