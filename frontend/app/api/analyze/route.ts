import { NextRequest, NextResponse } from 'next/server'
import { writeFile, mkdir, rm } from 'fs/promises'
import { existsSync } from 'fs'
import { join } from 'path'
import { spawn } from 'child_process'
import type { VulnerabilityResult, VulnerabilityType } from '@/types/vulnerability'

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const files = formData.getAll('files') as File[]
    const llmChoice = (formData.get('llm_choice') as string) || 'gpt'
    const specificFile = (formData.get('specific_file') as string) || ''
    const verbose = formData.get('verbose') === 'true'

    if (files.length === 0) {
      return NextResponse.json({ error: 'No files provided' }, { status: 400 })
    }

    const tempDir = join(process.cwd(), '..', 'temp', `analysis-${Date.now()}`)
    await mkdir(tempDir, { recursive: true })

    try {
      const savedFiles: string[] = []
      for (const file of files) {
        const bytes = await file.arrayBuffer()
        const buffer = Buffer.from(bytes)
        const filePath = join(tempDir, file.name)
        await writeFile(filePath, buffer)
        savedFiles.push(file.name)
      }

      const result = await runCodeSafeAnalysis(tempDir, llmChoice, specificFile, verbose)
      const formattedResult = await formatAnalysisResult(result, savedFiles)
      return NextResponse.json(formattedResult)
    } finally {
      if (existsSync(tempDir)) await rm(tempDir, { recursive: true, force: true })
    }
  } catch (error) {
    console.error('Analysis error:', error)
    return NextResponse.json({ error: error instanceof Error ? error.message : 'Analysis failed' }, { status: 500 })
  }
}

async function runCodeSafeAnalysis(projectPath: string, llmChoice: string, specificFile: string, verbose: boolean): Promise<string> {
  return new Promise((resolve, reject) => {
    const args = ['-r', projectPath, '-l', llmChoice]
    if (specificFile) args.push('-a', specificFile)
    if (verbose) args.push('-v')

    const env = {
      ...process.env,
      OPENAI_API_KEY: process.env.OPENAI_API_KEY,
      ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,
    }

    const codeSafe = spawn('code_safe', args, { env, cwd: join(process.cwd(), '..') })

    let output = ''
    let errorOutput = ''

    codeSafe.stdout.on('data', (d) => (output += d.toString()))
    codeSafe.stderr.on('data', (d) => (errorOutput += d.toString()))

    codeSafe.on('close', (code) => {
      // Accept output even if exit code is non-zero, as long as we have analysis results
      if (output.includes('Analyzing') && (output.includes('vulnerability_types:') || output.includes('VulnType.'))) {
        resolve(output)
      } else if (code === 0) {
        resolve(output)
      } else {
        reject(new Error(`Code Safe analysis failed: ${errorOutput || 'Unknown error'}`))
      }
    })

    codeSafe.on('error', (error) => reject(new Error(`Failed to start Code Safe: ${error.message}`)))

    setTimeout(() => {
      codeSafe.kill()
      reject(new Error('Analysis timed out after 5 minutes'))
    }, 300000)
  })
}

