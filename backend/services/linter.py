import re
import os
import json
import openai
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .rag_service import RAGService

# Goal: Create a more robust function to check for missing sections.
#
# Instructions:
# 1. Create a function `check_missing_sections(doc_sections: dict) -> list:`.
# 2. Inside, define the list of mandatory sections: ["Purpose", "Scope", "Responsibilities", "Revision History"].
# 3. Create a new list containing all the keys from the input `doc_sections` dictionary, ensuring each key is converted to lowercase and has leading/trailing whitespace stripped.
# 4. Loop through the `mandatory_sections` list.
# 5. For each required section, check if its lowercase version exists in the new list of lowercase document keys you created.
# 6. If a required section is not found, add a "Critical" finding to a findings list.
# 7. Return the final list of findings.

def check_missing_sections(doc_sections: dict) -> list:
    """Checks for missing mandatory sections using a case-insensitive search."""
    # Updated mandatory sections as per problem statement
    mandatory_sections = [
        "Title", "Purpose", "Scope", "Responsibilities", 
        "Definitions", "Procedure", "References", 
        "Revision History", "Approvals"
    ]
    findings = []

    # Create a list of the section titles from the document, converted to lowercase
    document_section_keys_lower = [key.lower().strip() for key in doc_sections.keys()]

    for required_section in mandatory_sections:
        # Check if the required section (in lowercase) is present
        if required_section.lower() not in document_section_keys_lower:
            findings.append({
                "description": f"Missing Mandatory Section: {required_section}",
                "severity": "Critical",
                "category": "Missing Sections"
            })
    return findings

def check_placeholders(full_text: str) -> list:
    """Check for prohibited placeholders and incomplete content."""
    placeholder_strings = ["TBD", "lorem ipsum", "to be decided", "TODO", "FIXME", "[INSERT", "XXX"]
    findings = []
    
    for placeholder in placeholder_strings:
        if re.search(placeholder, full_text, re.IGNORECASE):
            findings.append({
                "description": f"Prohibited Placeholder Found: '{placeholder}'",
                "severity": "Major",
                "category": "Content Quality"
            })
    return findings

def check_metadata_issues(metadata: dict) -> list:
    """Check for metadata issues as per problem statement."""
    findings = []
    
    # Check for Document ID (SOP-###)
    doc_id_found = False
    sop_pattern = r'SOP-\d+'
    
    for key, value in metadata.items():
        if isinstance(value, str):
            if re.search(sop_pattern, value, re.IGNORECASE):
                doc_id_found = True
                break
    
    if not doc_id_found:
        findings.append({
            "description": "Missing Document ID (expected format: SOP-###)",
            "severity": "Critical",
            "category": "Metadata Issues"
        })
    
    # Check for Version/Revision
    version_found = False
    version_keywords = ['version', 'revision', 'rev', 'v.']
    
    for key, value in metadata.items():
        if any(keyword in key.lower() for keyword in version_keywords):
            version_found = True
            break
    
    if not version_found:
        findings.append({
            "description": "Missing Version/Revision information",
            "severity": "Critical",
            "category": "Metadata Issues"
        })
    
    # Check for Effective Date (YYYY-MM-DD format)
    date_found = False
    date_pattern = r'\d{4}-\d{2}-\d{2}'
    
    for key, value in metadata.items():
        if isinstance(value, str):
            if re.search(date_pattern, value):
                date_found = True
                break
    
    if not date_found:
        findings.append({
            "description": "Missing Effective Date (expected format: YYYY-MM-DD)",
            "severity": "Major",
            "category": "Metadata Issues"
        })
    
    return findings

def check_revision_history(doc_sections: dict) -> list:
    """Check revision history completeness."""
    findings = []
    
    # Find revision history section
    revision_section = None
    for section_name, content in doc_sections.items():
        if 'revision' in section_name.lower() and 'history' in section_name.lower():
            revision_section = content
            break
    
    if not revision_section:
        findings.append({
            "description": "Revision History section not found",
            "severity": "Critical",
            "category": "Revision History"
        })
        return findings
    
    # Check if revision history has at least 1 entry
    # Look for table-like structure or at least version numbers
    version_patterns = [
        r'v\d+\.\d+',
        r'version\s+\d+',
        r'rev\s+\d+',
        r'\d+\.\d+',
        r'draft'
    ]
    
    entries_found = 0
    for pattern in version_patterns:
        matches = re.findall(pattern, revision_section, re.IGNORECASE)
        entries_found += len(matches)
    
    if entries_found == 0:
        findings.append({
            "description": "Revision History must have at least 1 entry",
            "severity": "Major",
            "category": "Revision History"
        })
    
    return findings

