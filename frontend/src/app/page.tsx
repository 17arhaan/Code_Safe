'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Shield, Zap, AlertTriangle, CheckCircle, FileText, Upload, Settings, ArrowRight } from 'lucide-react'
import FileUpload from '@/components/FileUpload'
import VulnerabilityReport from '@/components/VulnerabilityReport'
import { VulnerabilityResult } from '@/types/vulnerability'

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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse-slow"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-pulse-slow"></div>
      </div>

      {/* Header */}
      <motion.header 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="relative z-10 border-b border-slate-700/50 glass"
      >
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center gap-4">
            <motion.div 
              whileHover={{ scale: 1.1, rotate: 5 }}
              className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/25"
            >
              <Shield className="w-8 h-8 text-white" />
            </motion.div>
            <div>
              <h1 className="text-4xl font-bold text-white">Code Safe</h1>
              <p className="text-slate-300 text-lg">AI-Powered Security Scanner</p>
            </div>
          </div>
        </div>
      </motion.header>

      <main className="relative z-10 max-w-7xl mx-auto px-6 py-12">
        {!results && !isAnalyzing && !error && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8 }}
            className="space-y-20"
          >
            {/* Hero Section */}
            <div className="text-center max-w-5xl mx-auto space-y-8">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="inline-flex items-center gap-2 glass-light px-6 py-3 rounded-full text-blue-300 font-medium"
              >
                <Zap className="w-5 h-5" />
                Powered by GPT-4 & Claude AI
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.4 }}
                className="space-y-6"
              >
                <h2 className="text-6xl md:text-7xl font-bold text-white leading-tight">
                  Discover Security
                  <span className="block text-gradient mt-2">
                    Vulnerabilities
                  </span>
                </h2>
                <p className="text-xl text-slate-300 max-w-4xl mx-auto leading-relaxed">
                  Upload your Python project and let AI analyze it for complex, multi-step security vulnerabilities 
                  that traditional static analysis tools miss.
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.6, delay: 0.8 }}
                className="flex items-center justify-center gap-8 text-sm text-slate-400"
              >
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  7 Vulnerability Types
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                  High Accuracy AI
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                  Detailed Reports
                </div>
              </motion.div>
            </div>

            {/* Features Grid */}
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto"
            >
              {[
                {
                  icon: AlertTriangle,
                  title: "7 Vulnerability Types",
                  description: "Detects RCE, LFI, XSS, SQLI, SSRF, AFO, and IDOR vulnerabilities with high precision.",
                  color: "from-red-500 to-pink-500",
                  delay: 0.1
                },
                {
                  icon: CheckCircle,
                  title: "High Accuracy",
                  description: "AI-powered analysis with confidence scoring to minimize false positives.",
                  color: "from-green-500 to-emerald-500",
                  delay: 0.2
                },
                {
                  icon: FileText,
                  title: "Detailed Reports",
                  description: "Complete analysis with proof-of-concept exploits and remediation guidance.",
                  color: "from-blue-500 to-cyan-500",
                  delay: 0.3
                }
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: feature.delay }}
                  whileHover={{ y: -8, scale: 1.02 }}
                  className="group glass p-8 rounded-3xl hover:shadow-2xl hover:shadow-blue-500/10 transition-all duration-300"
                >
                  <motion.div
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    className={`w-16 h-16 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center mb-6 shadow-lg`}
                  >
                    <feature.icon className="w-8 h-8 text-white" />
                  </motion.div>
                  <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
                  <p className="text-slate-300 leading-relaxed">{feature.description}</p>
                </motion.div>
              ))}
            </motion.div>

            {/* Upload Section */}
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.8 }}
              className="max-w-5xl mx-auto"
            >
              <FileUpload 
                onAnalysisStart={handleAnalysisStart}
                onAnalysisComplete={handleAnalysisComplete}
                onAnalysisError={handleAnalysisError}
              />
            </motion.div>
          </motion.div>
        )}

        {/* Loading State */}
        {isAnalyzing && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="max-w-2xl mx-auto"
          >
            <div className="glass p-12 rounded-3xl text-center shadow-2xl">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-8 shadow-lg shadow-blue-500/25"
              >
                <Shield className="w-12 h-12 text-white" />
              </motion.div>
              <h3 className="text-3xl font-semibold text-white mb-4">Analyzing Your Code</h3>
              <p className="text-slate-300 mb-8 text-lg">
                AI is examining your project for security vulnerabilities...
              </p>
              <div className="w-full bg-slate-700/50 rounded-full h-3 overflow-hidden">
                <motion.div
                  initial={{ width: "0%" }}
                  animate={{ width: "75%" }}
                  transition={{ duration: 3, ease: "easeInOut" }}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full"
                />
              </div>
            </div>
          </motion.div>
        )}

        {/* Error State */}
        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="max-w-2xl mx-auto"
          >
            <div className="bg-red-500/10 border border-red-500/20 rounded-3xl p-8 backdrop-blur-sm">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-14 h-14 bg-red-500/20 rounded-full flex items-center justify-center">
                  <AlertTriangle className="w-7 h-7 text-red-400" />
                </div>
                <h3 className="text-2xl font-semibold text-red-400">Analysis Failed</h3>
              </div>
              <p className="text-red-300 mb-6 leading-relaxed text-lg">{error}</p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={resetAnalysis}
                className="bg-red-500 hover:bg-red-600 text-white px-8 py-3 rounded-xl transition-colors font-medium"
              >
                Try Again
              </motion.button>
            </div>
          </motion.div>
        )}

        {/* Results */}
        {results && (
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <VulnerabilityReport 
              results={results} 
              onReset={resetAnalysis}
            />
          </motion.div>
        )}
      </main>

      {/* Footer */}
      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 1 }}
        className="relative z-10 border-t border-slate-700/50 glass-light mt-24"
      >
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="text-center text-slate-400">
            <p>© 2024 Code Safe - Your Personal Security Scanner</p>
          </div>
        </div>
      </motion.footer>
    </div>
  )
}