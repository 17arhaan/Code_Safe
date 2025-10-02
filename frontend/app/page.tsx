"use client"

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Shield, Zap, AlertTriangle, CheckCircle, FileText } from 'lucide-react'
import FileUpload from '@/components/FileUpload'
import VulnerabilityReport from '@/components/VulnerabilityReport'
import DetailedVulnerabilityReport from '@/components/DetailedVulnerabilityReport'
import type { VulnerabilityResult } from '@/types/vulnerability'

export default function Home() {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [results, setResults] = useState<VulnerabilityResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleAnalysisStart = () => {
    setIsAnalyzing(true)
    setError(null)
    setResults(null)
  }

  const handleAnalysisComplete = (result: VulnerabilityResult) => {
    setIsAnalyzing(false)
    setResults(result)
  }

  const handleAnalysisError = (errorMessage: string) => {
    setIsAnalyzing(false)
    setError(errorMessage)
  }

  const resetAnalysis = () => {
    setResults(null)
    setError(null)
    setIsAnalyzing(false)
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <motion.header initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="border-b border-border sticky top-0 bg-background/80 backdrop-blur-xl z-50">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <Shield className="w-6 h-6 text-primary-foreground" />
            </div>
            <h1 className="text-2xl font-semibold">Code Safe</h1>
          </div>
        </div>
      </motion.header>

      <main className="max-w-7xl mx-auto px-6 py-16">
        {!results && !isAnalyzing && !error && (
          <div className="space-y-16">
            <div className="text-center max-w-4xl mx-auto space-y-6">
              <div className="inline-flex items-center gap-2 bg-secondary border border-border px-4 py-2 rounded-full text-sm text-foreground/70">
                <Zap className="w-4 h-4 text-primary" /> Powered by GPT-4 & Claude AI
              </div>
              <h2 className="text-5xl md:text-6xl font-bold leading-tight tracking-tight">
                AI-Powered Security <span className="text-primary block mt-2">Vulnerability Scanner</span>
              </h2>
              <p className="text-lg text-foreground/70 max-w-3xl mx-auto">
                Upload your Python project and let AI analyze it for complex, multi-step security vulnerabilities that traditional static analysis tools miss.
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
              {[
                { icon: AlertTriangle, title: '7 Vulnerability Types', description: 'Detects RCE, LFI, XSS, SQLI, SSRF, AFO, and IDOR vulnerabilities.' },
                { icon: CheckCircle, title: 'High Accuracy', description: 'Confidence scoring to minimize false positives using LLMs.' },
                { icon: FileText, title: 'Detailed Reports', description: 'Actionable PoCs and remediation guidance for each finding.' },
              ].map((feature, i) => (
                <div key={i} className="glass p-6 rounded-2xl border border-border">
                  <div className="w-12 h-12 bg-secondary rounded-xl flex items-center justify-center mb-4">
                    <feature.icon className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-foreground/70 text-sm leading-relaxed">{feature.description}</p>
                </div>
              ))}
            </div>

            <div className="max-w-4xl mx-auto">
              <FileUpload onAnalysisStart={handleAnalysisStart} onAnalysisComplete={handleAnalysisComplete} onAnalysisError={handleAnalysisError} />
            </div>
          </div>
        )}

        {isAnalyzing && (
          <div className="max-w-2xl mx-auto">
            <div className="glass p-12 rounded-2xl text-center border border-border">
              <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center mx-auto mb-6">
                <Shield className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-2xl font-semibold mb-3">Analyzing Your Code</h3>
              <p className="text-foreground/70 mb-6">AI is examining your project for security vulnerabilities...</p>
              <div className="w-full bg-secondary rounded-full h-2 overflow-hidden">
                <motion.div initial={{ width: '0%' }} animate={{ width: '75%' }} transition={{ duration: 3, ease: 'easeInOut' }} className="bg-primary h-2 rounded-full" />
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="max-w-2xl mx-auto">
            <div className="glass p-8 rounded-2xl border border-red-900/50">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-red-500/10 rounded-full flex items-center justify-center">
                  <AlertTriangle className="w-5 h-5 text-red-500" />
                </div>
                <h3 className="text-xl font-semibold">Analysis Failed</h3>
              </div>
              <p className="text-foreground/70 mb-6">{error}</p>
              <button onClick={resetAnalysis} className="bg-foreground text-background px-6 py-2.5 rounded-lg hover:opacity-90 transition-colors font-medium text-sm">Try Again</button>
            </div>
          </div>
        )}

        {results && (
          <div className="space-y-8">
            <VulnerabilityReport results={results} onReset={resetAnalysis} />
            <DetailedVulnerabilityReport result={results} />
          </div>
        )}
      </main>

      <footer className="border-t border-border mt-24">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="text-center text-foreground/60 text-sm">
            <p>© 2025 Code Safe. Built by Arhaan Girdhar</p>
          </div>
        </div>
      </footer>
    </div>
  )
}