def check_procedure_clarity(doc_sections: dict) -> list:
    """Check procedure section for sufficient clarity (≥3 numbered steps)."""
    findings = []
    
    # Find procedure section
    procedure_section = None
    for section_name, content in doc_sections.items():
        if 'procedure' in section_name.lower():
            procedure_section = content
            break
    
    if not procedure_section:
        findings.append({
            "description": "Procedure section not found",
            "severity": "Critical",
            "category": "Content Quality"
        })
        return findings
    
    # Count numbered steps
    numbered_steps = re.findall(r'^\s*\d+\.', procedure_section, re.MULTILINE)
    
    if len(numbered_steps) < 3:
        findings.append({
            "description": f"Procedure section has insufficient clarity (found {len(numbered_steps)} numbered steps, minimum required: 3)",
            "severity": "Major",
            "category": "Content Quality"
        })
    
    return findings

def check_approval_signatures(full_text: str) -> list:
    """Check for required approval/signature lines."""
    findings = []
    
    required_approvals = ['Prepared by', 'Reviewed by', 'Approved by']
    missing_approvals = []
    
    for approval in required_approvals:
        if not re.search(approval, full_text, re.IGNORECASE):
            missing_approvals.append(approval)
    
    for missing in missing_approvals:
        findings.append({
            "description": f"Missing approval/signature line: {missing}",
            "severity": "Major",
            "category": "Approvals"
        })
    
    return findings


def check_reference_staleness(references_text: str, client: openai.AzureOpenAI, chat_deployment: str) -> list:
    findings = []
    
    print("\n--- DEBUG: Inside check_reference_staleness ---")
    print(f"--- Input being sent to AI: '{references_text}' ---")
    
    if not references_text.strip():
        print("--- DEBUG: No reference text provided, skipping AI call. ---")
        return findings

    try:
        # --- START: NEW BOOLEAN JSON PROMPT ---
        prompt = f"""
        You are an automated compliance checking API. You only respond in valid JSON.
        Analyze the following list of regulatory standards. For each standard, determine if it is outdated.

        Respond with a single JSON array of objects. Each object must have two keys:
        1. "reference": The original standard text.
        2. "is_outdated": A boolean value, `true` if the standard is outdated, `false` otherwise.
        
        Do not add any other text, notes, or explanations. Your entire response must be only the JSON array.

        Example response:
        [
            {{"reference": "ISO 9001:1994", "is_outdated": true}},
            {{"reference": "21 CFR Part 11", "is_outdated": false}}
        ]

        List of standards to analyze:
        {references_text}
        """
        # --- END: NEW BOOLEAN JSON PROMPT ---
        
        response = client.chat.completions.create(
            model=chat_deployment,
            messages=[{"role": "user", "content": prompt}],
            #max_completion_tokens=300 
        )
        
        ai_response = response.choices[0].message.content
        print(f"--- Raw AI Response received: '{ai_response}' ---")

        # --- START: NEW JSON PARSING LOGIC ---
        try:
            # The AI should return a valid JSON list
            parsed_json = json.loads(ai_response)
            
            for item in parsed_json:
                # Check if the item is a dictionary and has the required keys
                if isinstance(item, dict) and item.get('is_outdated') is True:
                    findings.append({
                        "description": f"Outdated Reference: {item.get('reference', 'Unknown')}",
                        "severity": "Major"
                        # The 'explanation' will be added later by the RAG service
                    })
        except (json.JSONDecodeError, TypeError):
            print(f"--- DEBUG: FAILED to parse AI response as JSON. Response was: {ai_response} ---")
            return [] # Return empty on parsing failure
        # --- END: NEW JSON PARSING LOGIC ---

        return findings

    except Exception as e:
        print(f"Error in reference staleness check: {e}")
        return []


