from pathlib import Path
from typing import Union, Optional
from langchain.tools import tool

@tool
def write_file(content: str, file_path: Union[str, Path], create_dirs: Optional[bool] = True) -> bool:
   """
   Write content to a file at the specified path.
   
   Args:
       content: Content to write to the file
       file_path: Path where the file should be created
       create_dirs: If True, create parent directories if they don't exist
       
   Returns:
       bool: True if write was successful, False otherwise
   """
   try:
       # Convert string path to Path object
       path = Path(file_path)
       
       # Create parent directories if needed
       if create_dirs:
           path.parent.mkdir(parents=True, exist_ok=True)
           
       # Write the content
       path.write_text(content, encoding='utf-8')
       
       return True
       
   except Exception as e:
       print(f"Error writing file: {str(e)}")
       return False