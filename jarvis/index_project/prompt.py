from langchain.prompts import PromptTemplate
from langchain.prompts import PromptTemplate

# analyze_code_prompt = """Analyze the provided code and extract all interfaces and classes.
# Return a JSON object with their names, types, and descriptions.

# Expected format:
# {{
#     "components": [
#         {{
#             "name": "string",
#             "type": "string",
#             "description": "string"
#         }}
#     ]
# }}

# Code to analyze:
# {code}

# Return only valid JSON matching the schema above."""
analyze_code_prompt = """Analyze the provided code and extract all interfaces and classes.
Return a string with their names, types, and descriptions (Not as a json).

Expected format:
"
name: string,
type: enum | interface | class,
description: string,
"

Code to analyze:
{code}

Return only valid JSON matching the schema above."""
