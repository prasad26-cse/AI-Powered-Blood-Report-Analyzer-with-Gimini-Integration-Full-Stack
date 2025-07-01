import React, { useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';
import { 
  CloudArrowUpIcon,
  DocumentTextIcon,
  XMarkIcon,
  ArrowLeftIcon,
  MagnifyingGlassIcon,
  CheckCircleIcon,
  ChartBarIcon,
  ChevronDownIcon,
  InformationCircleIcon,
  StarIcon,
  DocumentArrowDownIcon
} from '@heroicons/react/24/outline';
import html2pdf from 'html2pdf.js';
import { useAuth } from '../context/AuthContext';

const UploadReport = () => {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadedReport, setUploadedReport] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [query, setQuery] = useState('Summarize my blood test report');
  const [instructionsVisible, setInstructionsVisible] = useState(true);
  const [showResults, setShowResults] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    summary: true,
    interpretation: true,
    recommendations: true,
    insights: true,
    clinical: true
  });
  const navigate = useNavigate();
  const analysisContentRef = useRef();
  const { user } = useAuth();

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'application/pdf') {
        setFile(droppedFile);
      } else {
        toast.error('Please upload a PDF file');
      }
    }
  }, []);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (selectedFile.type === 'application/pdf') {
        setFile(selectedFile);
      } else {
        toast.error('Please select a PDF file');
      }
    }
  };

  const removeFile = () => {
    setFile(null);
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file to upload');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      console.log('Uploading file:', file.name);
      console.log('Auth headers:', axios.defaults.headers.common);
      
      const response = await axios.post('/api/upload-report', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Upload response:', response.data);
      setUploadedReport(response.data);
      setInstructionsVisible(false);
      toast.success('Report uploaded successfully! Starting analysis...');
      
      // Automatically start analysis after upload
      await handleAnalyze(response.data.report_id);
    } catch (error) {
      console.error('Upload error:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      const errorMessage = error.response?.data?.detail || 'Failed to upload report';
      toast.error(errorMessage);
    } finally {
      setUploading(false);
    }
  };

  const handleAnalyze = async (reportId = null) => {
    const targetReportId = reportId || uploadedReport?.id;
    
    if (!targetReportId) {
      toast.error('No report selected for analysis');
      return;
    }

    if (!query.trim()) {
      toast.error('Please enter a query to analyze');
      return;
    }

    setAnalyzing(true);
    const formData = new FormData();
    formData.append('report_id', targetReportId);
    formData.append('query', query);

    try {
      console.log('Starting analysis for report ID:', targetReportId);
      console.log('Query:', query);
      console.log('Auth headers:', axios.defaults.headers.common);
      
      const response = await axios.post('/api/analyze-report-sync', formData);
      
      console.log('Analysis response:', response.data);
      console.log('Response type:', typeof response.data);
      console.log('Response keys:', Object.keys(response.data));
      console.log('Response.result:', response.data.result);
      console.log('Response.status:', response.data.status);
      
      // Check if the response has the expected structure
      if (response.data) {
        let resultText;
        
        // Handle different response formats
        if (typeof response.data === 'string') {
          // Direct string response
          resultText = response.data;
          console.log('Using direct string response');
        } else if (response.data.result && typeof response.data.result === 'string') {
          // JSON object with result field
          resultText = response.data.result;
          console.log('Using result field from JSON response');
        } else if (response.data.status === 'completed' && response.data.result) {
          // Status object with result
          resultText = response.data.result;
          console.log('Using completed status result');
        } else if (response.data.status === 'processed' && response.data.result) {
          // Processed status with result
          resultText = response.data.result;
          console.log('Using processed status result');
        } else {
          // Fallback: stringify the entire response
          resultText = JSON.stringify(response.data, null, 2);
          console.log('Using fallback JSON stringify');
        }
        
        // Robustly parse resultText if it is a stringified dict
        if (
          typeof resultText === "string" &&
          resultText.trim().startsWith("{") &&
          resultText.includes("'result':")
        ) {
          try {
            const parsed = JSON.parse(resultText.replace(/'/g, '"'));
            if (parsed.result) {
              resultText = parsed.result;
              console.log("Parsed resultText from stringified dict:", resultText);
            }
          } catch (e) {
            // Not JSON, leave as is
            console.log("Could not parse stringified dict resultText:", e);
          }
        }
        
        // Clean up the result text
        if (resultText) {
          // Remove any JSON artifacts and clean up the text
          resultText = resultText
            .replace(/\\n/g, '\n')  // Convert escaped newlines
            .replace(/\\'/g, "'")   // Convert escaped quotes
            .replace(/\\"/g, '"')   // Convert escaped double quotes
            .replace(/^['"]|['"]$/g, '') // Remove leading/trailing quotes
            // Remove any remaining JSON artifacts
            .replace(/,\s*'fallback':\s*False\s*}/g, '') // Remove fallback: False artifacts
            .replace(/,\s*'fallback':\s*true\s*}/g, '') // Remove fallback: true artifacts
            .replace(/,\s*"fallback":\s*false\s*}/g, '') // Remove fallback: false artifacts
            .replace(/,\s*"fallback":\s*true\s*}/g, '') // Remove fallback: true artifacts
            .replace(/,\s*'status':\s*['"][^'"]*['"]\s*}/g, '') // Remove status artifacts
            .replace(/,\s*"status":\s*['"][^'"]*['"]\s*}/g, '') // Remove status artifacts
            .replace(/,\s*'result':\s*['"][^'"]*['"]\s*}/g, '') // Remove result artifacts
            .replace(/,\s*"result":\s*['"][^'"]*['"]\s*}/g, '') // Remove result artifacts
            // Remove any remaining JSON-like structures
            .replace(/\{[^}]*'fallback'[^}]*\}/g, '') // Remove objects with fallback
            .replace(/\{[^}]*"fallback"[^}]*\}/g, '') // Remove objects with fallback
            .replace(/\{[^}]*'status'[^}]*\}/g, '') // Remove objects with status
            .replace(/\{[^}]*"status"[^}]*\}/g, '') // Remove objects with status
            // Clean up extra commas and formatting
            .replace(/,\s*,/g, ',') // Remove double commas
            .replace(/,\s*$/g, '') // Remove trailing commas
            .replace(/^\s*,\s*/g, '') // Remove leading commas
            // Remove any remaining JSON fragments
            .replace(/\{[^}]*\}/g, '') // Remove any remaining JSON objects
            .replace(/\[[^\]]*\]/g, '') // Remove any remaining JSON arrays
            // Clean up extra whitespace and newlines
            .replace(/\n\s*\n\s*\n/g, '\n\n') // Remove excessive newlines
            .replace(/^\s+|\s+$/g, '') // Trim whitespace
            .trim();
        }
        
        console.log('Final resultText:', resultText);
        console.log('ResultText type:', typeof resultText);
        console.log('ResultText length:', resultText?.length);
        
        if (resultText) {
        setAnalysisResult(resultText);
        setShowResults(true); // Show the results section
        toast.success('Analysis completed successfully!');
        
        // Update the uploaded report with analysis status
        if (uploadedReport) {
          setUploadedReport({
            ...uploadedReport,
            status: 'completed',
            analysis_result: resultText
          });
        }

        // Scroll to results section
        setTimeout(() => {
          const resultsSection = document.getElementById('results-section');
          if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }, 500);
        } else {
          // Show a user-friendly message instead of throwing an error
          const fallbackMsg = 'No analysis result was generated for your report. Please ensure your PDF is a valid blood test report or try again later.';
          setAnalysisResult(fallbackMsg);
          setShowResults(true);
          toast.warning(fallbackMsg);
          // Optionally, update uploadedReport status
          if (uploadedReport) {
            setUploadedReport({
              ...uploadedReport,
              status: 'completed',
              analysis_result: fallbackMsg
            });
          }
        }

      } else {
        // Handle unexpected response structure
        setAnalysisResult('Analysis completed but received unexpected response format. Please try again.');
        setShowResults(true);
        toast.warning('Analysis completed with warnings');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      
      let errorMessage = 'Analysis failed';
      
      if (error.response) {
        // Server responded with error status
        const status = error.response.status;
        const detail = error.response.data?.detail || error.response.data?.message || 'Unknown server error';
        
        if (status === 500) {
          errorMessage = 'Server error: The analysis service is temporarily unavailable. Please try again in a few minutes.';
        } else if (status === 404) {
          errorMessage = 'Report not found. Please upload your report again.';
        } else if (status === 401) {
          errorMessage = 'Authentication required. Please log in again.';
        } else {
          errorMessage = `Server error (${status}): ${detail}`;
        }
      } else if (error.request) {
        // Network error
        errorMessage = 'Network error: Unable to connect to the server. Please check your internet connection and try again.';
      } else {
        // Other error
        errorMessage = `Error: ${error.message}`;
      }
      
      toast.error(errorMessage);
      
      // Set a fallback result for better UX
      setAnalysisResult(`Analysis failed: ${errorMessage}. Your report has been uploaded successfully. Please try the analysis again later.`);
      setShowResults(true);
    } finally {
      setAnalyzing(false);
    }
  };

  const resetUpload = () => {
    setUploadedReport(null);
    setAnalysisResult(null);
    setFile(null);
    setQuery('Summarize my blood test report');
    setInstructionsVisible(true);
    setShowResults(false);
  };

  const goToDashboard = () => {
    toast.success('Redirecting to dashboard...');
    setTimeout(() => {
      navigate('/dashboard');
    }, 1000);
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const parseAnalysisResult = (result) => {
    if (!result) return {};
    
    const sections = {
      summary: '',
      interpretation: '',
      recommendations: '',
      insights: '',
      clinical: ''
    };

    // Clean up the result text first
    let cleanResult = result
      .replace(/\\n/g, '\n')  // Convert escaped newlines
      .replace(/\\'/g, "'")   // Convert escaped quotes
      .replace(/\\"/g, '"')   // Convert escaped double quotes
      .replace(/^['"]|['"]$/g, '') // Remove leading/trailing quotes
      // Remove any remaining JSON artifacts
      .replace(/,\s*'fallback':\s*False\s*}/g, '') // Remove fallback: False artifacts
      .replace(/,\s*'fallback':\s*true\s*}/g, '') // Remove fallback: true artifacts
      .replace(/,\s*"fallback":\s*false\s*}/g, '') // Remove fallback: false artifacts
      .replace(/,\s*"fallback":\s*true\s*}/g, '') // Remove fallback: true artifacts
      .replace(/,\s*'status':\s*['"][^'"]*['"]\s*}/g, '') // Remove status artifacts
      .replace(/,\s*"status":\s*['"][^'"]*['"]\s*}/g, '') // Remove status artifacts
      .replace(/,\s*'result':\s*['"][^'"]*['"]\s*}/g, '') // Remove result artifacts
      .replace(/,\s*"result":\s*['"][^'"]*['"]\s*}/g, '') // Remove result artifacts
      // Remove any remaining JSON-like structures
      .replace(/\{[^}]*'fallback'[^}]*\}/g, '') // Remove objects with fallback
      .replace(/\{[^}]*"fallback"[^}]*\}/g, '') // Remove objects with fallback
      .replace(/\{[^}]*'status'[^}]*\}/g, '') // Remove objects with status
      .replace(/\{[^}]*"status"[^}]*\}/g, '') // Remove objects with status
      // Clean up extra commas and formatting
      .replace(/,\s*,/g, ',') // Remove double commas
      .replace(/,\s*$/g, '') // Remove trailing commas
      .replace(/^\s*,\s*/g, '') // Remove leading commas
      // Remove any remaining JSON fragments
      .replace(/\{[^}]*\}/g, '') // Remove any remaining JSON objects
      .replace(/\[[^\]]*\]/g, '') // Remove any remaining JSON arrays
      // Clean up extra whitespace and newlines
      .replace(/\n\s*\n\s*\n/g, '\n\n') // Remove excessive newlines
      .replace(/^\s+|\s+$/g, '') // Trim whitespace
      .trim();

    const lines = cleanResult.split('\n');
    let currentSection = '';
    let sectionContent = [];
    
    lines.forEach(line => {
      const trimmedLine = line.trim();
      
      // Check for section headers with different patterns and enhance them
      if (trimmedLine.includes('**1. Summary') || 
          trimmedLine.includes('**Summary') || 
          trimmedLine.includes('Summary of Key Findings')) {
        // Save previous section content
        if (currentSection && sectionContent.length > 0) {
          sections[currentSection] = sectionContent.join('\n');
        }
        currentSection = 'summary';
        sectionContent = [];
      } else if (trimmedLine.includes('**2. Interpretation') || 
                 trimmedLine.includes('**Interpretation') ||
                 trimmedLine.includes('Interpretation of Any abnormal Values')) {
        if (currentSection && sectionContent.length > 0) {
          sections[currentSection] = sectionContent.join('\n');
        }
        currentSection = 'interpretation';
        sectionContent = [];
      } else if (trimmedLine.includes('**3. Clinical') || 
                 trimmedLine.includes('**Clinical') ||
                 trimmedLine.includes('Clinical Significance of Results')) {
        if (currentSection && sectionContent.length > 0) {
          sections[currentSection] = sectionContent.join('\n');
        }
        currentSection = 'clinical';
        sectionContent = [];
      } else if (trimmedLine.includes('**4. Recommendations') || 
                 trimmedLine.includes('**Recommendations') ||
                 trimmedLine.includes('Recommendations for follow-up')) {
        if (currentSection && sectionContent.length > 0) {
          sections[currentSection] = sectionContent.join('\n');
        }
        currentSection = 'recommendations';
        sectionContent = [];
      } else if (trimmedLine.includes('**5. General Health') || 
                 trimmedLine.includes('**General Health') ||
                 trimmedLine.includes('General Health Insights Based on the Results')) {
        if (currentSection && sectionContent.length > 0) {
          sections[currentSection] = sectionContent.join('\n');
        }
        currentSection = 'insights';
        sectionContent = [];
      } else if (currentSection && trimmedLine) {
        // Add content to current section, but skip empty lines and section headers
        if (trimmedLine && 
            !trimmedLine.startsWith('**') && 
            !trimmedLine.includes('Blood Test Report Summary') &&
            !trimmedLine.includes('important Note') &&
            !trimmedLine.includes('Important Note')) {
          
          // Clean up the line content and enhance formatting
          let cleanLine = trimmedLine
            .replace(/^\*\s*/, '')  // Remove leading asterisks
            .replace(/^\d+\.\s*/, '')  // Remove numbered lists
            .trim();
          
          if (cleanLine) {
            sectionContent.push(cleanLine);
          }
        }
      }
    });

    // Save the last section
    if (currentSection && sectionContent.length > 0) {
      sections[currentSection] = sectionContent.join('\n');
    }

    // Clean up each section and add proper structure with enhanced visual formatting
    Object.keys(sections).forEach(key => {
      if (sections[key]) {
        let content = sections[key]
          .replace(/\n\s*\n\s*\n/g, '\n\n')  // Remove excessive newlines
          .replace(/^\s+|\s+$/g, '')  // Trim whitespace
          .trim();

        // Add enhanced structure to recommendations section
        if (key === 'recommendations' && content) {
          const lines = content.split('\n');
          const structuredLines = lines.map((line, index) => {
            const trimmed = line.trim();
            if (trimmed.startsWith('Diet') || trimmed.startsWith('Lifestyle') || 
                trimmed.startsWith('Repeat') || trimmed.startsWith('Consider') ||
                trimmed.startsWith('Further') || trimmed.startsWith('Maintaining') ||
                trimmed.startsWith('Addressing') || trimmed.startsWith('Regular') ||
                trimmed.startsWith('Healthy') || trimmed.startsWith('Balanced')) {
              return `🔹 ${trimmed}`;
            }
            return trimmed;
          });
          content = structuredLines.join('\n');
        }

        // Add enhanced structure to interpretation section
        if (key === 'interpretation' && content) {
          const lines = content.split('\n');
          const structuredLines = lines.map((line, index) => {
            const trimmed = line.trim();
            if (trimmed.includes('mg/dL') || trimmed.includes('triglycerides') ||
                trimmed.includes('cholesterol') || trimmed.includes('HDL') ||
                trimmed.includes('LDL')) {
              return `🔸 ${trimmed}`;
            }
            return trimmed;
          });
          content = structuredLines.join('\n');
        }

        // Add enhanced structure to clinical section
        if (key === 'clinical' && content) {
          const lines = content.split('\n');
          const structuredLines = lines.map((line, index) => {
            const trimmed = line.trim();
            if (trimmed.includes('attention') || trimmed.includes('warrant') ||
                trimmed.includes('risk') || trimmed.includes('complications')) {
              return `⚠️ ${trimmed}`;
            }
            return trimmed;
          });
          content = structuredLines.join('\n');
        }

        // Add enhanced structure to insights section
        if (key === 'insights' && content) {
          const lines = content.split('\n');
          const structuredLines = lines.map((line, index) => {
            const trimmed = line.trim();
            if (trimmed.includes('health') || trimmed.includes('well-being') ||
                trimmed.includes('lifestyle') || trimmed.includes('diet') ||
                trimmed.includes('exercise')) {
              return `💡 ${trimmed}`;
            }
            return trimmed;
          });
          content = structuredLines.join('\n');
        }

        sections[key] = content;
      }
    });

    return sections;
  };

  const highlightImportantTerms = (text) => {
    if (!text) return '';
    
    // Clean the text first
    let cleanText = text
      .replace(/\n/g, '\n')
      .replace(/'/g, "'")
      .replace(/"/g, '"')
      .trim();
    
    // Define important medical terms and their colors
    const importantTerms = {
      'high': 'text-red-600 font-semibold',
      'low': 'text-blue-600 font-semibold',
      'normal': 'text-green-600 font-semibold',
      'abnormal': 'text-red-600 font-semibold',
      'elevated': 'text-orange-600 font-semibold',
      'decreased': 'text-blue-600 font-semibold',
      'critical': 'text-red-700 font-bold',
      'urgent': 'text-red-600 font-bold',
      'consult': 'text-purple-600 font-semibold',
      'monitor': 'text-yellow-600 font-semibold',
      'follow-up': 'text-blue-600 font-semibold',
      'immediate': 'text-red-600 font-bold',
      'severe': 'text-red-600 font-semibold',
      'moderate': 'text-orange-600 font-semibold',
      'mild': 'text-yellow-600 font-semibold',
      'borderline': 'text-orange-600 font-semibold',
      'optimal': 'text-green-600 font-semibold',
      'protective': 'text-green-600 font-semibold',
      'risk': 'text-red-600 font-semibold',
      'recommended': 'text-blue-600 font-semibold',
      'important': 'text-purple-600 font-semibold',
      'crucial': 'text-red-600 font-bold',
      'beneficial': 'text-green-600 font-semibold',
      'acceptable': 'text-green-600 font-semibold',
      'concerning': 'text-red-600 font-semibold',
      'warrant': 'text-orange-600 font-semibold',
      'mitigate': 'text-blue-600 font-semibold',
      'preventing': 'text-green-600 font-semibold',
      'cardiovascular': 'text-red-600 font-semibold',
      'heart disease': 'text-red-600 font-semibold',
      'cholesterol': 'text-orange-600 font-semibold',
      'triglycerides': 'text-orange-600 font-semibold',
      'HDL': 'text-green-600 font-semibold',
      'LDL': 'text-orange-600 font-semibold',
      'hemoglobin': 'text-blue-600 font-semibold',
      'platelet': 'text-blue-600 font-semibold',
      'glucose': 'text-blue-600 font-semibold',
      'vitamin d': 'text-blue-600 font-semibold',
      'vitamin d level': 'text-blue-600 font-semibold',
      'lipid panel': 'text-orange-600 font-semibold',
      'calcium': 'text-blue-600 font-semibold',
      'desirable': 'text-green-600 font-semibold',
      'adequate': 'text-green-600 font-semibold',
      'healthy': 'text-green-600 font-semibold',
      'lifestyle': 'text-blue-600 font-semibold',
      'diet': 'text-blue-600 font-semibold',
      'exercise': 'text-blue-600 font-semibold',
      'physical activity': 'text-blue-600 font-semibold',
      'weight': 'text-blue-600 font-semibold',
      'alcohol': 'text-orange-600 font-semibold',
      'saturated': 'text-red-600 font-semibold',
      'trans fats': 'text-red-600 font-semibold',
      'lipoprotein': 'text-blue-600 font-semibold',
      'fasting': 'text-blue-600 font-semibold',
      'family history': 'text-purple-600 font-semibold',
      'medical history': 'text-purple-600 font-semibold',
      'comprehensive': 'text-purple-600 font-semibold',
      'professional': 'text-purple-600 font-semibold',
      'physician': 'text-purple-600 font-semibold',
      'clinical': 'text-purple-600 font-semibold'
    };

    let highlightedText = cleanText;

    // Always bold these terms in addition to color
    const boldTerms = [
      'cholesterol', 'triglycerides', 'vitamin d', 'lipid panel', 'vitamin d level'
    ];
    Object.entries(importantTerms).forEach(([term, className]) => {
      const isBold = boldTerms.includes(term.toLowerCase());
      const regex = new RegExp(`\\b${term}\\b`, 'gi');
      highlightedText = highlightedText.replace(regex, (match) =>
        isBold
          ? `<strong class="${className}">${match}</strong>`
          : `<span class="${className}">${match}</span>`
      );
    });

    // Add 🔹 and blue bold to lines starting with 'Lifestyle'
    highlightedText = highlightedText.replace(
      /(^|\n)(Lifestyle)(:)?/g,
      (match, p1, p2, p3) =>
        `${p1}<span class="text-blue-600 font-bold">🔹 ${p2}${p3 || ''}</span>`
    );

    return highlightedText;
  };

  const renderSection = (title, content, sectionKey, icon, color = 'blue', number = 1) => {
    if (!content || !content.trim()) return null;

    const isExpanded = expandedSections[sectionKey];
    
    // Define emoji icons for each section
    const sectionIcons = {
      'Summary': '📋',
      'Clinical Interpretation': '🏥',
      'Detailed Interpretation': '🔬',
      'Recommendations': '💊',
      'General Health Insights': '🌟'
    };

    const sectionNumbers = {
      'Summary': 1,
      'Clinical Interpretation': 2,
      'Detailed Interpretation': 3,
      'Recommendations': 4,
      'General Health Insights': 5
    };

    const sectionIcon = sectionIcons[title] || '📄';
    const sectionNumber = sectionNumbers[title] || number;

    const formatContent = (text, sectionKey = '') => {
      if (!text) return '';
      let formattedText = text
        .replace(/\\n/g, '\n')
        .replace(/\\'/g, "'")
        .replace(/\\"/g, '"')
        .replace(/\s+'$/g, '') // Remove stray single quote at end of string
        .replace(/\*\*([^*]+)\*\*/g, '$1') // Remove all ** from text
        .trim();

      // Convert bullet points and numbered lists with enhanced visual indicators
      formattedText = formattedText
        .replace(/^🔹\s+(.+)$/gm, '<li class="mb-3 flex items-start space-x-3"><span class="text-blue-500 text-lg">🔹</span><span class="flex-1">$1</span></li>')
        .replace(/^🔸\s+(.+)$/gm, '<li class="mb-3 flex items-start space-x-3"><span class="text-orange-500 text-lg">🔸</span><span class="flex-1">$1</span></li>')
        .replace(/^⚠️\s+(.+)$/gm, '<li class="mb-3 flex items-start space-x-3"><span class="text-red-500 text-lg">⚠️</span><span class="flex-1">$1</span></li>')
        .replace(/^💡\s+(.+)$/gm, '<li class="mb-3 flex items-start space-x-3"><span class="text-yellow-500 text-lg">💡</span><span class="flex-1">$1</span></li>')
        .replace(/^\*\s+(.+)$/gm, '<li class="mb-3 flex items-start space-x-3"><span class="text-purple-500 text-lg">•</span><span class="flex-1">$1</span></li>')
        .replace(/^\d+\.\s+(.+)$/gm, '<li class="mb-3 flex items-start space-x-3"><span class="w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0">$1</span><span class="flex-1">$2</span></li>')
        .replace(/^-\s+(.+)$/gm, '<li class="mb-3 flex items-start space-x-3"><span class="text-green-500 text-lg">•</span><span class="flex-1">$1</span></li>')
        .replace(/^(Diet|Lifestyle|Repeat|Consider|Further|Maintaining|Addressing|Regular|Healthy|Balanced)\s+(.+)$/gm, '<li class="mb-3 flex items-start space-x-3"><span class="text-indigo-500 text-lg">🔹</span><span class="flex-1"><strong class="text-indigo-600">$1:</strong> $2</span></li>')
        .replace(/\n\n/g, '</p><p class="mb-4 text-gray-700 leading-relaxed">')
        .replace(/^(.+)$/gm, '<p class="mb-4 text-gray-700 leading-relaxed">$1</p>')
        .replace(/<p class="mb-4 text-gray-700 leading-relaxed"><\/p>/g, '')
        .replace(/<p class="mb-4 text-gray-700 leading-relaxed"><p class="mb-4 text-gray-700 leading-relaxed">/g, '<p class="mb-4 text-gray-700 leading-relaxed">')
        .replace(/<\/p><\/p>/g, '</p>');

      if (formattedText.includes('<li')) {
        formattedText = formattedText
          .replace(/<p class="mb-4 text-gray-700 leading-relaxed"><li/g, '<li')
          .replace(/<\/li><\/p>/g, '</li>')
          .replace(/<p class="mb-4 text-gray-700 leading-relaxed">/g, '<ul class="space-y-2 mb-6 bg-gray-50 rounded-lg p-4 border border-gray-200">')
          .replace(/<\/p>/g, '</ul>');
      }
      return formattedText;
    };

    return (
      <div key={sectionKey} className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <button
          onClick={() => toggleSection(sectionKey)}
          className="w-full px-6 py-4 bg-gradient-to-r from-gray-50 to-gray-100 hover:from-gray-100 hover:to-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-inset transition-all duration-200 flex items-center justify-between"
        >
          <div className="flex items-center space-x-3">
            <span className="text-2xl">{sectionIcon}</span>
            <h3 className="text-lg font-bold text-gray-900">
              <span className="mr-2">{sectionNumber}.</span> {title}
            </h3>
          </div>
          <ChevronDownIcon 
            className={`h-5 w-5 text-gray-500 transition-transform duration-200 ${
              isExpanded ? 'rotate-180' : ''
            }`} 
          />
        </button>
        
        {isExpanded && (
          <div className="px-6 py-4 border-t border-gray-200 bg-white">
            <div 
              className="prose prose-medical max-w-none"
              dangerouslySetInnerHTML={{ __html: formatContent(content) }}
            />
          </div>
        )}
      </div>
    );
  };

  const createCleanDisplayText = (text) => {
    if (!text) return '';
    return text
      .replace(/\\n/g, '\n')
      .replace(/\\'/g, "'")
      .replace(/\\"/g, '"')
      .replace(/^['"]|['"]$/g, '')
      // Remove JSON artifacts and malformed content
      .replace(/,\s*'fallback':\s*False\s*}/g, '')
      .replace(/,\s*'fallback':\s*true\s*}/g, '')
      .replace(/,\s*"fallback":\s*false\s*}/g, '')
      .replace(/,\s*"fallback":\s*true\s*}/g, '')
      .replace(/,\s*'status':\s*['"][^'"]*['"]\s*}/g, '')
      .replace(/,\s*"status":\s*['"][^'"]*['"]\s*}/g, '')
      .replace(/,\s*'result':\s*['"][^'"]*['"]\s*}/g, '')
      .replace(/,\s*"result":\s*['"][^'"]*['"]\s*}/g, '')
      .replace(/\{[^}]*'fallback'[^}]*\}/g, '')
      .replace(/\{[^}]*"fallback"[^}]*\}/g, '')
      .replace(/\{[^}]*'status'[^}]*\}/g, '')
      .replace(/\{[^}]*"status"[^}]*\}/g, '')
      .replace(/,\s*,/g, ',')
      .replace(/,\s*$/g, '')
      .replace(/^\s*,\s*/g, '')
      .replace(/\{[^}]*\}/g, '')
      .replace(/\[[^\]]*\]/g, '')
      .replace(/\*\*([^*]+)\*\*/g, '$1') // Remove all ** from text
      .replace(/\*([^*]+)\*/g, '$1') // Remove all * from text
      .replace(/\n\s*\n\s*\n/g, '\n\n')
      .trim();
  };

  const exportToText = () => {
    if (!analysisResult) return;
    
    // Create clean text for export
    const cleanText = createCleanDisplayText(analysisResult);
    
    const element = document.createElement('a');
    const file = new Blob([cleanText], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `blood-test-analysis-${uploadedReport?.filename?.replace('.pdf', '') || 'report'}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // Enhanced PDF export function with Gemini AI footer
  const exportToPDF = () => {
    const analysis = parseAnalysisResult(analysisResult);
    const tempDiv = document.createElement('div');
    tempDiv.style.background = '#fff';
    tempDiv.style.fontFamily = 'Arial, sans-serif';
    tempDiv.style.padding = '20px';
    tempDiv.style.width = '100%';
    tempDiv.style.maxWidth = '800px';
    tempDiv.style.boxSizing = 'border-box';
    tempDiv.style.lineHeight = '1.6';
    
    // Function to format content specifically for PDF
    const formatContentForPDF = (text, sectionKey = '') => {
      if (!text) return '';
      let formatted = text
        .replace(/\*\*([^*]+)\*\*/g, '<strong style="font-weight: bold; color: #1e293b;">$1</strong>')
        .replace(/\*([^*]+)\*/g, '<em style="font-style: italic; color: #475569;">$1</em>')
        .replace(/(normal|good|excellent|healthy)/gi, '<span style="color: #059669; font-weight: 600;">$1</span>')
        .replace(/(elevated|high|concerning|abnormal)/gi, '<span style="color: #d97706; font-weight: 600;">$1</span>')
        .replace(/(critical|dangerous|severe)/gi, '<span style="color: #dc2626; font-weight: 600;">$1</span>');
      
      // Enhanced formatting for insights section in PDF
      if (sectionKey === 'insights') {
        // Highlight section titles with better styling and prevent page breaks
        formatted = formatted
          .replace(/(Dietary and Lifestyle Modifications|Repeat Blood Tests|Vitamin D Supplementation|Comprehensive Cardiovascular Risk Assessment|HbA1c test)/gi, 
            '<div style="page-break-inside: avoid; break-inside: avoid; font-size: 16px; font-weight: bold; color: #7c3aed; margin: 15px 0 8px 0; border-bottom: 2px solid #7c3aed; padding-bottom: 4px;">$1</div>')
          // Prevent breaking of key medical terms
          .replace(/(Vitamin D|HbA1c|HDL|LDL|BMI|CBC|CMP)/gi, '<span style="white-space: nowrap; font-weight: 600;">$1</span>')
          // Convert numbered lists with proper formatting and page break prevention
          .replace(/(\d+\.\s+)/g, '<div style="page-break-inside: avoid; break-inside: avoid; margin: 12px 0 8px 0; padding: 10px; background: #f8f7ff; border-left: 3px solid #7c3aed; border-radius: 6px;"><strong style="color: #7c3aed;">$1</strong>')
          // Convert bullet points with page break prevention
          .replace(/(•\s+|- \s+)/g, '<div style="page-break-inside: avoid; break-inside: avoid; margin: 8px 0 6px 20px; padding: 8px; background: #f8f7ff; border-left: 2px solid #7c3aed; border-radius: 4px;">• ')
          // Add proper paragraph breaks with page break prevention
          .replace(/([.!?])\s+(?=[A-Z][a-z])/g, '$1</div><div style="page-break-inside: avoid; break-inside: avoid; margin: 10px 0; padding: 8px; background: #f8f7ff; border-left: 2px solid #7c3aed; border-radius: 4px;">')
          // Close divs properly
          .replace(/(<div[^>]*>.*?)(?=<div|$)/g, '$1</div>');
      }
      
      // Enhanced formatting for recommendations section in PDF
      if (sectionKey === 'recommendations') {
        formatted = formatted
          // Wrap each recommendation in a container that won't break
          .replace(/(Dietary Review|Exercise Plan|Medication Review|Follow-up Testing|Lifestyle Modifications|Nutrition Consultation|Physical Activity|Stress Management|Sleep Hygiene|Weight Management|Smoking Cessation|Alcohol Moderation|Blood Pressure Monitoring|Blood Sugar Monitoring|Cholesterol Management|Vitamin Supplementation|Mental Health Support|Cardiovascular Health|Diabetes Management|Hypertension Control)/gi, 
            '<div style="page-break-inside: avoid; break-inside: avoid; margin: 15px 0; padding: 12px; background: #fef7f7; border-left: 3px solid #dc2626; border-radius: 6px;"><strong style="color: #991b1b; font-size: 15px;">$1:</strong>')
          // Close recommendation containers
          .replace(/([.!?])\s+(?=[A-Z][a-z][^:]*:)/g, '$1</div><div style="page-break-inside: avoid; break-inside: avoid; margin: 15px 0; padding: 12px; background: #fef7f7; border-left: 3px solid #dc2626; border-radius: 6px;"><strong style="color: #991b1b; font-size: 15px;">')
          // Handle numbered recommendations
          .replace(/(\d+\.\s+)/g, '<div style="page-break-inside: avoid; break-inside: avoid; margin: 12px 0; padding: 10px; background: #fef7f7; border-left: 3px solid #dc2626; border-radius: 6px;"><strong style="color: #991b1b;">$1</strong>')
          // Add proper paragraph breaks
          .replace(/([.!?])\s+(?=[A-Z][a-z])/g, '$1</div><div style="page-break-inside: avoid; break-inside: avoid; margin: 8px 0;">')
          // Close any remaining open divs
          .replace(/(<div[^>]*>.*?)(?=<div|$)/g, '$1</div>');
      }
      
      return formatted;
    };
    
    // Create comprehensive PDF content with improved layout and pagination
    const pdfContent = `
      <div style="page-break-inside: avoid; break-inside: avoid; margin-bottom: 30px; padding: 20px; background: #f8fafc; border: 2px solid #e2e8f0; border-radius: 8px;">
        <div style="font-size: 24px; font-weight: 700; color: #1e293b; margin-bottom: 10px; text-align: center;">Blood Test Analysis Report</div>
        <div style="font-size: 18px; font-weight: 600; color: #475569; margin-bottom: 8px; text-align: center;">${file?.name || 'Blood Test Report'}</div>
        <div style="font-size: 14px; color: #64748b; text-align: center;">
          Patient: ${user?.full_name || 'N/A'} | Email: ${user?.email || 'N/A'} | Generated: ${new Date().toLocaleDateString()}
        </div>
      </div>
      
      ${analysis.summary ? `
      <div class="summary-section" style="page-break-inside: avoid; break-inside: avoid; margin-bottom: 25px; padding: 20px; background: #eff6ff; border-left: 5px solid #2563eb; border-radius: 8px;">
        <h2 style="font-size: 18px; font-weight: bold; color: #1e40af; margin-bottom: 15px; margin-top: 0;">📋 Summary of Key Findings</h2>
        <div style="font-size: 14px; color: #1e293b; line-height: 1.8; text-align: justify; page-break-inside: avoid; break-inside: avoid;">
          ${formatContentForPDF(analysis.summary)}
        </div>
      </div>
      ` : ''}
      
      ${analysis.interpretation ? `
      <div class="interpretation-section" style="page-break-inside: avoid; break-inside: avoid; margin-bottom: 25px; padding: 20px; background: #fef3c7; border-left: 5px solid #d97706; border-radius: 8px;">
        <h2 style="font-size: 18px; font-weight: bold; color: #92400e; margin-bottom: 15px; margin-top: 0;">🔍 Interpretation of Abnormal Values</h2>
        <div style="font-size: 14px; color: #1e293b; line-height: 1.8; text-align: justify; page-break-inside: avoid; break-inside: avoid;">
          ${formatContentForPDF(analysis.interpretation)}
        </div>
      </div>
      ` : ''}
      
      ${analysis.clinical ? `
      <div class="clinical-section" style="page-break-inside: avoid; break-inside: avoid; margin-bottom: 25px; padding: 20px; background: #f0fdf4; border-left: 5px solid #059669; border-radius: 8px;">
        <h2 style="font-size: 18px; font-weight: bold; color: #047857; margin-bottom: 15px; margin-top: 0;">🏥 Clinical Significance of Results</h2>
        <div style="font-size: 14px; color: #1e293b; line-height: 1.8; text-align: justify; page-break-inside: avoid; break-inside: avoid;">
          ${formatContentForPDF(analysis.clinical)}
        </div>
      </div>
      ` : ''}
      
      ${analysis.recommendations ? `
      <div class="recommendation-block" style="page-break-inside: avoid; break-inside: avoid; margin-bottom: 25px; padding: 20px; background: #fef2f2; border-left: 5px solid #dc2626; border-radius: 8px;">
        <h2 style="font-size: 18px; font-weight: bold; color: #991b1b; margin-bottom: 15px; margin-top: 0;">💡 Recommendations for Follow-up</h2>
        <div style="font-size: 14px; color: #1e293b; line-height: 1.8; text-align: justify; page-break-inside: avoid; break-inside: avoid;">
          ${formatContentForPDF(analysis.recommendations, 'recommendations')}
        </div>
      </div>
      ` : ''}
      
      ${analysis.insights ? `
      <div class="insight-block" style="page-break-inside: avoid; break-inside: avoid; margin-bottom: 25px; padding: 20px; background: #f3e8ff; border-left: 5px solid #7c3aed; border-radius: 8px;">
        <h2 style="font-size: 18px; font-weight: bold; color: #5b21b6; margin-bottom: 15px; margin-top: 0;">💊 General Health Insights</h2>
        <div style="font-size: 14px; color: #1e293b; line-height: 1.8; text-align: justify; word-wrap: break-word; hyphens: auto; page-break-inside: avoid; break-inside: avoid;">
          ${formatContentForPDF(analysis.insights, 'insights')}
        </div>
      </div>
      ` : ''}
      
      <div style="page-break-inside: avoid; break-inside: avoid; margin-top: 40px; padding: 25px; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border: 2px solid #cbd5e1; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <div style="margin-bottom: 15px;">
          <div style="display: inline-block; padding: 8px 16px; background: #1e293b; color: white; border-radius: 20px; font-size: 14px; font-weight: 600; margin-bottom: 10px;">
            🤖 AI-Generated Analysis Report
          </div>
        </div>
        
        <div style="margin-bottom: 15px;">
          <p style="font-size: 16px; font-weight: 600; color: #1e293b; margin: 0 0 8px 0; line-height: 1.4;">
            Generated by Google Gemini AI Technology
          </p>
          <p style="font-size: 14px; color: #475569; margin: 0; line-height: 1.5;">
            This comprehensive blood test analysis was powered by advanced artificial intelligence
          </p>
        </div>
        
        <div style="display: flex; justify-content: center; align-items: center; gap: 20px; margin-bottom: 15px; flex-wrap: wrap;">
          <div style="display: flex; align-items: center; gap: 6px;">
            <span style="color: #059669; font-size: 16px;">✓</span>
            <span style="font-size: 12px; color: #64748b;">AI-Powered Analysis</span>
          </div>
          <div style="display: flex; align-items: center; gap: 6px;">
            <span style="color: #059669; font-size: 16px;">✓</span>
            <span style="font-size: 12px; color: #64748b;">Medical Knowledge Base</span>
          </div>
          <div style="display: flex; align-items: center; gap: 6px;">
            <span style="color: #059669; font-size: 16px;">✓</span>
            <span style="font-size: 12px; color: #64748b;">Comprehensive Review</span>
          </div>
        </div>
        
        <div style="border-top: 1px solid #cbd5e1; padding-top: 15px;">
          <p style="font-size: 13px; color: #64748b; margin: 0 0 8px 0; line-height: 1.4;">
            <strong>Important Notice:</strong> This analysis is generated by artificial intelligence and should be used as a reference only.
          </p>
          <p style="font-size: 12px; color: #94a3b8; margin: 0; line-height: 1.4;">
            For medical decisions, diagnosis, and treatment plans, please consult with a qualified healthcare professional.
          </p>
        </div>
        
        <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #cbd5e1;">
          <p style="font-size: 11px; color: #94a3b8; margin: 0; line-height: 1.3;">
            Report generated on ${new Date().toLocaleDateString()} at ${new Date().toLocaleTimeString()} | 
            AI-Based Blood Test Analysis System v1.0
          </p>
        </div>
      </div>
    `;
    
    tempDiv.innerHTML = pdfContent;
    
    // Get full_name from context
    let fullName = 'report';
    if (user?.full_name) {
      fullName = user.full_name.replace(/\s+/g, '_');
    }
    
    html2pdf().set({
      margin: [0.75, 0.5, 0.75, 0.5], // [top, right, bottom, left] margins
      filename: `${fullName}_complete_blood_analysis.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { 
        scale: 2,
        useCORS: true,
        allowTaint: true,
        letterRendering: true
      },
      jsPDF: { 
        unit: 'in', 
        format: 'a4', 
        orientation: 'portrait',
        compress: true
      },
      pagebreak: { 
        mode: ['avoid-all', 'css', 'legacy'],
        before: '.page-break-before',
        after: '.page-break-after',
        avoid: '.recommendation-block, .insight-block, .summary-section, .interpretation-section, .clinical-section'
      }
    }).from(tempDiv).save();
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate('/dashboard')}
          className="p-2 text-medical-600 hover:text-medical-900 transition-colors"
        >
          <ArrowLeftIcon className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-medical-900">Upload Blood Report</h1>
          <p className="mt-2 text-medical-600">
            Upload your blood test report PDF for AI analysis
          </p>
        </div>
      </div>

      {/* Upload Area */}
      <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-8">
        {file ? (
          <div className="space-y-4">
            <div className="flex items-center space-x-4 p-4 bg-medical-50 rounded-lg border border-medical-200">
              <DocumentTextIcon className="h-8 w-8 text-primary-600" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-medical-900 truncate">
                  {file.name}
                </p>
                <p className="text-sm text-medical-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              <button
                onClick={removeFile}
                className="p-1 text-medical-400 hover:text-medical-600 transition-colors"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>
            
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {uploading ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Uploading...</span>
                </div>
              ) : (
                'Upload Report'
              )}
            </button>
          </div>
        ) : instructionsVisible ? (
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive 
                ? 'border-primary-400 bg-primary-50' 
                : 'border-medical-300 hover:border-medical-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <CloudArrowUpIcon className="mx-auto h-12 w-12 text-medical-400" />
            <div className="mt-4">
              <label htmlFor="file-upload" className="cursor-pointer">
                <span className="mt-2 block text-sm font-medium text-medical-900">
                  <span className="text-primary-600 hover:text-primary-500">
                    Click to upload
                  </span>{' '}
                  or drag and drop
                </span>
                <span className="mt-1 block text-xs text-medical-500">
                  PDF files only, max 10MB
                </span>
              </label>
              <input
                id="file-upload"
                name="file-upload"
                type="file"
                className="sr-only"
                accept=".pdf"
                onChange={handleFileSelect}
              />
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-medical-600 mb-4">Upload completed. You can upload another file if needed.</p>
            <button
              onClick={resetUpload}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Upload Another Report
            </button>
          </div>
        )}
      </div>

      {/* Loading State for Analysis */}
      {analyzing && (
        <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <h3 className="text-lg font-semibold text-medical-900 mb-2">Analyzing Your Report</h3>
            <p className="text-medical-600">Please wait while our AI analyzes your blood test results...</p>
          </div>
        </div>
      )}

      {/* Analysis Section - Show after upload but hide when results are shown */}
      {uploadedReport && !showResults && (
        <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
          <h2 className="text-lg font-semibold text-medical-900 mb-4">Analyze Your Report</h2>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="analysis-query" className="block text-sm font-medium text-medical-700 mb-2">
                What would you like to know about your report?
              </label>
              <textarea
                id="analysis-query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., Summarize my blood test report, Are there any concerning values?, What do these results mean?"
                className="w-full px-3 py-3 border border-medical-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                rows="3"
              />
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={() => handleAnalyze()}
                disabled={analyzing || !query.trim()}
                className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {analyzing ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <MagnifyingGlassIcon className="h-4 w-4" />
                    <span>Analyze Report</span>
                  </>
                )}
              </button>
              
              <button
                onClick={() => navigate('/dashboard')}
                className="px-4 py-2 border border-medical-300 text-medical-700 rounded-lg hover:bg-medical-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
              >
                Go to Dashboard
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Results Section */}
      {showResults && analysisResult && (
        <div id="results-section" className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
          {/* Success message and navigation/buttons (not in PDF) */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="h-5 w-5 text-green-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-green-800">
                  Analysis completed successfully!
                </p>
                <p className="text-sm text-green-700 mt-1">
                  Your blood test report has been analyzed and the results are ready for review.
                </p>
              </div>
            </div>
          </div>
          <div className="flex space-x-3 analysis-nav-row mb-6">
            <button
              onClick={exportToText}
              className="inline-flex items-center px-4 py-2 border border-medical-300 shadow-sm text-sm font-medium rounded-lg text-medical-700 bg-white hover:bg-medical-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
            >
              <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
              Export
            </button>
            <button
              onClick={exportToPDF}
              className="inline-flex items-center px-4 py-2 border border-medical-300 shadow-sm text-sm font-medium rounded-lg text-medical-700 bg-white hover:bg-medical-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
            >
              <DocumentArrowDownIcon className="h-4 w-4 mr-2" />
              Download PDF
            </button>
              <button
                onClick={() => handleAnalyze()}
                disabled={analyzing || !query.trim()}
                className="inline-flex items-center px-4 py-2 border border-medical-300 shadow-sm text-sm font-medium rounded-lg text-medical-700 bg-white hover:bg-medical-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <MagnifyingGlassIcon className="h-4 w-4 mr-2" />
                Re-analyze
              </button>
              <button
                onClick={goToDashboard}
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
              >
                <ChartBarIcon className="h-4 w-4 mr-2" />
                View in Dashboard
              </button>
            </div>
          {/* Only analysis content below is wrapped in the ref for PDF export */}
          <div ref={analysisContentRef}>
            {/* Key Highlights */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 mb-6">
              <div className="flex items-center mb-3">
                <StarIcon className="h-5 w-5 text-blue-600 mr-2" />
                <h3 className="text-lg font-semibold text-blue-900">Key Highlights</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm text-blue-800">Analysis completed with AI insights</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-sm text-blue-800">Professional medical interpretation</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <span className="text-sm text-blue-800">Personalized recommendations</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  <span className="text-sm text-blue-800">Health insights and trends</span>
                </div>
              </div>
            </div>

            {/* Quick Summary */}
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-4 mb-6">
              <div className="flex items-center mb-3">
                <InformationCircleIcon className="h-5 w-5 text-green-600 mr-2" />
                <h3 className="text-lg font-semibold text-green-900">Quick Summary</h3>
              </div>
              <div className="space-y-2">
                {(() => {
                  const parsedSections = parseAnalysisResult(analysisResult);
                  const summary = parsedSections.summary || '';
                  const lines = summary.split('\n').slice(0, 3); // Take first 3 lines
                  return lines.map((line, index) => (
                    <div key={index} className="flex items-start space-x-2">
                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                      <p className="text-sm text-green-800">{line}</p>
                    </div>
                  ));
                })()}
              </div>
            </div>
            
            {/* Structured Analysis Results */}
            <div className="space-y-4">
              {(() => {
                const parsedSections = parseAnalysisResult(analysisResult);
                
                return (
                  <>
                    {renderSection(
                      'Summary',
                      parsedSections.summary,
                      'summary',
                      undefined,
                      undefined,
                      1
                    )}
                    
                    {renderSection(
                      'Clinical Interpretation',
                      parsedSections.clinical,
                      'clinical',
                      undefined,
                      undefined,
                      2
                    )}
                    
                    {renderSection(
                      'Detailed Interpretation',
                      parsedSections.interpretation,
                      'interpretation',
                      undefined,
                      undefined,
                      3
                    )}
                    
                    {renderSection(
                      'Recommendations',
                      parsedSections.recommendations,
                      'recommendations',
                      undefined,
                      undefined,
                      4
                    )}
                    
                    {renderSection(
                      'General Health Insights',
                      parsedSections.insights,
                      'insights',
                      undefined,
                      undefined,
                      5
                    )}
                    
                    {/* Fallback for unstructured results */}
                    {!parsedSections.summary && !parsedSections.interpretation && (
                      <div className="bg-medical-50 border border-medical-200 rounded-lg p-6">
                        <h3 className="text-lg font-semibold text-medical-900 mb-4">Complete Analysis</h3>
                        <div className="space-y-4">
                          {(() => {
                            const cleanText = createCleanDisplayText(analysisResult);
                            const paragraphs = cleanText.split('\n\n').filter(p => p.trim());
                            return paragraphs.map((paragraph, index) => (
                              <div key={index} className="bg-white rounded-lg p-4 shadow-sm">
                                <div className="flex items-start space-x-3">
                                  <div className="w-6 h-6 bg-medical-600 text-white rounded-full flex items-center justify-center text-sm font-semibold flex-shrink-0">
                                    {index + 1}
                                  </div>
                                  <div 
                                    className="prose prose-medical max-w-none text-medical-800 leading-relaxed"
                                    dangerouslySetInnerHTML={{ 
                                      __html: highlightImportantTerms(paragraph.replace(/\n/g, '<br>')) 
                                    }}
                                  />
                                </div>
                              </div>
                            ));
                          })()}
                        </div>
                      </div>
                    )}
                  </>
                );
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadReport; 