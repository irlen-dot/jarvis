from typing import Dict, Any, Optional, Union
import json
import re

class AgentOutputParser:
    """Parser for handling and normalizing React agent outputs."""
    
    @staticmethod
    def extract_code_block(text: str) -> Optional[str]:
        """
        Extract content from markdown code blocks.
        
        Args:
            text: Text containing possible code blocks
        Returns:
            Optional[str]: Content of the code block if found
        """
        # Match both ``` and ```json style code blocks
        code_block_pattern = r"```(?:json)?\n(.*?)\n```"
        match = re.search(code_block_pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    @staticmethod
    def parse_output(output: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse agent output, handling various formats including code blocks.
        
        Args:
            output: Raw output from agent
        Returns:
            Dict[str, Any]: Parsed and normalized output
        """
        try:
            # If already a dict, return it
            if isinstance(output, dict):
                return output

            if not isinstance(output, str):
                return {
                    "success": False,
                    "message": f"Unexpected output type: {type(output)}"
                }

            # Check for code blocks
            code_content = AgentOutputParser.extract_code_block(output)
            if code_content:
                try:
                    return json.loads(code_content)
                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "message": f"Error parsing JSON from code block: {str(e)}",
                        "raw_content": code_content
                    }

            # Try parsing as direct JSON
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                # If not JSON, return as plain content
                return {
                    "success": True,
                    "content": output,
                    "type": "text"
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error parsing output: {str(e)}",
                "raw_output": output
            }

def process_agent_output(result: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Process agent output with improved handling of various input types.
    
    Args:
        result: Raw result from agent - can be string or dictionary
    Returns:
        Dict[str, Any]: Processed and normalized output
    """
    try:
        # Handle string input
        if isinstance(result, str):
            output = result
            original_input = None
        # Handle dictionary input
        elif isinstance(result, dict):
            output = result.get("output", "")
            original_input = result.get("input")
        else:
            return {
                "success": False,
                "message": f"Unexpected result type: {type(result)}",
                "raw_output": str(result)
            }

        parser = AgentOutputParser()
        parsed_result = parser.parse_output(output)
        
        # Add original input if available
        if original_input is not None:
            parsed_result["original_input"] = original_input
            
        return parsed_result

    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing output: {str(e)}",
            "raw_output": str(result)
        }