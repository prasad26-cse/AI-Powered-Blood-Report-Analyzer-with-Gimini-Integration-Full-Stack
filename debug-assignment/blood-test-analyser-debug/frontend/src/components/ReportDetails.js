import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import axios from 'axios';
import { 
  ArrowLeftIcon,
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
  ChartBarIcon,
  CalendarIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  DocumentArrowDownIcon,
  EyeIcon,
  EyeSlashIcon,
  StarIcon,
  InformationCircleIcon,
  ExclamationCircleIcon,
  CheckIcon
} from '@heroicons/react/24/outline';

const ReportDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [expandedSections, setExpandedSections] = useState({
    summary: true,
    interpretation: true,
    recommendations: true,
    insights: true
  });
  const [showExtractedText, setShowExtractedText] = useState(false);

  const fetchReportDetails = useCallback(async () => {
    try {
      const response = await axios.get(`/api/report/${id}`);
      setReport(response.data);
      if (response.data.analysis_result) {
        setAnalysisResult(response.data.analysis_result);
      }
    } catch (error) {
      toast.error('Failed to fetch report details');
      console.error('Error fetching report:', error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchReportDetails();
  }, [fetchReportDetails]);

  const handleAnalyze = async () => {
    if (!query.trim()) {
      toast.error('Please enter a query');
      return;
    }

    setAnalyzing(true);
    const formData = new FormData();
    formData.append('report_id', id);
    formData.append('query', query);

    try {
      const response = await axios.post('/api/analyze-report-sync', formData);
      setAnalysisResult(response.data.result);
      setAnalyzing(false);
      toast.success('Analysis completed!');
      fetchReportDetails(); // Refresh report data
    } catch (error) {
      setAnalyzing(false);
      toast.error('Analysis failed: ' + (error.response?.data?.detail || 'Unknown error'));
      console.error('Error during analysis:', error);
    }
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const exportToPDF = () => {
    const element = document.getElementById('analysis-report');
    const opt = {
      margin: 1,
      filename: `blood-test-analysis-${report?.filename?.replace('.pdf', '')}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };
    
    // Import html2pdf dynamically
    import('html2pdf.js').then(html2pdf => {
      html2pdf().set(opt).from(element).save();
    });
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

    const lines = result.split('\n');
    let currentSection = '';
    
    lines.forEach(line => {
      const trimmedLine = line.trim();
      
      if (trimmedLine.includes('**1. Summary') || trimmedLine.includes('**Summary')) {
        currentSection = 'summary';
      } else if (trimmedLine.includes('**2. Interpretation') || trimmedLine.includes('**Interpretation')) {
        currentSection = 'interpretation';
      } else if (trimmedLine.includes('**3. Clinical') || trimmedLine.includes('**Clinical')) {
        currentSection = 'clinical';
      } else if (trimmedLine.includes('**4. Recommendations') || trimmedLine.includes('**Recommendations')) {
        currentSection = 'recommendations';
      } else if (trimmedLine.includes('**5. General Health') || trimmedLine.includes('**General Health')) {
        currentSection = 'insights';
      } else if (currentSection && trimmedLine) {
        sections[currentSection] += (sections[currentSection] ? '\n' : '') + line;
      }
    });

    return sections;
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'processing':
        return <ClockIcon className="h-5 w-5 text-yellow-500 animate-pulse" />;
      case 'failed':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderSection = (title, content, sectionKey, icon) => {
    if (!content) return null;
    
    return (
      <div className="bg-white rounded-xl shadow-sm border border-medical-200 overflow-hidden">
        <button
          onClick={() => toggleSection(sectionKey)}
          className="w-full px-6 py-4 flex items-center justify-between bg-gradient-to-r from-medical-50 to-white hover:from-medical-100 transition-all duration-200"
        >
          <div className="flex items-center space-x-3">
            {icon}
            <h3 className="text-lg font-semibold text-medical-900">{title}</h3>
          </div>
          {expandedSections[sectionKey] ? (
            <ChevronUpIcon className="h-5 w-5 text-medical-600" />
          ) : (
            <ChevronDownIcon className="h-5 w-5 text-medical-600" />
          )}
        </button>
        
        {expandedSections[sectionKey] && (
          <div className="px-6 pb-6">
            <div className="prose prose-medical max-w-none">
              {content.split('\n').map((line, index) => {
                const trimmedLine = line.trim();
                if (!trimmedLine) return <br key={index} />;
                
                // Highlight important keywords
                const highlightedLine = trimmedLine
                  .replace(/\*\*(.*?)\*\*/g, '<strong class="text-medical-900 font-semibold">$1</strong>')
                  .replace(/\*(.*?)\*/g, '<em class="text-medical-700 italic">$1</em>')
                  .replace(/(normal|good|excellent|healthy)/gi, '<span class="text-green-600 font-medium">$1</span>')
                  .replace(/(elevated|high|concerning|abnormal)/gi, '<span class="text-orange-600 font-medium">$1</span>')
                  .replace(/(critical|dangerous|severe)/gi, '<span class="text-red-600 font-medium">$1</span>');
                
                return (
                  <p key={index} className="mb-3 text-medical-800 leading-relaxed" 
                     dangerouslySetInnerHTML={{ __html: highlightedLine }} />
                );
              })}
            </div>
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="text-center py-12">
        <p className="text-medical-600">Report not found</p>
      </div>
    );
  }

  const parsedAnalysis = parseAnalysisResult(analysisResult);

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="p-2 text-medical-600 hover:text-medical-900 transition-colors"
          >
            <ArrowLeftIcon className="h-5 w-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-medical-900">Blood Test Analysis Report</h1>
            <p className="mt-2 text-medical-600">
              {report.filename}
            </p>
          </div>
        </div>
        
        {analysisResult && (
          <button
            onClick={exportToPDF}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            <DocumentArrowDownIcon className="h-4 w-4" />
            <span>Export PDF</span>
          </button>
        )}
      </div>

      {/* Report Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
          <div className="flex items-center space-x-3">
            <DocumentTextIcon className="h-8 w-8 text-blue-600" />
            <div>
              <p className="text-sm font-medium text-blue-600">Status</p>
              <div className="flex items-center space-x-2 mt-1">
                {getStatusIcon(report.status)}
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                  {report.status}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border border-green-200">
          <div className="flex items-center space-x-3">
            <CalendarIcon className="h-8 w-8 text-green-600" />
            <div>
              <p className="text-sm font-medium text-green-600">Upload Date</p>
              <p className="text-sm text-green-900 font-medium">{formatDate(report.upload_date)}</p>
            </div>
          </div>
        </div>

        {report.confidence_score && (
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
            <div className="flex items-center space-x-3">
              <ChartBarIcon className="h-8 w-8 text-purple-600" />
              <div>
                <p className="text-sm font-medium text-purple-600">AI Confidence</p>
                <p className="text-sm text-purple-900 font-medium">{Math.round(report.confidence_score * 100)}%</p>
              </div>
            </div>
          </div>
        )}

        <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-6 border border-orange-200">
          <div className="flex items-center space-x-3">
            <StarIcon className="h-8 w-8 text-orange-600" />
            <div>
              <p className="text-sm font-medium text-orange-600">Analysis Type</p>
              <p className="text-sm text-orange-900 font-medium">Gemini AI</p>
            </div>
          </div>
        </div>
      </div>

      {/* Query Section */}
      <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
        <h2 className="text-xl font-semibold text-medical-900 mb-4 flex items-center space-x-2">
          <MagnifyingGlassIcon className="h-6 w-6 text-primary-600" />
          <span>Ask Questions About Your Report</span>
        </h2>
        
        <div className="space-y-4">
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-medical-700 mb-2">
              Your Question
            </label>
            <textarea
              id="query"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., What are the key findings in my blood test? Are there any concerning values?"
              className="w-full px-4 py-3 border border-medical-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
              rows="3"
            />
          </div>
          
          <button
            onClick={handleAnalyze}
            disabled={analyzing || !query.trim()}
            className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-lg hover:from-primary-700 hover:to-primary-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg"
          >
            {analyzing ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Analyzing with AI...</span>
              </>
            ) : (
              <>
                <MagnifyingGlassIcon className="h-5 w-5" />
                <span>Analyze Report</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Analysis Results */}
      {analysisResult && (
        <div id="analysis-report" className="space-y-6">
          <div className="bg-gradient-to-r from-medical-50 to-medical-100 rounded-xl p-6 border border-medical-200">
            <h2 className="text-2xl font-bold text-medical-900 mb-2 flex items-center space-x-3">
              <ChartBarIcon className="h-8 w-8 text-primary-600" />
              <span>AI-Powered Analysis Results</span>
            </h2>
            <p className="text-medical-600">Comprehensive analysis powered by Google Gemini AI</p>
          </div>

          {renderSection(
            "Summary of Key Findings",
            parsedAnalysis.summary,
            'summary',
            <InformationCircleIcon className="h-6 w-6 text-blue-600" />
          )}

          {renderSection(
            "Interpretation of Values",
            parsedAnalysis.interpretation,
            'interpretation',
            <ExclamationCircleIcon className="h-6 w-6 text-orange-600" />
          )}

          {renderSection(
            "Clinical Significance",
            parsedAnalysis.clinical,
            'clinical',
            <CheckIcon className="h-6 w-6 text-green-600" />
          )}

          {renderSection(
            "Recommendations & Follow-up",
            parsedAnalysis.recommendations,
            'recommendations',
            <StarIcon className="h-6 w-6 text-purple-600" />
          )}

          {renderSection(
            "General Health Insights",
            parsedAnalysis.insights,
            'insights',
            <ChartBarIcon className="h-6 w-6 text-indigo-600" />
          )}

          {/* Raw Analysis (Collapsible) */}
          <div className="bg-white rounded-xl shadow-sm border border-medical-200 overflow-hidden">
            <button
              onClick={() => setShowExtractedText(!showExtractedText)}
              className="w-full px-6 py-4 flex items-center justify-between bg-gradient-to-r from-gray-50 to-white hover:from-gray-100 transition-all duration-200"
            >
              <div className="flex items-center space-x-3">
                <DocumentTextIcon className="h-6 w-6 text-gray-600" />
                <h3 className="text-lg font-semibold text-gray-900">Complete Analysis Text</h3>
              </div>
              {showExtractedText ? (
                <EyeSlashIcon className="h-5 w-5 text-gray-600" />
              ) : (
                <EyeIcon className="h-5 w-5 text-gray-600" />
              )}
            </button>
            
            {showExtractedText && (
              <div className="px-6 pb-6">
                <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                  <div className="prose prose-sm max-w-none text-gray-700">
                    {analysisResult.split('\n').map((line, index) => (
                      <p key={index} className="mb-2">
                        {line}
                      </p>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Extracted Text */}
      {report.extracted_text && (
        <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
          <h2 className="text-lg font-semibold text-medical-900 mb-4">Raw PDF Text</h2>
          <div className="bg-medical-50 rounded-lg p-4 max-h-64 overflow-y-auto">
            <pre className="text-sm text-medical-700 whitespace-pre-wrap font-sans">
              {report.extracted_text}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportDetails; 