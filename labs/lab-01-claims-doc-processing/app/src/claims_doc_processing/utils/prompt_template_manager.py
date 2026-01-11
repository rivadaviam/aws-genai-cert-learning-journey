"""Prompt template manager for document processing."""

class PromptTemplateManager:
    """
    Manages reusable prompt templates for document processing.
    
    This class centralizes all prompt templates used in the Lambda function,
    making it easier to maintain and customize prompts without modifying
    the main processing logic.
    """
    
    def __init__(self):
        self.templates = {
            "document_understanding": """
Analyze this insurance claim document and provide a comprehensive understanding of:
1. Document type and structure
2. Key sections identified
3. Overall document quality and completeness
4. Any notable patterns or anomalies

Document:
{document_text}

Provide your analysis in JSON format with clear structure.""",
            
            "extract_info": """
Extract the following information from this insurance claim document and return it as valid JSON:
- Claimant Name
- Policy Number
- Incident Date
- Claim Amount
- Incident Description
- Claim Type
- Any additional relevant information

Document:
{document_text}

Return ONLY valid JSON, no additional text or explanation.""",
            
            "generate_summary": """
Based on this extracted claim information:
{extracted_info}

Generate a concise, professional summary of the insurance claim that includes:
1. Key claim details
2. Claimant information
3. Incident overview
4. Claim amount

Keep the summary clear and under 200 words."""
        }
    
    def get_prompt(self, template_name, **kwargs):
        """
        Get a formatted prompt from a template.
        
        Args:
            template_name: Name of the template to use
            **kwargs: Variables to format into the template
        
        Returns:
            Formatted prompt string
        
        Raises:
            ValueError: If template_name is not found
        """
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found. Available templates: {list(self.templates.keys())}")
        
        return template.format(**kwargs)
    
    def list_templates(self):
        """
        List all available template names.
        
        Returns:
            List of template names
        """
        return list(self.templates.keys())

