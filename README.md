# Advanced Prompt Engineering for Medical Code Extraction

## Overview
Two-minute overview providing context, stating the problem the project is addressing, characterising the approach, and giving a brief account of how the problem was addressed.

**Preverity:** what is the company, what are we trying to do (CGE)

**AHRQ:** introduce the PDFs and what they contain (rates/measures)

**Problem:** Need a way to extract codes reliably and consistently to save coworkers hundreds of hours of manual extraction. The problem is that the page layouts are inconsistent, and the PDF text reads into python out of order.

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

