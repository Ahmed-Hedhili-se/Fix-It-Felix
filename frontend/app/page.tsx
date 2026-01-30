"use client"
import React, { useState } from 'react';
import { ImageUploader } from '@/components/dashboard/ImageUploader';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { analyzeImage, AnalysisResponse, OperationMode } from '@/lib/analysis';
import { Loader2, AlertTriangle, CheckCircle, FileText, Activity, Server, Shield, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Home() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [userContext, setUserContext] = useState('');
  const [mode, setMode] = useState<OperationMode>('cloud');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResponse | null>(null);

  const handleClear = () => {
    setSelectedImage(null);
    setResult(null);
    setUserContext('');
  };

  const handleAnalyze = async () => {
    if (!selectedImage && !userContext) return;

    setIsAnalyzing(true);
    setResult(null);

    try {
      const data = await analyzeImage(selectedImage, userContext, mode);
      setResult(data);
    } catch (error) {
      console.error(error);
      alert("Analysis failed. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };


  const onImageSelected = (file: File) => {
    setSelectedImage(file);
    setResult(null);
  };

  return (
    <main className="min-h-screen bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black text-slate-200">

      { }
      <header className="border-b border-white/10 glass sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="text-primary w-6 h-6" />
            <h1 className="text-xl font-bold tracking-wider uppercase">
              Fix-It Felix <span className="text-primary text-xs ml-1 bg-yellow-400/10 px-2 py-0.5 rounded border border-primary/20">v2.0 Beta</span>
            </h1>
          </div>
          <div className="flex gap-4">
            { }
            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700"></div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">

        { }
        <div className="lg:col-span-5 space-y-6">
          <div className="space-y-2">
            <h2 className="text-sm uppercase tracking-widest text-slate-500 font-bold">1. Visual Input</h2>
            <ImageUploader
              onImageSelected={onImageSelected}
              selectedImage={selectedImage}
              onClear={handleClear}
            />
          </div>

          <div className="space-y-2">
            <h2 className="text-sm uppercase tracking-widest text-slate-500 font-bold">2. Context Protocol</h2>
            <textarea
              className="w-full h-32 bg-slate-900/50 border border-slate-800 rounded-lg p-4 text-sm focus:border-primary focus:ring-1 focus:ring-primary outline-none transition-all placeholder:text-slate-600 resize-none"
              placeholder="Describe the defect or ask a specific question (e.g., 'Noticed rust on joint B-12')..."
              value={userContext}
              onChange={(e) => setUserContext(e.target.value)}
            />
          </div>


          <div className="space-y-4">
            <h2 className="text-sm uppercase tracking-widest text-slate-500 font-bold">3. Operations Mode</h2>
            <div className="grid grid-cols-3 gap-2">
              <Button
                variant={mode === 'cloud' ? 'default' : 'industrial'}
                size="sm"
                className="h-20 flex flex-col gap-2"
                onClick={() => setMode('cloud')}
              >
                <Server className="w-5 h-5" />
                <span className="text-xs">Cloud Tier (GPT-4o)</span>
              </Button>
              <Button
                variant={mode === 'local' ? 'default' : 'industrial'}
                size="sm"
                className="h-20 flex flex-col gap-2"
                onClick={() => setMode('local')}
              >
                <Shield className="w-5 h-5" />
                <span className="text-xs">Local Privacy</span>
              </Button>
              <Button
                variant={mode === 'fast' ? 'default' : 'industrial'}
                size="sm"
                className="h-20 flex flex-col gap-2"
                onClick={() => setMode('fast')}
              >
                <Zap className="w-5 h-5" />
                <span className="text-xs">Fast / Offline</span>
              </Button>
            </div>
          </div>

          <Button
            className="w-full h-12 text-base shadow-[0_0_20px_rgba(251,191,36,0.15)] mt-4"
            onClick={handleAnalyze}
            disabled={(!selectedImage && !userContext) || isAnalyzing}
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Processing Neural Audit...
              </>
            ) : (
              "Run Diagnostic Analysis"
            )}
          </Button>
        </div>

        { }
        <div className="lg:col-span-7">
          <h2 className="text-sm uppercase tracking-widest text-slate-500 font-bold mb-6">3. Diagnostic Report</h2>

          <AnimatePresence mode="wait">
            {!result && !isAnalyzing && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-[500px] border border-dashed border-slate-800 rounded-lg flex flex-col items-center justify-center text-slate-600 space-y-4"
              >
                <Activity className="w-16 h-16 opacity-20" />
                <p>System Ready. Waiting for input stream...</p>
              </motion.div>
            )}

            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-6"
              >
                { }
                <div className="grid grid-cols-2 gap-4">
                  <Card className="border-l-4 border-l-primary bg-slate-900/80">
                    <CardHeader className="py-4">
                      <CardTitle className="text-xs text-slate-400">Detected Severity</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-black text-red-500 flex items-center gap-2">
                        <AlertTriangle className="w-6 h-6" />
                        {result.analysis.severity}
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="border-l-4 border-l-blue-500 bg-slate-900/80">
                    <CardHeader className="py-4">
                      <CardTitle className="text-xs text-slate-400">Knowledge Base</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-lg font-bold text-blue-400 flex items-center gap-2">
                        <FileText className="w-5 h-5" />
                        {result.knowledge_base.found_match ? "Historical Match Found" : "New Anomaly"}
                      </div>
                      <div className="text-xs text-slate-500 mt-1">
                        Confidence: {(result.knowledge_base.confidence_score * 100).toFixed(1)}%
                      </div>
                    </CardContent>
                  </Card>
                </div>

                { }
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="w-5 h-5 text-primary" />
                      Technical Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <p className="text-slate-300 leading-relaxed">
                      {result.analysis.problem_description}
                    </p>

                    <div className="bg-slate-950/50 p-4 rounded border border-slate-800">
                      <h4 className="text-primary font-bold text-sm mb-2 uppercase flex items-center gap-2">
                        <CheckCircle className="w-4 h-4" /> Recommended Action
                      </h4>
                      <p className="text-slate-300 whitespace-pre-line text-sm">
                        {result.analysis.repair_solution}
                      </p>
                    </div>
                  </CardContent>
                </Card>

                { }
                {result.knowledge_base.found_match && (
                  <Card className="bg-blue-950/20 border-blue-900/30">
                    <CardHeader>
                      <CardTitle className="text-blue-400 text-sm">Reference Case: {result.knowledge_base.document_ref}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-slate-400 italic">
                        "{result.knowledge_base.reference_solution}"
                      </p>
                    </CardContent>
                  </Card>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

      </div>
    </main>
  );
}
