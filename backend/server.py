"""
FastAPI backend server for Code Safe
Provides REST API for vulnerability analysis
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
import shutil
from pathlib import Path
import subprocess
import json
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Code Safe API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def parse_analysis_output(output: str) -> dict:
    """Parse the code_safe CLI output into structured JSON"""
    import re
    
    # Split by "Analyzing" to get individual file analyses
    # Use regex to handle cases where the file path might be split across lines
    parts = re.split(r'\n\s*Analyzing\s+', output)
    
    file_analyses = []
    
    for i, part in enumerate(parts):
        if i == 0:
            # First part might not start with "Analyzing", check if it contains analysis
            if 'scratchpad:' in part or 'analysis:' in part:
                # Extract filename from the beginning if present
                lines = part.split('\n')
                filename = 'unknown_file'
                analysis_text = part
                for line in lines[:5]:  # Check first few lines for filename
                    if line.strip() and not line.startswith('-') and '/' in line:
                        filename = line.strip()
                        # Remove the filename line from analysis text
                        analysis_text = '\n'.join(lines[lines.index(line)+1:])
                        break
                if analysis_text.strip():
                    file_analyses.append(parse_file_analysis(filename, analysis_text))
        else:
            # Extract filename and analysis from this part
            lines = part.split('\n')
            if lines:
                # First line(s) should contain the filename
                filename = lines[0].strip()
                # Handle case where filename might be split across multiple lines
                filename_lines = []
                analysis_start_idx = 0
                for j, line in enumerate(lines):
                    if line.strip().startswith('-') or 'scratchpad:' in line:
                        analysis_start_idx = j
                        break
                    if line.strip():
                        filename_lines.append(line.strip())
                
                if filename_lines:
                    filename = ''.join(filename_lines)
                    analysis_text = '\n'.join(lines[analysis_start_idx:])
                    if analysis_text.strip():
                        file_analyses.append(parse_file_analysis(filename, analysis_text))
    
    # Calculate summary
    total_vulnerabilities = sum(len(fa['findings']) for fa in file_analyses)
    all_findings = [f for fa in file_analyses for f in fa['findings']]
    high_confidence = sum(1 for f in all_findings if f.get('confidence_score', 0) >= 8)
    avg_confidence = sum(f.get('confidence_score', 0) for f in all_findings) / len(all_findings) if all_findings else 0
    
    vulnerability_counts = {
        'RCE': 0, 'SQLI': 0, 'XSS': 0, 'LFI': 0, 
        'SSRF': 0, 'AFO': 0, 'IDOR': 0
    }
    
    for finding in all_findings:
        for vuln_type in finding.get('vulnerability_types', []):
            if vuln_type in vulnerability_counts:
                vulnerability_counts[vuln_type] += 1
    
    return {
        'project_name': 'Uploaded Project',
        'analysis_date': None,
        'total_files_analyzed': len(file_analyses),
        'total_vulnerabilities': total_vulnerabilities,
        'high_confidence_vulnerabilities': high_confidence,
        'file_analyses': file_analyses,
        'summary': {
            'vulnerability_counts': vulnerability_counts,
            'average_confidence': round(avg_confidence, 2),
            'most_critical_file': file_analyses[0]['file_path'] if file_analyses else None
        }
    }

def parse_file_analysis(file_path: str, analysis_text: str) -> dict:
    """Parse analysis text - extract all vulnerability findings"""
    import re
    
    findings = []
    
    # Split the text into sections separated by "----------------------------------------"
    sections = re.split(r'-{40,}', analysis_text)
    
    current_finding = {}
    
    for section in sections:
        section = section.strip()
        if not section:
            continue
            
        # Check what type of section this is
        if section.startswith('scratchpad:'):
            # Start a new finding if we have a complete one
            if current_finding.get('confidence_score', 0) > 0 and current_finding.get('analysis'):
                findings.append(dict(current_finding))
                current_finding = {}
            
            current_finding['scratchpad'] = section.replace('scratchpad:', '').strip()
            
        elif section.startswith('analysis:'):
            current_finding['analysis'] = section.replace('analysis:', '').strip()
            
        elif section.startswith('poc:'):
            current_finding['poc'] = section.replace('poc:', '').strip()
            
        elif section.startswith('confidence_score:'):
            score_text = section.replace('confidence_score:', '').strip()
            try:
                current_finding['confidence_score'] = int(score_text)
            except ValueError:
                current_finding['confidence_score'] = 0
                
        elif section.startswith('vulnerability_types:'):
            # Extract vulnerability types from the section
            vuln_types = re.findall(r'VulnType\.(\w+)', section)
            if vuln_types:
                current_finding['vulnerability_types'] = vuln_types
            else:
                # Fallback: look for lines starting with "- VulnType."
                lines = section.split('\n')
                vuln_types = []
                for line in lines:
                    line = line.strip()
                    if line.startswith('- VulnType.'):
                        vuln_type = line.replace('- VulnType.', '').strip()
                        vuln_types.append(vuln_type)
                current_finding['vulnerability_types'] = vuln_types
            
            current_finding['context_code'] = []
            
            # This is typically the last section, so add the finding
            if current_finding.get('confidence_score', 0) > 0 and current_finding.get('analysis'):
                findings.append(dict(current_finding))
                current_finding = {}
    
    # Add the last finding if it exists
    if current_finding.get('confidence_score', 0) > 0 and current_finding.get('analysis'):
        findings.append(current_finding)
    
    return {
        'file_path': file_path,
        'findings': findings
    }

@app.get("/")
async def root():
    return {"message": "Code Safe API is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/analyze")
async def analyze(
    files: List[UploadFile] = File(...),
    llm_choice: str = Form("gpt"),
    specific_file: Optional[str] = Form(None),
    verbose: bool = Form(False)
):
    """Analyze uploaded files for security vulnerabilities"""
    
    if not files:
        return JSONResponse(
            status_code=400,
            content={"error": "No files provided"}
        )
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="code_safe_")
    logger.info(f"Created temp directory: {temp_dir}")
    
    try:
        # Save uploaded files
        saved_files = []
        for file in files:
            file_path = Path(temp_dir) / file.filename
            with open(file_path, 'wb') as f:
                content = await file.read()
                f.write(content)
            saved_files.append(file.filename)
            logger.info(f"Saved file: {file.filename}")
        
        # Build code_safe command - use venv's code_safe if available
        venv_code_safe = Path(__file__).parent.parent / '.venv' / 'bin' / 'code_safe'
        code_safe_cmd = str(venv_code_safe) if venv_code_safe.exists() else 'code_safe'
        
        # Always analyze the first uploaded file if specific_file is not provided
        file_to_analyze = specific_file if specific_file else saved_files[0]
        
        cmd = [code_safe_cmd, '-r', temp_dir, '-a', file_to_analyze, '-l', llm_choice]
        if verbose:
            cmd.append('-v')
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        # Get environment with API keys
        env = os.environ.copy()
        
        # Load .env file if it exists
        env_file = Path(__file__).parent.parent / '.env'
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env[key.strip()] = value.strip()
        
        logger.info(f"Environment has OPENAI_API_KEY: {'OPENAI_API_KEY' in env}")
        logger.info(f"Environment has ANTHROPIC_API_KEY: {'ANTHROPIC_API_KEY' in env}")
        logger.info(f"Temp directory contents: {os.listdir(temp_dir)}")
        
        # Run code_safe analysis
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            env=env
        )
        
        output = result.stdout
        stderr = result.stderr
        logger.info(f"Analysis output length: {len(output)} chars")
        logger.info(f"Exit code: {result.returncode}")
        if stderr:
            logger.error(f"stderr: {stderr}")
        if output:
            logger.info(f"stdout: {output}")
        else:
            logger.warning("No stdout output - CLI might not have found any files to analyze")
        
        # Parse output even if exit code is non-zero (CLI might crash after analysis)
        if output and ('Analyzing' in output and ('vulnerability_types:' in output or 'VulnType.' in output)):
            logger.info("Parsing analysis results...")
            parsed_result = parse_analysis_output(output)
            logger.info(f"Found {parsed_result['total_vulnerabilities']} vulnerabilities")
            return JSONResponse(content=parsed_result)
        elif result.returncode == 0:
            parsed_result = parse_analysis_output(output)
            return JSONResponse(content=parsed_result)
        else:
            error_msg = result.stderr or "Analysis failed with no output"
            logger.error(f"Analysis failed: {error_msg}")
            return JSONResponse(
                status_code=500,
                content={"error": error_msg}
            )
            
    except subprocess.TimeoutExpired:
        logger.error("Analysis timed out")
        return JSONResponse(
            status_code=500,
            content={"error": "Analysis timed out after 5 minutes"}
        )
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned up temp directory: {temp_dir}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

