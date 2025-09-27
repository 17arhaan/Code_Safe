'use client'

import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, Settings, Zap, Plus, Brain, Cpu } from 'lucide-react'
import { VulnerabilityResult } from '@/types/vulnerability'

interface FileUploadProps {
  onAnalysisStart: () => void
  onAnalysisComplete: (result: VulnerabilityResult) => void
  onAnalysisError: (error: string) => void
}

export default function FileUpload({ onAnalysisStart, onAnalysisComplete, onAnalysisError }: FileUploadProps) {
  const [files, setFiles] = useState<File[]>([])
  const [llmChoice, setLlmChoice] = useState<'gpt' | 'claude'>('gpt')
  const [specificFile, setSpecificFile] = useState('')
  const [verbose, setVerbose] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const validFiles = acceptedFiles.filter(file => {
      const name = file.name.toLowerCase()
      return name.endsWith('.py') || 
             name.endsWith('.txt') || 
             name.endsWith('.md') || 
             name.endsWith('.yml') || 
             name.endsWith('.yaml') ||
             name.endsWith('.json') ||
             name.endsWith('.toml') ||
             name.endsWith('.cfg') ||
             name.endsWith('.ini')
    })
    
    setFiles(prev => [...prev, ...validFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/x-python': ['.py'],
      'text/plain': ['.txt', '.md', '.yml', '.yaml', '.toml', '.cfg', '.ini'],
      'application/json': ['.json']
    },
    multiple: true
  })

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleAnalyze = async () => {
    if (files.length === 0) {
      onAnalysisError('Please upload at least one file')
      return
    }

    onAnalysisStart()

    try {
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files', file)
      })
      formData.append('llm_choice', llmChoice)
      if (specificFile) {
        formData.append('specific_file', specificFile)
      }
      formData.append('verbose', verbose.toString())

      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Analysis failed')
      }

      const result = await response.json()
      onAnalysisComplete(result)
    } catch (error) {
      onAnalysisError(error instanceof Error ? error.message : 'Unknown error occurred')
    }
  }

  return (
    <div className="space-y-8">
      {/* File Upload Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        {...getRootProps()}
        className={`group relative border-2 border-dashed rounded-3xl p-16 text-center cursor-pointer transition-all duration-300 ${
          isDragActive
            ? 'border-blue-400 bg-blue-500/10 scale-105'
            : 'border-slate-600 glass hover:border-slate-500 hover:bg-slate-800/30'
        }`}
      >
        <input {...getInputProps()} />
        <motion.div 
          className="flex flex-col items-center gap-6"
          whileHover={{ scale: 1.02 }}
        >
          <motion.div
            animate={isDragActive ? { scale: 1.2, rotate: 10 } : { scale: 1, rotate: 0 }}
            className={`w-24 h-24 rounded-full flex items-center justify-center transition-all duration-300 ${
              isDragActive 
                ? 'bg-blue-500/20 shadow-lg shadow-blue-500/25' 
                : 'bg-slate-700/50 group-hover:bg-slate-600/50'
            }`}
          >
            {isDragActive ? (
              <Plus className="w-12 h-12 text-blue-400" />
            ) : (
              <Upload className="w-12 h-12 text-slate-400 group-hover:text-slate-300" />
            )}
          </motion.div>
          <div className="space-y-3">
            <h3 className="text-3xl font-semibold text-white">
              {isDragActive ? 'Drop files here' : 'Upload Python Project'}
            </h3>
            <p className="text-xl text-slate-300">
              Drag & drop Python files (.py) or click to browse
            </p>
            <p className="text-sm text-slate-500">
              Also supports: .txt, .md, .yml, .json, .toml files
            </p>
          </div>
        </motion.div>
      </motion.div>

      {/* Uploaded Files */}
      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.4 }}
            className="glass rounded-3xl p-8"
          >
            <h4 className="text-2xl font-semibold text-white mb-6">
              Uploaded Files ({files.length})
            </h4>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {files.map((file, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="flex items-center justify-between glass-light rounded-2xl p-4 group hover:bg-slate-700/30 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-blue-500/20 rounded-xl flex items-center justify-center">
                      <File className="w-6 h-6 text-blue-400" />
                    </div>
                    <div>
                      <span className="text-white font-medium text-lg">{file.name}</span>
                      <p className="text-slate-400 text-sm">
                        {(file.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => removeFile(index)}
                    className="w-10 h-10 bg-slate-600/50 hover:bg-red-500/20 hover:text-red-400 rounded-full flex items-center justify-center transition-all opacity-0 group-hover:opacity-100"
                  >
                    <X className="w-5 h-5" />
                  </motion.button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Analysis Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="glass rounded-3xl p-8"
      >
        <div className="flex items-center gap-3 mb-8">
          <div className="w-12 h-12 bg-slate-700/50 rounded-xl flex items-center justify-center">
            <Settings className="w-6 h-6 text-slate-400" />
          </div>
          <h4 className="text-2xl font-semibold text-white">Analysis Settings</h4>
        </div>
        
        <div className="space-y-8">
          {/* LLM Choice */}
          <div className="space-y-4">
            <label className="block text-lg font-medium text-slate-300">
              AI Model
            </label>
            <div className="grid grid-cols-2 gap-4">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setLlmChoice('gpt')}
                className={`p-6 rounded-2xl text-left transition-all duration-200 ${
                  llmChoice === 'gpt'
                    ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/25'
                    : 'glass-light text-slate-300 hover:bg-slate-700/30'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Brain className="w-6 h-6" />
                  <div>
                    <div className="font-semibold text-lg">GPT-4</div>
                    <div className="text-sm opacity-75">Recommended</div>
                  </div>
                </div>
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setLlmChoice('claude')}
                className={`p-6 rounded-2xl text-left transition-all duration-200 ${
                  llmChoice === 'claude'
                    ? 'bg-gradient-to-br from-purple-500 to-purple-600 text-white shadow-lg shadow-purple-500/25'
                    : 'glass-light text-slate-300 hover:bg-slate-700/30'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Cpu className="w-6 h-6" />
                  <div>
                    <div className="font-semibold text-lg">Claude</div>
                    <div className="text-sm opacity-75">Alternative</div>
                  </div>
                </div>
              </motion.button>
            </div>
          </div>

          {/* Specific File */}
          <div className="space-y-4">
            <label className="block text-lg font-medium text-slate-300">
              Focus on Specific File (Optional)
            </label>
            <input
              type="text"
              value={specificFile}
              onChange={(e) => setSpecificFile(e.target.value)}
              placeholder="e.g., app.py"
              className="w-full px-6 py-4 bg-slate-800/50 border border-slate-600 rounded-2xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-lg"
            />
          </div>

          {/* Verbose Mode */}
          <div className="flex items-center gap-4">
            <input
              type="checkbox"
              id="verbose"
              checked={verbose}
              onChange={(e) => setVerbose(e.target.checked)}
              className="w-6 h-6 text-blue-500 bg-slate-800 border-slate-600 rounded focus:ring-blue-500 focus:ring-2"
            />
            <label htmlFor="verbose" className="text-slate-300 cursor-pointer text-lg">
              Verbose mode (detailed analysis steps)
            </label>
          </div>
        </div>
      </motion.div>

      {/* Analyze Button */}
      <motion.button
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        whileHover={{ scale: 1.02, y: -2 }}
        whileTap={{ scale: 0.98 }}
        onClick={handleAnalyze}
        disabled={files.length === 0}
        className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:from-slate-600 disabled:to-slate-700 disabled:cursor-not-allowed text-white font-semibold py-6 px-8 rounded-3xl transition-all shadow-lg hover:shadow-xl hover:shadow-blue-500/25 disabled:shadow-none text-xl btn-pulse"
      >
        <div className="flex items-center justify-center gap-3">
          <Zap className="w-6 h-6" />
          <span>Analyze for Vulnerabilities</span>
        </div>
      </motion.button>
    </div>
  )
}
