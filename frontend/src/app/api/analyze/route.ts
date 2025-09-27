import { NextRequest, NextResponse } from 'next/server'
import { writeFile, mkdir, rm } from 'fs/promises'
import { existsSync } from 'fs'
import { join } from 'path'
import { spawn } from 'child_process'
import { VulnerabilityResult, VulnerabilityType } from '@/types/vulnerability'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const files = formData.getAll('files') as File[]
    const llmChoice = formData.get('llm_choice') as string || 'gpt'
    const specificFile = formData.get('specific_file') as string || ''
    const verbose = formData.get('verbose') === 'true'

    if (files.length === 0) {
      return NextResponse.json({ error: 'No files provided' }, { status: 400 })
    }

    // Create temporary directory for analysis
    const tempDir = join(process.cwd(), '..', 'temp', `analysis-${Date.now()}`)
    await mkdir(tempDir, { recursive: true })

    try {
      // Save uploaded files
      const savedFiles: string[] = []
      for (const file of files) {
        const bytes = await file.arrayBuffer()
        const buffer = Buffer.from(bytes)
        const filePath = join(tempDir, file.name)
        await writeFile(filePath, buffer)
        savedFiles.push(file.name)
      }

      // Run code_safe analysis
      const result = await runCodeSafeAnalysis(tempDir, llmChoice, specificFile, verbose)
      
      // Parse and format the results
      const formattedResult = await formatAnalysisResult(result, savedFiles, tempDir)

      return NextResponse.json(formattedResult)
    } finally {
      // Clean up temporary directory
      if (existsSync(tempDir)) {
        await rm(tempDir, { recursive: true, force: true })
      }
    }
  } catch (error) {
    console.error('Analysis error:', error)
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Analysis failed' },
      { status: 500 }
    )
  }
}

async function runCodeSafeAnalysis(
  projectPath: string,
  llmChoice: string,
  specificFile: string,
  verbose: boolean
): Promise<string> {
  return new Promise((resolve, reject) => {
    const args = ['-r', projectPath, '-l', llmChoice]
    
    if (specificFile) {
      args.push('-a', specificFile)
    }
    
    if (verbose) {
      args.push('-v')
    }

    // Set environment variables for API keys
    const env = {
      ...process.env,
      OPENAI_API_KEY: process.env.OPENAI_API_KEY,
      ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,
    }

    const codeSafe = spawn('code_safe', args, { 
      env,
      cwd: join(process.cwd(), '..')
    })

    let output = ''
    let errorOutput = ''

    codeSafe.stdout.on('data', (data) => {
      output += data.toString()
    })

    codeSafe.stderr.on('data', (data) => {
      errorOutput += data.toString()
    })

    codeSafe.on('close', (code) => {
      if (code === 0) {
        resolve(output)
      } else {
        reject(new Error(`Code Safe analysis failed: ${errorOutput || 'Unknown error'}`))
      }
    })

    codeSafe.on('error', (error) => {
      reject(new Error(`Failed to start Code Safe: ${error.message}`))
    })

    // Set timeout for long-running analyses
    setTimeout(() => {
      codeSafe.kill()
      reject(new Error('Analysis timed out after 5 minutes'))
    }, 300000) // 5 minutes
  })
}

async function formatAnalysisResult(
  rawOutput: string,
  analyzedFiles: string[],
  projectPath: string
): Promise<VulnerabilityResult> {
  // Parse the code_safe output
  const lines = rawOutput.split('\n')
  const fileAnalyses = []
  let currentFile = ''
  let currentAnalysis = ''
  let inAnalysis = false
  
  // Simple parser for code_safe output
  for (const line of lines) {
    if (line.startsWith('Analyzing ')) {
      if (currentFile && currentAnalysis) {
        fileAnalyses.push(parseFileAnalysis(currentFile, currentAnalysis))
      }
      currentFile = line.replace('Analyzing ', '').trim()
      currentAnalysis = ''
      inAnalysis = true
    } else if (inAnalysis && line.trim()) {
      currentAnalysis += line + '\n'
    }
  }
  
  // Add the last file analysis
  if (currentFile && currentAnalysis) {
    fileAnalyses.push(parseFileAnalysis(currentFile, currentAnalysis))
  }

  // Calculate summary statistics
  const totalVulnerabilities = fileAnalyses.reduce((sum, file) => sum + file.findings.length, 0)
  const highConfidenceVulns = fileAnalyses.reduce((sum, file) => 
    sum + file.findings.filter(f => f.confidence_score >= 8).length, 0
  )
  
  const allFindings = fileAnalyses.flatMap(f => f.findings)
  const averageConfidence = allFindings.length > 0 
    ? allFindings.reduce((sum, f) => sum + f.confidence_score, 0) / allFindings.length 
    : 0

  // Count vulnerability types
  const vulnerabilityCounts: Record<VulnerabilityType, number> = {
    LFI: 0, RCE: 0, SSRF: 0, AFO: 0, SQLI: 0, XSS: 0, IDOR: 0
  }
  
  allFindings.forEach(finding => {
    finding.vulnerability_types.forEach(type => {
      vulnerabilityCounts[type]++
    })
  })

  return {
    project_name: 'Uploaded Project',
    analysis_date: new Date().toISOString(),
    total_files_analyzed: analyzedFiles.length,
    total_vulnerabilities: totalVulnerabilities,
    high_confidence_vulnerabilities: highConfidenceVulns,
    file_analyses: fileAnalyses,
    summary: {
      vulnerability_counts: vulnerabilityCounts,
      average_confidence: averageConfidence,
      most_critical_file: fileAnalyses.length > 0 ? fileAnalyses[0].file_path : null
    }
  }
}

function parseFileAnalysis(filePath: string, analysisText: string) {
  // Parse the analysis output sections
  const sections = analysisText.split('----------------------------------------')
  const findings = []
  
  let scratchpad = ''
  let analysis = ''
  let poc = ''
  let confidenceScore = 0
  let vulnerabilityTypes: VulnerabilityType[] = []
  
  for (const section of sections) {
    const trimmed = section.trim()
    if (trimmed.startsWith('scratchpad:')) {
      scratchpad = trimmed.replace('scratchpad:', '').trim()
    } else if (trimmed.startsWith('analysis:')) {
      analysis = trimmed.replace('analysis:', '').trim()
    } else if (trimmed.startsWith('poc:')) {
      poc = trimmed.replace('poc:', '').trim()
    } else if (trimmed.startsWith('confidence_score:')) {
      const scoreMatch = trimmed.match(/confidence_score:\s*(\d+)/)
      if (scoreMatch) {
        confidenceScore = parseInt(scoreMatch[1])
      }
    } else if (trimmed.includes('vulnerability_types:')) {
      // Extract vulnerability types
      const vulnMatches = trimmed.match(/VulnType\.(\w+)/g) || trimmed.match(/- (\w+)/g)
      if (vulnMatches) {
        vulnerabilityTypes = vulnMatches.map(match => 
          match.replace('VulnType.', '').replace('- ', '') as VulnerabilityType
        )
      }
    }
  }
  
  if (analysis || poc || confidenceScore > 0) {
    findings.push({
      scratchpad,
      analysis,
      poc,
      confidence_score: confidenceScore,
      vulnerability_types: vulnerabilityTypes,
      context_code: []
    })
  }
  
  return {
    file_path: filePath,
    findings
  }
}
