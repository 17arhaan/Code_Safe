"use client"

import { useState, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useDropzone } from "react-dropzone"
import { Upload, File, X, Zap, Brain, Cpu } from "lucide-react"
import type { VulnerabilityResult } from "../types/vulnerability"

interface FileUploadProps {
  onAnalysisStart: () => void
  onAnalysisComplete: (result: VulnerabilityResult) => void
  onAnalysisError: (error: string) => void
}

export default function FileUpload({ onAnalysisStart, onAnalysisComplete, onAnalysisError }: FileUploadProps) {
  const [files, setFiles] = useState<File[]>([])
  const [llmChoice, setLlmChoice] = useState<"gpt" | "claude">("gpt")
  const [specificFile, setSpecificFile] = useState("")
  const [verbose, setVerbose] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const validFiles = acceptedFiles.filter((file) => {
      const name = file.name.toLowerCase()
      return (
        name.endsWith(".py") ||
        name.endsWith(".txt") ||
        name.endsWith(".md") ||
        name.endsWith(".yml") ||
        name.endsWith(".yaml") ||
        name.endsWith(".json") ||
        name.endsWith(".toml") ||
        name.endsWith(".cfg") ||
        name.endsWith(".ini")
      )
    })

    setFiles((prev) => [...prev, ...validFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/x-python": [".py"],
      "text/plain": [".txt", ".md", ".yml", ".yaml", ".toml", ".cfg", ".ini"],
      "application/json": [".json"],
    },
    multiple: true,
  })

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleAnalyze = async () => {
    if (files.length === 0) {
      onAnalysisError("Please upload at least one file")
      return
    }

    onAnalysisStart()

    try {
      const formData = new FormData()
      files.forEach((file) => {
        formData.append("files", file)
      })
      formData.append("llm_choice", llmChoice)
      if (specificFile) {
        formData.append("specific_file", specificFile)
      }
      formData.append("verbose", verbose.toString())

      const response = await fetch("http://localhost:8000/api/analyze", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Analysis failed")
      }

      const result = await response.json()
      onAnalysisComplete(result)
    } catch (error) {
      onAnalysisError(error instanceof Error ? error.message : "Unknown error occurred")
    }
  }

  return (
    // The problem is that the opening <div className="space-y-6"> is never closed in this file,
    // which causes the lint error: "JSX element 'div' has no corresponding closing tag."
    // To fix this, ensure that every opening <div> has a corresponding closing </div>.
    // The code below is correct *so far* (the error is not in this selection), but the file is missing a closing </div> for this one.
    <div className="space-y-6">
      {/* 
        The error is due to passing DOM event handlers (from getRootProps) to a Framer Motion component.
        Framer Motion's motion.div does not accept all native div props, especially event handlers like onClick, onDrag, etc.
        Solution: Use a plain div as the dropzone root, and nest motion.div inside for animation.
      */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all ${
          isDragActive ? "border-blue-500 bg-blue-500/5" : "border-neutral-800 hover:border-neutral-700 bg-neutral-950"
        }`}
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          whileHover={{ scale: 1.01 }}
        >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-4">
          <motion.div
            animate={{
              y: isDragActive ? [0, -10, 0] : 0,
              scale: isDragActive ? 1.1 : 1,
            }}
            transition={{
              y: { duration: 1, repeat: isDragActive ? Number.POSITIVE_INFINITY : 0, ease: "easeInOut" },
              scale: { duration: 0.3 },
            }}
            className={`w-16 h-16 rounded-full flex items-center justify-center transition-colors ${
              isDragActive ? "bg-blue-500/10" : "bg-neutral-900"
            }`}
          >
            <Upload className={`w-8 h-8 ${isDragActive ? "text-blue-500" : "text-neutral-400"}`} />
          </motion.div>
          <motion.div animate={{ scale: isDragActive ? 1.05 : 1 }} transition={{ duration: 0.2 }} className="space-y-2">
            <h3 className="text-xl font-semibold text-white">
              {isDragActive ? "Drop files here" : "Upload Python Project"}
            </h3>
            <p className="text-neutral-400 text-sm">Drag & drop Python files (.py) or click to browse</p>
            <p className="text-neutral-600 text-xs">Also supports: .txt, .md, .yml, .json, .toml files</p>
          </motion.div>
        </div>
      </motion.div>
      </div>

      <AnimatePresence mode="wait">
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className="glass rounded-2xl p-6"
          >
            <h4 className="text-lg font-semibold text-white mb-4">Uploaded Files ({files.length})</h4>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {files.map((file, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.3, delay: index * 0.05, ease: [0.22, 1, 0.36, 1] }}
                  whileHover={{ x: 4 }}
                  className="flex items-center justify-between bg-neutral-900 rounded-xl p-3 group hover:bg-neutral-800 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <motion.div
                      whileHover={{ rotate: 360 }}
                      transition={{ duration: 0.6 }}
                      className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center"
                    >
                      <File className="w-5 h-5 text-blue-500" />
                    </motion.div>
                    <div>
                      <span className="text-white font-medium text-sm">{file.name}</span>
                      <p className="text-neutral-500 text-xs">{(file.size / 1024).toFixed(1)} KB</p>
                    </div>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.1, rotate: 90 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={() => removeFile(index)}
                    className="w-8 h-8 hover:bg-neutral-700 rounded-lg flex items-center justify-center transition-all opacity-0 group-hover:opacity-100"
                  >
                    <X className="w-4 h-4 text-neutral-400" />
                  </motion.button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2, ease: [0.22, 1, 0.36, 1] }}
        className="glass rounded-2xl p-6"
      >
        <h4 className="text-lg font-semibold text-white mb-6">Analysis Settings</h4>

        <div className="space-y-6">
          <div className="space-y-3">
            <label className="block text-sm font-medium text-neutral-400">AI Model</label>
            <div className="grid grid-cols-2 gap-3">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setLlmChoice("gpt")}
                className={`p-4 rounded-xl text-left transition-all ${
                  llmChoice === "gpt"
                    ? "bg-blue-500 text-white"
                    : "bg-neutral-900 text-neutral-400 hover:bg-neutral-800"
                }`}
              >
                <div className="flex items-center gap-2">
                  <Brain className="w-5 h-5" />
                  <div>
                    <div className="font-semibold text-sm">GPT-4</div>
                    <div className="text-xs opacity-75">Recommended</div>
                  </div>
                </div>
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setLlmChoice("claude")}
                className={`p-4 rounded-xl text-left transition-all ${
                  llmChoice === "claude"
                    ? "bg-blue-500 text-white"
                    : "bg-neutral-900 text-neutral-400 hover:bg-neutral-800"
                }`}
              >
                <div className="flex items-center gap-2">
                  <Cpu className="w-5 h-5" />
                  <div>
                    <div className="font-semibold text-sm">Claude</div>
                    <div className="text-xs opacity-75">Alternative</div>
                  </div>
                </div>
              </motion.button>
            </div>
          </div>

          <div className="space-y-3">
            <label className="block text-sm font-medium text-neutral-400">Focus on Specific File (Optional)</label>
            <motion.input
              whileFocus={{ scale: 1.01 }}
              type="text"
              value={specificFile}
              onChange={(e) => setSpecificFile(e.target.value)}
              placeholder="e.g., app.py"
              className="w-full px-4 py-3 bg-neutral-900 border border-neutral-800 rounded-xl text-white placeholder-neutral-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-sm"
            />
          </div>

          <motion.div whileHover={{ x: 2 }} className="flex items-center gap-3">
            <input
              type="checkbox"
              id="verbose"
              checked={verbose}
              onChange={(e) => setVerbose(e.target.checked)}
              className="w-5 h-5 text-blue-500 bg-neutral-900 border-neutral-800 rounded focus:ring-blue-500 focus:ring-2"
            />
            <label htmlFor="verbose" className="text-neutral-400 cursor-pointer text-sm">
              Verbose mode (detailed analysis steps)
            </label>
          </motion.div>
        </div>
      </motion.div>

      <motion.button
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4, ease: [0.22, 1, 0.36, 1] }}
        whileHover={{ scale: files.length > 0 ? 1.02 : 1 }}
        whileTap={{ scale: files.length > 0 ? 0.98 : 1 }}
        onClick={handleAnalyze}
        disabled={files.length === 0}
        className="w-full bg-white hover:bg-neutral-200 disabled:bg-neutral-900 disabled:cursor-not-allowed text-black disabled:text-neutral-600 font-semibold py-4 px-6 rounded-xl transition-all text-sm"
      >
        <div className="flex items-center justify-center gap-2">
          <Zap className="w-5 h-5" />
          <span>Analyze for Vulnerabilities</span>
        </div>
      </motion.button>
    </div>
  )
}