async function formatAnalysisResult(rawOutput: string, analyzedFiles: string[]): Promise<VulnerabilityResult> {
  // Split by "Analyzing" to get individual file analyses
  // Use regex to handle cases where the file path might be split across lines
  const parts = rawOutput.split(/\n\s*Analyzing\s+/)
  
  const fileAnalyses: { file_path: string; findings: any[] }[] = []
  
  for (let i = 0; i < parts.length; i++) {
    const part = parts[i]
    
    if (i === 0) {
      // First part might not start with "Analyzing", check if it contains analysis
      if (part.includes('scratchpad:') || part.includes('analysis:')) {
        // Extract filename from the beginning if present
        const lines = part.split('\n')
        let filename = 'unknown_file'
        let analysisText = part
        
        for (let j = 0; j < Math.min(5, lines.length); j++) {
          const line = lines[j]
          if (line.trim() && !line.startsWith('-') && line.includes('/')) {
            filename = line.trim()
            // Clean up the filename to show only the actual file name
            const cleanFilename = filename.split('/').pop() || filename
            // Remove the filename line from analysis text
            analysisText = lines.slice(lines.indexOf(line) + 1).join('\n')
            filename = cleanFilename
            break
          }
        }
        
        if (analysisText.trim()) {
          fileAnalyses.push(parseFileAnalysis(filename, analysisText))
        }
      }
    } else {
      // Extract filename and analysis from this part
      const lines = part.split('\n')
      if (lines.length > 0) {
        // First line(s) should contain the filename
        let filename = lines[0].trim()
        // Handle case where filename might be split across multiple lines
        const filenameLines: string[] = []
        let analysisStartIdx = 0
        
        for (let j = 0; j < lines.length; j++) {
          const line = lines[j]
          if (line.trim().startsWith('-') || line.includes('scratchpad:')) {
            analysisStartIdx = j
            break
          }
          if (line.trim()) {
            filenameLines.push(line.trim())
          }
        }
        
        if (filenameLines.length > 0) {
          filename = filenameLines.join('')
          // Clean up the filename to show only the actual file name
          const cleanFilename = filename.split('/').pop() || filename
          const analysisText = lines.slice(analysisStartIdx).join('\n')
          if (analysisText.trim()) {
            fileAnalyses.push(parseFileAnalysis(cleanFilename, analysisText))
          }
        }
      }
    }
  }

  const totalVulnerabilities = fileAnalyses.reduce((sum, f) => sum + f.findings.length, 0)
  const allFindings = fileAnalyses.flatMap((f) => f.findings)
  const averageConfidence = allFindings.length > 0 ? allFindings.reduce((s, f) => s + f.confidence_score, 0) / allFindings.length : 0

  const vulnerabilityCounts = { LFI: 0, RCE: 0, SSRF: 0, AFO: 0, SQLI: 0, XSS: 0, IDOR: 0 } as Record<VulnerabilityType, number>
  allFindings.forEach((f) => f.vulnerability_types.forEach((t: VulnerabilityType) => (vulnerabilityCounts[t]++)))

  return {
    project_name: 'Uploaded Project',
    analysis_date: new Date().toISOString(),
    total_files_analyzed: analyzedFiles.length,
    total_vulnerabilities: totalVulnerabilities,
    high_confidence_vulnerabilities: allFindings.filter((f) => f.confidence_score >= 8).length,
    file_analyses: fileAnalyses,
    summary: {
      vulnerability_counts: vulnerabilityCounts,
      average_confidence: averageConfidence,
      most_critical_file: fileAnalyses.length > 0 ? fileAnalyses[0].file_path : null,
    },
  }
}

function parseFileAnalysis(filePath: string, analysisText: string) {
  const sections = analysisText.split(/\-{40,}/)
  const findings: any[] = []
  
  let currentFinding: any = {}
  
  for (const section of sections) {
    const trimmed = section.trim()
    if (!trimmed) continue
    
    if (trimmed.startsWith('scratchpad:')) {
      // Start a new finding if we have a complete one
      if (currentFinding.confidence_score > 0 && currentFinding.analysis) {
        findings.push({ ...currentFinding })
        currentFinding = {}
      }
      currentFinding.scratchpad = trimmed.replace('scratchpad:', '').trim()
    } else if (trimmed.startsWith('analysis:')) {
      currentFinding.analysis = trimmed.replace('analysis:', '').trim()
    } else if (trimmed.startsWith('poc:')) {
      currentFinding.poc = trimmed.replace('poc:', '').trim()
    } else if (trimmed.startsWith('confidence_score:')) {
      const scoreText = trimmed.replace('confidence_score:', '').trim()
      const score = parseInt(scoreText)
      currentFinding.confidence_score = isNaN(score) ? 0 : score
    } else if (trimmed.startsWith('vulnerability_types:')) {
      // Extract vulnerability types from the section
      let vulnMatches = trimmed.match(/VulnType\.(\w+)/g)
      if (vulnMatches) {
        currentFinding.vulnerability_types = vulnMatches.map((m) => m.replace('VulnType.', '') as VulnerabilityType)
      } else {
        // Fallback: look for lines starting with "- VulnType."
        const lines = trimmed.split('\n')
        const vulnTypes: VulnerabilityType[] = []
        for (const line of lines) {
          const cleanLine = line.trim()
          if (cleanLine.startsWith('- VulnType.')) {
            const vulnType = cleanLine.replace('- VulnType.', '').trim() as VulnerabilityType
            vulnTypes.push(vulnType)
          }
        }
        currentFinding.vulnerability_types = vulnTypes
      }
      
      currentFinding.context_code = []
      
      // This is typically the last section, so add the finding
      if (currentFinding.confidence_score > 0 && currentFinding.analysis) {
        findings.push({ ...currentFinding })
        currentFinding = {}
      }
    }
  }
  
  // Add the last finding if exists
  if (currentFinding.confidence_score > 0 && currentFinding.analysis) {
    findings.push(currentFinding)
  }

  return { file_path: filePath, findings }
}

