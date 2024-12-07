import anthropic
from typing import Dict, Optional, List
from langchain_anthropic import ChatAnthropic  # Updated import
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json
import os

class SQLResponse(BaseModel):
    query: Optional[str] = Field(description="The generated SQL query")
    explanation: Optional[str] = Field(description="Explanation if query generation fails")

class SQLQueryGenerator:
    def __init__(self, api_key: str):
        self.llm = ChatAnthropic(
            model="claude-3-sonnet-20240229",
            anthropic_api_key=api_key,
            max_tokens=1024  # Added token limit
        )
        self.output_parser = PydanticOutputParser(pydantic_object=SQLResponse)
        
        # Define the system prompt template
        self.system_template = """You are a text to SQL query expert. Please help to generate a SQL query to answer the question. Your response should ONLY be based on the given context and follow the response guidelines and format instructions.

                                    Table Schema:
                                    {schema}

                                    Example Q&A Pairs:
                                    {examples}

                                    Foreign Key Information:
                                    {foreign_keys}
                                    
                                    DB Types Information:
                                    {types}

                                    Response Guidelines:
                                    1. If the provided context is sufficient, please generate a valid query without any explanations for the question.
                                    2. If the provided context is insufficient, please explain why it can't be generated.
                                    3. Please use the most relevant table(s).
                                    4. Please format the query before responding.

                                    The output should be a JSON object with the following format:
                                    {{
                                        "query": "A generated SQL query when context is sufficient.",
                                        "explanation": "An explanation of failing to generate the query."
                                    }}

                                    Question: {question}"""
                                    
        self.test_template =  """You are a text to SQL query expert. Please help to generate a SQL query to answer the question. Your response should ONLY be based on the given context and follow the response guidelines and format instructions.

                                    Table Schema:
                                    {schema}

                                    Example Q&A Pairs:
                                    {examples}

                                    Foreign Key Information:
                                    {foreign_keys}
                                    
                                    Response Guidelines:
                                    1. If the provided context is sufficient, please generate a valid query without any explanations for the question.
                                    2. If the provided context is insufficient, please explain why it can't be generated.
                                    3. Please use the most relevant table(s).
                                    4. Please format the query before responding.

                                    The output should be a JSON object with the following format:
                                    {{
                                        "query": "A generated SQL query when context is sufficient.",
                                        "explanation": "An explanation of failing to generate the query."
                                    }}

                                    Question: {question}"""                      

    def _format_examples(self, examples: List[Dict[str, str]]) -> str:
        """Format the example Q&A pairs."""
        examples_str = ""
        for example in examples:
            examples_str += f"### {example['question']}\n{example['query']}\n\n"
        return examples_str

    def generate_query(self, 
                      question: str, 
                      tables: str,
                      examples: List[Dict[str, str]], 
                      foreign_keys: str,
                      types: str
                      ) -> SQLResponse:
        """
        Generate a SQL query based on the natural language question.
        
        Args:
            question: The natural language question
            tables: Tables Information
            examples: List of example Q&A pairs
            foreign_keys: Foreign key relationships between tables
            types: User-defined types information
            
        Returns:
            SQLResponse object containing the generated query or explanation
        """
        
        # Format the prompt components
        examples_str = self._format_examples(examples)
        
        # Create the prompt
        prompt = ChatPromptTemplate.from_template(self.system_template)
        
        # Format the prompt with the given inputs
        formatted_prompt = prompt.format(
            schema=tables,
            examples=examples_str,
            foreign_keys=foreign_keys,
            types=types,
            question=question
        )
        
        # Generate response using Claude
        response = self.llm.invoke(formatted_prompt)
        
        # Parse the response
        try:
            # Extract JSON from the response
            json_str = response.content
            # Parse into SQLResponse object
            sql_response = self.output_parser.parse(json_str)
            return sql_response
        except Exception as e:
            return SQLResponse(
                query=None,
                explanation=f"Failed to parse response: {str(e)}"
            )
            
    def generate_test_query(self, 
                      question: str, 
                      tables: str,
                      examples: List[Dict[str, str]], 
                      foreign_keys: str,
                      ) -> SQLResponse:
        """
        Generate a SQL query based on the natural language question.
        
        Args:
            question: The natural language question
            tables: Tables Information
            examples: List of example Q&A pairs
            foreign_keys: Foreign key relationships between tables
            
        Returns:
            SQLResponse object containing the generated query or explanation
        """
        
        # Format the prompt components
        examples_str = self._format_examples(examples)
        
        # Create the prompt
        prompt = ChatPromptTemplate.from_template(self.test_template)
        
        # Format the prompt with the given inputs
        formatted_prompt = prompt.format(
            schema=tables,
            examples=examples_str,
            foreign_keys=foreign_keys,
            question=question
        )
        
        # Generate response using Claude
        response = self.llm.invoke(formatted_prompt)
        
        # Parse the response
        try:
            # Extract JSON from the response
            json_str = response.content
            # Parse into SQLResponse object
            sql_response = self.output_parser.parse(json_str)
            return sql_response
        except Exception as e:
            return SQLResponse(
                query=None,
                explanation=f"Failed to parse response: {str(e)}"
            )