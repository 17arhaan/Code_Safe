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
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      <motion.header initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="border-b border-border sticky top-0 bg-background/80 backdrop-blur-xl z-50">
        <div className="max-w-7xl mx-auto px-4 md:px-6 py-4 md:py-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 md:w-10 md:h-10 bg-primary rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 md:w-6 md:h-6 text-primary-foreground" />
            </div>
            <h1 className="text-xl md:text-2xl font-semibold">Code Safe</h1>
          </div>
        </div>
      </motion.header>

      <main className="flex-1 max-w-7xl mx-auto px-4 md:px-6 py-8 md:py-16 w-full">
        {!results && !isAnalyzing && !error && (
          <div className="space-y-16">
            <div className="text-center max-w-4xl mx-auto space-y-6">
              <div className="inline-flex items-center gap-2 bg-secondary border border-border px-3 md:px-4 py-2 rounded-full text-xs md:text-sm text-foreground/70">
                <Zap className="w-3 h-3 md:w-4 md:h-4 text-primary" /> Powered by GPT-4 & Claude AI
              </div>
              <h2 className="text-3xl md:text-5xl lg:text-6xl font-bold leading-tight tracking-tight">
                AI-Powered Security <span className="text-primary block mt-2">Vulnerability Scanner</span>
              </h2>
              <p className="text-base md:text-lg text-foreground/70 max-w-3xl mx-auto px-4">
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
            <div className="glass p-8 md:p-12 rounded-2xl text-center border border-border">
              {/* Animated Shield Icon */}
              <div className="relative w-16 h-16 mx-auto mb-6">
                <motion.div
                  className="absolute inset-0 bg-primary/20 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                />
                <motion.div
                  className="absolute inset-2 bg-secondary rounded-full flex items-center justify-center"
                  animate={{ rotate: 360 }}
                  transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                >
                  <Shield className="w-8 h-8 text-primary" />
                </motion.div>
              </div>
              
              <h3 className="text-xl md:text-2xl font-semibold mb-3">Analyzing Your Code</h3>
              <p className="text-foreground/70 mb-6 text-sm md:text-base">
                AI is examining your project for security vulnerabilities...
              </p>
              
              {/* Enhanced Progress Bar */}
              <div className="space-y-4">
                <div className="w-full bg-secondary rounded-full h-3 overflow-hidden relative">
                  <motion.div 
                    initial={{ width: '0%' }} 
                    animate={{ 
                      width: ['0%', '15%', '35%', '60%', '85%', '95%', '95%', '95%']
                    }} 
                    transition={{ 
                      duration: 120, // 2 minutes to feel realistic
                      times: [0, 0.1, 0.3, 0.5, 0.7, 0.85, 0.95, 1],
                      ease: 'easeInOut'
                    }} 
                    className="bg-gradient-to-r from-primary via-primary/90 to-primary/80 h-3 rounded-full relative"
                  >
                    {/* Animated shimmer effect */}
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                      animate={{ x: ['-100%', '100%'] }}
                      transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
                    />
                  </motion.div>
                </div>
                
                {/* Dynamic Progress Percentage */}
                <motion.div 
                  className="text-center text-xs text-foreground/50 font-mono"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5 }}
                >
                  <motion.span
                    animate={{ 
                      opacity: [1, 0.5, 1]
                    }}
                    transition={{ 
                      duration: 2, 
                      repeat: Infinity, 
                      ease: 'easeInOut' 
                    }}
                  >
                    Analyzing... This may take 1-3 minutes
                  </motion.span>
                </motion.div>
                
                {/* Analysis Steps */}
                <div className="space-y-3 text-sm text-foreground/60">
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 }}
                    className="flex items-center justify-center gap-2"
                  >
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="w-3 h-3 border-2 border-primary border-t-transparent rounded-full"
                    />
                    <span>Parsing code structure and dependencies...</span>
                  </motion.div>
                  
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 8 }}
                    className="flex items-center justify-center gap-2"
                  >
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="w-3 h-3 border-2 border-orange-500 border-t-transparent rounded-full"
                    />
                    <span>Running AI security analysis with LLM...</span>
                  </motion.div>
                  
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 25 }}
                    className="flex items-center justify-center gap-2"
                  >
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full"
                    />
                    <span>Analyzing vulnerability patterns and confidence...</span>
                  </motion.div>
                  
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 45 }}
                    className="flex items-center justify-center gap-2"
                  >
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                      className="w-3 h-3 border-2 border-green-500 border-t-transparent rounded-full"
                    />
                    <span>Generating detailed vulnerability report...</span>
                  </motion.div>
                </div>
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

      {!isAnalyzing && (
        <footer className="border-t border-border mt-12 md:mt-24">
          <div className="max-w-7xl mx-auto px-4 md:px-6 py-6 md:py-8">
            <div className="text-center text-foreground/60 text-xs md:text-sm">
              <p>© 2025 Code Safe. Built by Arhaan Girdhar</p>
            </div>
          </div>
        </footer>
      )}
    </div>
  )
}