def check_semantic_conformance(doc_sections: dict, client: openai.AzureOpenAI, embedding_deployment: str) -> list:
    findings = []
    try:
        golden_embeddings_path = 'ai_assets/golden_template_embeddings.json'
        if not os.path.exists(golden_embeddings_path):
            print("Golden template embeddings file not found.")
            return []
        with open(golden_embeddings_path, 'r') as f:
            golden_embeddings = json.load(f)

        for section_name, section_content in doc_sections.items():
            if not section_content.strip(): continue
            
            # Find corresponding golden section key (case-insensitive)
            golden_key = next((gk for gk in golden_embeddings if gk.lower() == section_name.lower()), None)

            if golden_key:
                response = client.embeddings.create(input=section_content, model=embedding_deployment)
                current_embedding = np.array(response.data[0].embedding).reshape(1, -1)
                golden_embedding = np.array(golden_embeddings[golden_key]).reshape(1, -1)
                
                similarity = cosine_similarity(current_embedding, golden_embedding)[0][0]
                
                if similarity < 0.9:
                    findings.append({
                        "description": f"Section '{section_name}' deviates from template (similarity: {similarity:.2f}).",
                        "severity": "Major"
                    })
    except Exception as e:
        print(f"Error in semantic conformance check: {e}")
    return findings


def run_all_checks(parsed_data: dict, client: openai.AzureOpenAI, chat_deployment: str, embedding_deployment: str) -> list:
    """Run comprehensive GxP compliance checks on the parsed document data."""
    all_findings = []
    
    # Extract data from parsed document
    metadata = parsed_data.get('metadata', {})
    doc_sections = parsed_data.get('sections', {})
    full_text = parsed_data.get('full_text', '')
    
    # Create an instance of the RAG service
    rag_service = RAGService()
    
    print("\n🔍 Running comprehensive GxP compliance checks...")
    
    # 1. Check for missing mandatory sections
    print("- Checking for missing mandatory sections...")
    all_findings.extend(check_missing_sections(doc_sections))
    
    # 2. Check metadata issues
    print("- Checking metadata requirements...")
    all_findings.extend(check_metadata_issues(metadata))
    
    # 3. Check revision history
    print("- Checking revision history completeness...")
    all_findings.extend(check_revision_history(doc_sections))
    
    # 4. Check for placeholder text and content quality
    print("- Checking for prohibited placeholders...")
    all_findings.extend(check_placeholders(full_text))
    
    # 5. Check procedure clarity
    print("- Checking procedure section clarity...")
    all_findings.extend(check_procedure_clarity(doc_sections))
    
    # 6. Check approval signatures
    print("- Checking approval/signature lines...")
    all_findings.extend(check_approval_signatures(full_text))
    
    # 7. Check for outdated references
    print("- Checking for outdated references...")
    # Find the 'References' section text specifically
    references_text = ""
    for key, value in doc_sections.items():
        if 'references' in key.lower():
            references_text = value
            break
    all_findings.extend(check_reference_staleness(references_text, client, chat_deployment))
    
    print("- Checking semantic conformance...")
    all_findings.extend(check_semantic_conformance(doc_sections, client, embedding_deployment))
    
    # Enrich findings with explanations from the RAG service
    print("- Enriching findings with knowledge base context...")
    for finding in all_findings:
        try:
            # Query the knowledge base using the finding's description
            relevant_chunks = rag_service.query(finding['description'], n_results=3)
            
            if relevant_chunks:
                # Join the text chunks together with a title
                explanation = "Relevant Context from Knowledge Base:\n\n"
                explanation += "\n\n".join(relevant_chunks)
                
                # Add the explanation to the finding
                finding['explanation'] = explanation
            else:
                finding['explanation'] = "No relevant context found in knowledge base."
                
        except Exception as e:
            print(f"Error enriching finding with RAG: {e}")
            finding['explanation'] = "Unable to retrieve context from knowledge base."
    
    print(f"Compliance checks completed. Found {len(all_findings)} total findings.")
    return all_findings