import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { 
  DocumentTextIcon,
  ArrowRightIcon,
  ClockIcon,
  CheckCircleIcon,
  XCircleIcon,
  PlusIcon,
  EyeIcon,
  QuestionMarkCircleIcon,
  TrashIcon,
  ExclamationTriangleIcon,
  LockClosedIcon,
  StarIcon,
  ChartBarIcon,
  ExclamationCircleIcon,
  InformationCircleIcon,
  CheckIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { toast } from 'react-hot-toast';
import { Dialog } from '@headlessui/react';
import html2pdf from 'html2pdf.js';

const Dashboard = () => {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [reportToDelete, setReportToDelete] = useState(null);
  const [deletePassword, setDeletePassword] = useState('');
  const [deleting, setDeleting] = useState(false);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [selectedReportAnalysis, setSelectedReportAnalysis] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [expandedSections, setExpandedSections] = useState({
    summary: true,
    interpretation: true,
    recommendations: true,
    insights: true,
    clinical: true
  });

  // Function to reset expanded sections when modal opens
  const resetExpandedSections = () => {
    setExpandedSections({
      summary: true,
      interpretation: true,
      recommendations: true,
      insights: true,
      clinical: true
    });
  };

  const formatContent = (text, sectionKey = '') => {
    if (!text) return '';
    let formatted = text
      .replace(/\*\*([^*]+)\*\*/g, '<strong class="text-medical-900 font-semibold">$1</strong>')
      .replace(/\*([^*]+)\*/g, '<em class="text-medical-700 italic">$1</em>')
      .replace(/(normal|good|excellent|healthy)/gi, '<span class="text-green-600 font-medium">$1</span>')
      .replace(/(elevated|high|concerning|abnormal)/gi, '<span class="text-orange-600 font-medium">$1</span>')
      .replace(/(critical|dangerous|severe)/gi, '<span class="text-red-600 font-medium">$1</span>');
    
    // Enhanced formatting for recommendations and insights
    if (sectionKey === 'recommendations' || sectionKey === 'insights') {
      let blocks = formatted.split(/\n\n|(?=\d+\. )|(?=• )|(?=- )/g).filter(Boolean);
      formatted = blocks.map(block => `<div class="mb-3">${block.trim()}</div>`).join('');
      formatted = formatted.replace(/(Vitamin D|HbA1c|HDL|LDL|BMI|CBC|CMP)/gi, '<span style="white-space: nowrap;">$1</span>');
    }
    
    // Enhanced formatting for interpretation section: pointwise, spaced, bullet style
    if (sectionKey === 'interpretation') {
      // Remove stray bullets, single letters, and empty lines
      let cleaned = formatted.replace(/^[•\-*]\s*$/gm, '').replace(/^([A-Z])$/gm, '').replace(/\n{2,}/g, '\n');
      // Split on patterns like 'Analyte (value):', '*', or double newlines
      let points = cleaned.split(/(?=[A-Z][a-zA-Z ]+\([^)]+\):)|\*|\n\n|\n|•/).map(p => p.trim()).filter(p => p && p.length > 2);
      formatted = points.map(point => `<div class="mb-2 flex items-start"><span class="mr-2 text-medical-600">•</span><span>${point}</span></div>`).join('');
      formatted = formatted.replace(/(Vitamin D|HbA1c|HDL|LDL|BMI|CBC|CMP)/gi, '<span style="white-space: nowrap;">$1</span>');
    }
    
    if (!formatted.includes('<p>') && !formatted.includes('<div')) {
      formatted = `<p class="mb-3">${formatted}</p>`;
    }
    
    return formatted;
  };

  const fetchReports = async () => {
    try {
      setRefreshing(true);
      const response = await axios.get('/api/user-reports');
      setReports(response.data);
    } catch (error) {
      toast.error('Failed to fetch reports');
      console.error('Error fetching reports:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchReports();
    
    // Set up polling to refresh data every 30 seconds
    const interval = setInterval(() => {
      if (!loading) {
        fetchReports();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [loading]);

  // Function to manually refresh data
  const handleRefresh = () => {
    fetchReports();
  };

  // Function to open delete confirmation modal
  const handleDeleteClick = (report) => {
    setReportToDelete(report);
    setDeletePassword('');
    setShowDeleteModal(true);
  };

  // Function to close delete modal
  const handleCloseDeleteModal = () => {
    setShowDeleteModal(false);
    setReportToDelete(null);
    setDeletePassword('');
  };

  // Function to delete report with authentication
  const handleDeleteReport = async () => {
    if (!deletePassword.trim()) {
      toast.error('Please enter your password to confirm deletion');
      return;
    }

    try {
      setDeleting(true);
      
      // Get username from stored user data
      const storedUser = localStorage.getItem('user');
      const userData = storedUser ? JSON.parse(storedUser) : null;
      const username = userData?.username || '';
      
      // First verify the password by making a login request
      const formData = new FormData();
      formData.append('identifier', username);
      formData.append('password', deletePassword);

      const loginResponse = await axios.post('/api/login', formData);

      if (loginResponse.data.access_token) {
        // Password is correct, proceed with deletion
        const token = loginResponse.data.access_token;
        
        await axios.delete(`/api/report/${reportToDelete.id}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        toast.success('Report deleted successfully');
        handleCloseDeleteModal();
        fetchReports(); // Refresh the reports list
      }
    } catch (error) {
      if (error.response?.status === 401) {
        toast.error('Incorrect password. Please try again.');
      } else {
        toast.error('Failed to delete report. Please try again.');
        console.error('Error deleting report:', error);
      }
    } finally {
      setDeleting(false);
    }
  };

  const getStatusIcon = (status) => {
    if (!status) return <QuestionMarkCircleIcon className="w-5 h-5 text-gray-400" />;
    
    switch (status.toLowerCase()) {
      case 'completed':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'processing':
        return <ClockIcon className="w-5 h-5 text-yellow-500" />;
      case 'failed':
        return <XCircleIcon className="w-5 h-5 text-red-500" />;
      case 'uploaded':
        return <DocumentTextIcon className="w-5 h-5 text-blue-500" />;
      default:
        return <QuestionMarkCircleIcon className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    if (!status) return 'bg-gray-100 text-gray-800';
    
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'uploaded':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Calculate chart data
  const getStatusChartData = () => {
    const statusCounts = {
      completed: reports.filter(r => r.status === 'completed').length,
      processing: reports.filter(r => r.status === 'processing').length,
      failed: reports.filter(r => r.status === 'failed').length,
      uploaded: reports.filter(r => r.status === 'uploaded').length,
      pending: reports.filter(r => r.status === 'pending').length
    };
    
    return [
      { name: 'Completed', value: statusCounts.completed, color: '#10B981' },
      { name: 'Processing', value: statusCounts.processing, color: '#F59E0B' },
      { name: 'Failed', value: statusCounts.failed, color: '#EF4444' },
      { name: 'Uploaded', value: statusCounts.uploaded, color: '#3B82F6' },
      { name: 'Pending', value: statusCounts.pending, color: '#6B7280' }
    ].filter(item => item.value > 0);
  };

  const getConfidenceChartData = () => {
    const buckets = [
      { name: '90-100%', value: 0, color: '#10B981' },
      { name: '80-89%', value: 0, color: '#3B82F6' },
      { name: '70-79%', value: 0, color: '#F59E0B' },
      { name: 'Below 70%', value: 0, color: '#EF4444' },
    ];
    
    reports.forEach(r => {
      if (r.confidence_score >= 0.9) buckets[0].value++;
      else if (r.confidence_score >= 0.8) buckets[1].value++;
      else if (r.confidence_score >= 0.7) buckets[2].value++;
      else if (r.confidence_score > 0) buckets[3].value++;
    });
    
    return buckets.filter(bucket => bucket.value > 0);
  };

  const fetchFullAnalysis = async (report) => {
    try {
      const response = await axios.get(`/api/report/${report.id}`);
      setSelectedReportAnalysis(response.data.analysis_result || '');
      setSelectedReport(report);
      resetExpandedSections(); // Reset sections to expanded state
      setShowAnalysisModal(true);
    } catch (error) {
      toast.error('Failed to fetch full analysis');
    }
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
    let cleanResult = result
      .replace(/\\n/g, '\n')
      .replace(/\\'/g, "'")
      .replace(/\\"/g, '"')
      .replace(/^['"]|['"]$/g, '')
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
      .replace(/\n\s*\n\s*\n/g, '\n\n')
      .replace(/^\s+|\s+$/g, '')
      .trim();
    // Remove stray bullet points and empty lines
    cleanResult = cleanResult.replace(/^[•\-*]\s*$/gm, '').replace(/\n{2,}/g, '\n');
    const lines = cleanResult.split('\n');
    let currentSection = '';
    let sectionContent = [];
    lines.forEach(line => {
      const trimmedLine = line.trim();
      if (trimmedLine.match(/\*\*1\.?\s*Summary|\*\*Summary|Summary of Key Findings/i)) {
        if (currentSection && sectionContent.length > 0) sections[currentSection] = sectionContent.join('\n');
        currentSection = 'summary'; sectionContent = [];
      } else if (trimmedLine.match(/\*\*2\.?\s*Interpretation|\*\*Interpretation|Interpretation of Any abnormal Values|Interpretation of Abnormal Values/i)) {
        if (currentSection && sectionContent.length > 0) sections[currentSection] = sectionContent.join('\n');
        currentSection = 'interpretation'; sectionContent = [];
      } else if (trimmedLine.match(/\*\*3\.?\s*Clinical|\*\*Clinical|Clinical Significance of Results/i)) {
        if (currentSection && sectionContent.length > 0) sections[currentSection] = sectionContent.join('\n');
        currentSection = 'clinical'; sectionContent = [];
      } else if (trimmedLine.match(/\*\*4\.?\s*Recommendations|\*\*Recommendations|Recommendations & Follow-up/i)) {
        if (currentSection && sectionContent.length > 0) sections[currentSection] = sectionContent.join('\n');
        currentSection = 'recommendations'; sectionContent = [];
      } else if (trimmedLine.match(/\*\*5\.?\s*General Health|\*\*General Health|General Health Insights/i)) {
        if (currentSection && sectionContent.length > 0) sections[currentSection] = sectionContent.join('\n');
        currentSection = 'insights'; sectionContent = [];
      } else if (currentSection && trimmedLine) {
        // Remove lines that are just single letters or stray bullets
        if (!/^([A-Z]|[•\-*])$/.test(trimmedLine)) {
          sectionContent.push(line);
        }
      }
    });
    if (currentSection && sectionContent.length > 0) {
      sections[currentSection] = sectionContent.join('\n');
    }
    return sections;
  };

  const renderSection = (title, content, sectionKey, icon, color = 'blue', number = 1) => {
    const isExpanded = expandedSections[sectionKey];
    return (
      <div key={sectionKey} className="bg-white rounded-xl shadow-sm border border-medical-200 overflow-hidden mb-4">
        <button
          onClick={() => setExpandedSections(prev => ({ ...prev, [sectionKey]: !prev[sectionKey] }))}
          className="w-full px-6 py-4 flex items-center justify-between bg-gradient-to-r from-medical-50 to-white hover:from-medical-100 transition-all duration-200"
        >
          <div className="flex items-center space-x-3">
            {icon}
            <h3 className="text-lg font-semibold text-medical-900">{title}</h3>
          </div>
          {isExpanded ? (
            <ChevronUpIcon className="h-5 w-5 text-medical-600" />
          ) : (
            <ChevronDownIcon className="h-5 w-5 text-medical-600" />
          )}
        </button>
        {isExpanded && (
          <div className="px-6 pb-6">
            <div 
              className={`prose prose-medical max-w-none ${
                sectionKey === 'insights' 
                  ? 'space-y-4 leading-relaxed' 
                  : ''
              }`}
              style={sectionKey === 'insights' ? {
                wordWrap: 'break-word',
                hyphens: 'auto',
                lineHeight: '1.8'
              } : {}}
              dangerouslySetInnerHTML={{ __html: formatContent(content, sectionKey) }} 
            />
          </div>
        )}
      </div>
    );
  };

  // Add this function to handle PDF export for a report
  const exportReportSummaryToPDF = (report) => {
    const analysis = parseAnalysisResult(report.analysis_result);
    const tempDiv = document.createElement('div');
    tempDiv.style.background = '#fff';
    tempDiv.style.fontFamily = 'Arial, sans-serif';
    tempDiv.style.padding = '20px';
    tempDiv.style.width = '100%';
    tempDiv.style.maxWidth = '800px';
    tempDiv.style.boxSizing = 'border-box';
    tempDiv.style.lineHeight = '1.6';

    // Get user details from localStorage
    let userDetailsHTML = '';
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        const userData = JSON.parse(storedUser);
        userDetailsHTML = `<div style="font-size:16px;font-weight:600;color:#1e293b;text-align:center;margin-bottom:6px;">${userData.full_name || ''}</div>`;
        if (userData.email) {
          userDetailsHTML += `<div style="font-size:13px;color:#64748b;text-align:center;margin-bottom:10px;">${userData.email}</div>`;
        }
      }
    } catch {}

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
        ${userDetailsHTML}
        <div style="font-size: 18px; font-weight: 600; color: #475569; margin-bottom: 8px; text-align: center;">${report.filename}</div>
        <div style="font-size: 14px; color: #64748b; text-align: center;">
          Uploaded: ${new Date(report.upload_date).toLocaleDateString()} | Generated: ${new Date().toLocaleDateString()}
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
    
    // Get full_name from localStorage
    let fullName = 'report';
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        const userData = JSON.parse(storedUser);
        if (userData.full_name) fullName = userData.full_name.replace(/\s+/g, '_');
      }
    } catch {}
    
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

  if (loading) {
    return (
      <div className="min-h-screen bg-medical-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-medical-600">Loading your reports...</p>
        </div>
      </div>
    );
  }

  const statusChartData = getStatusChartData();
  const confidenceChartData = getConfidenceChartData();

  return (
    <div className="min-h-screen bg-medical-50 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-medical-900">Dashboard</h1>
            <p className="mt-2 text-medical-600">
              View your blood test reports and analysis results
            </p>
          </div>
          <div className="mt-4 sm:mt-0 flex space-x-3">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="inline-flex items-center px-4 py-2 border border-medical-300 shadow-sm text-sm font-medium rounded-md text-medical-700 bg-white hover:bg-medical-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors disabled:opacity-50"
            >
              {refreshing ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-medical-600 mr-2"></div>
              ) : (
                <ArrowRightIcon className="w-4 h-4 mr-2" />
              )}
              Refresh
            </button>
            <Link
              to="/upload"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
            >
              <PlusIcon className="w-4 h-4 mr-2" />
              Upload Report
            </Link>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <DocumentTextIcon className="w-8 h-8 text-medical-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-medical-600">Total Reports</p>
                <p className="text-2xl font-bold text-medical-900">{reports.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircleIcon className="w-8 h-8 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-medical-600">Completed</p>
                <p className="text-2xl font-bold text-medical-900">
                  {reports.filter(r => r.status && r.status === 'completed').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ClockIcon className="w-8 h-8 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-medical-600">Processing</p>
                <p className="text-2xl font-bold text-medical-900">
                  {reports.filter(r => r.status && r.status === 'processing').length}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <XCircleIcon className="w-8 h-8 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-medical-600">Failed</p>
                <p className="text-2xl font-bold text-medical-900">
                  {reports.filter(r => r.status && r.status === 'failed').length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        {reports.length > 0 && (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {/* Status Distribution Pie Chart */}
            <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-4 sm:p-6">
              <h2 className="text-lg font-semibold text-medical-900 mb-4 sm:mb-6 text-center">
                Report Status Distribution
              </h2>
              <div className="flex flex-col items-center">
                <div className="relative w-48 h-48 sm:w-64 sm:h-64 mb-4 sm:mb-6">
                  {statusChartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={statusChartData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {statusChartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip 
                          formatter={(value, name) => [value, name]}
                          contentStyle={{
                            backgroundColor: 'white',
                            border: '1px solid #e5e7eb',
                            borderRadius: '8px',
                            padding: '8px'
                          }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-full text-medical-500">
                      No data available
                    </div>
                  )}
                </div>
                <div className="w-full space-y-2 sm:space-y-3">
                  {statusChartData.map((item) => {
                    const percentage = reports.length > 0 ? (item.value / reports.length) * 100 : 0;
                    return (
                      <div key={item.name} className="flex items-center justify-between text-xs sm:text-sm p-2 bg-medical-50 rounded-lg">
                        <div className="flex items-center">
                          <div 
                            className="w-3 h-3 sm:w-4 sm:h-4 rounded-full mr-2 sm:mr-3"
                            style={{ backgroundColor: item.color }}
                          ></div>
                          <span className="text-medical-700 font-medium truncate">{item.name}</span>
                        </div>
                        <span className="font-semibold text-medical-900 ml-2">
                          {item.value} ({percentage.toFixed(1)}%)
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Confidence Score Distribution Pie Chart */}
            <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-4 sm:p-6">
              <h2 className="text-lg font-semibold text-medical-900 mb-4 sm:mb-6 text-center">
                Confidence Score Distribution
              </h2>
              <div className="flex flex-col items-center">
                <div className="relative w-48 h-48 sm:w-64 sm:h-64 mb-4 sm:mb-6">
                  {confidenceChartData.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={confidenceChartData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {confidenceChartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip 
                          formatter={(value, name) => [value, name]}
                          contentStyle={{
                            backgroundColor: 'white',
                            border: '1px solid #e5e7eb',
                            borderRadius: '8px',
                            padding: '8px'
                          }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex items-center justify-center h-full text-medical-500">
                      No confidence data available
                    </div>
                  )}
                </div>
                <div className="w-full grid grid-cols-2 gap-2 sm:gap-3">
                  <div className="flex items-center space-x-2 p-2 bg-medical-50 rounded-lg">
                    <span className="w-3 h-3 sm:w-4 sm:h-4 rounded-full inline-block" style={{background:'#10B981'}}></span>
                    <span className="text-xs sm:text-sm font-medium text-medical-700">90-100%</span>
                  </div>
                  <div className="flex items-center space-x-2 p-2 bg-medical-50 rounded-lg">
                    <span className="w-3 h-3 sm:w-4 sm:h-4 rounded-full inline-block" style={{background:'#3B82F6'}}></span>
                    <span className="text-xs sm:text-sm font-medium text-medical-700">80-89%</span>
                  </div>
                  <div className="flex items-center space-x-2 p-2 bg-medical-50 rounded-lg">
                    <span className="w-3 h-3 sm:w-4 sm:h-4 rounded-full inline-block" style={{background:'#F59E0B'}}></span>
                    <span className="text-xs sm:text-sm font-medium text-medical-700">70-79%</span>
                  </div>
                  <div className="flex items-center space-x-2 p-2 bg-medical-50 rounded-lg">
                    <span className="w-3 h-3 sm:w-4 sm:h-4 rounded-full inline-block" style={{background:'#EF4444'}}></span>
                    <span className="text-xs sm:text-sm font-medium text-medical-700">Below 70%</span>
                  </div>
              </div>
              </div>
            </div>
          </div>
        )}

        {/* Reports List with Results */}
        <div className="bg-white rounded-xl shadow-sm border border-medical-200">
          <div className="px-6 py-4 border-b border-medical-200">
            <h2 className="text-lg font-semibold text-medical-900">Your Reports & Analysis Results</h2>
          </div>
          <div className="divide-y divide-medical-200">
            {reports.length === 0 ? (
              <div className="px-6 py-12 text-center">
                <DocumentTextIcon className="w-12 h-12 text-medical-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-medical-900 mb-2">No reports yet</h3>
                <p className="text-medical-600 mb-4">
                  Upload your first blood test report to get started
                </p>
              </div>
            ) : (
              reports.map((report) => (
                <div key={report.id} className="p-6 hover:bg-medical-50 transition-colors">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-4">
                      {getStatusIcon(report.status)}
                      <div>
                        <h3 className="text-lg font-medium text-medical-900">
                          {report.filename}
                        </h3>
                        <p className="text-sm text-medical-600">
                          Uploaded {new Date(report.upload_date).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(report.status)}`}>
                        {report.status ? report.status.charAt(0).toUpperCase() + report.status.slice(1) : 'Unknown'}
                      </span>
                      <button
                        onClick={() => fetchFullAnalysis(report)}
                        className="inline-flex items-center px-3 py-1.5 border border-medical-300 shadow-sm text-xs font-medium rounded-md text-medical-700 bg-white hover:bg-medical-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors"
                      >
                        <EyeIcon className="w-4 h-4 mr-1" />
                        View Details
                      </button>
                      <button
                        onClick={() => handleDeleteClick(report)}
                        className="inline-flex items-center px-3 py-1.5 border border-red-300 shadow-sm text-xs font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
                      >
                        <TrashIcon className="w-4 h-4 mr-1" />
                        Delete
                      </button>
                    </div>
                  </div>
                  
                  {/* Analysis Result Preview */}
                  {report.status && report.status === 'completed' && report.analysis_result && (
                    <div className="bg-medical-50 border border-medical-200 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-medical-900 mb-2 flex items-center">
                        <InformationCircleIcon className="h-4 w-4 text-blue-600 mr-1" />
                        Summary of Key Findings:
                      </h4>
                      <div className="text-sm text-medical-700">
                        <div className="prose prose-medical max-w-none" dangerouslySetInnerHTML={{ __html: formatContent(parseAnalysisResult(report.analysis_result).summary || 'No summary available.', 'summary') }} />
                      </div>
                      <div className="flex space-x-2 mt-2">
                        <button
                          onClick={() => fetchFullAnalysis(report)}
                          className="inline-flex items-center text-xs text-primary-600 hover:text-primary-700"
                        >
                          Read full analysis &rarr;
                        </button>
                        <button
                          onClick={() => exportReportSummaryToPDF(report)}
                          className="inline-flex items-center text-xs text-medical-700 hover:text-blue-700 border border-medical-300 rounded px-2 py-1 ml-2"
                        >
                          Download PDF
                        </button>
                      </div>
                    </div>
                  )}
                  
                  {report.status && report.status === 'processing' && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <div className="flex items-center">
                        <ClockIcon className="w-4 h-4 text-yellow-600 mr-2" />
                        <span className="text-sm text-yellow-800">Analysis in progress...</span>
                      </div>
                    </div>
                  )}
                  
                  {report.status && report.status === 'failed' && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <div className="flex items-center">
                        <XCircleIcon className="w-4 h-4 text-red-600 mr-2" />
                        <span className="text-sm text-red-800">Analysis failed. Please try again.</span>
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Previous Results Table */}
        <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6 mt-8">
          <h2 className="text-lg font-semibold text-medical-900 mb-4">Previous Results</h2>
          {reports.length === 0 ? (
            <div className="text-medical-600 text-center py-8">No reports found.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-medical-200">
                <thead className="bg-medical-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-medical-500 uppercase tracking-wider">File Name</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-medical-500 uppercase tracking-wider">Upload Date</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-medical-500 uppercase tracking-wider">Status</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-medical-500 uppercase tracking-wider">Confidence</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-medical-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-medical-200">
                  {reports.map((report) => (
                    <tr key={report.id} className="hover:bg-medical-50 transition-colors">
                      <td className="px-4 py-2 text-medical-900 font-medium">{report.filename}</td>
                      <td className="px-4 py-2 text-medical-700">{new Date(report.upload_date).toLocaleString()}</td>
                      <td className="px-4 py-2">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(report.status)}`}>
                          {getStatusIcon(report.status)}
                          <span className="ml-1">{report.status ? report.status.charAt(0).toUpperCase() + report.status.slice(1) : 'Unknown'}</span>
                        </span>
                      </td>
                      <td className="px-4 py-2 text-medical-700">{report.confidence_score ? `${(report.confidence_score*100).toFixed(1)}%` : '-'}</td>
                      <td className="px-4 py-2">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => fetchFullAnalysis(report)}
                            className="inline-flex items-center text-primary-600 hover:text-primary-800 font-medium"
                          >
                            <EyeIcon className="w-5 h-5 mr-1" /> View
                          </button>
                          <button
                            onClick={() => handleDeleteClick(report)}
                            className="inline-flex items-center text-red-600 hover:text-red-800 font-medium"
                          >
                            <TrashIcon className="w-5 h-5 mr-1" /> Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="p-6">
              <div className="flex items-center mb-4">
                <div className="flex-shrink-0">
                  <ExclamationTriangleIcon className="w-8 h-8 text-red-600" />
                </div>
                <div className="ml-3">
                  <h3 className="text-lg font-medium text-gray-900">Delete Report</h3>
                  <p className="text-sm text-gray-500">This action cannot be undone.</p>
                </div>
              </div>
              
              <div className="mb-4">
                <p className="text-sm text-gray-700 mb-2">
                  Are you sure you want to delete <strong>{reportToDelete?.filename}</strong>?
                </p>
                <p className="text-xs text-gray-500">
                  This will permanently remove the report and all associated analysis data.
                </p>
              </div>

              <div className="mb-6">
                <label htmlFor="delete-password" className="block text-sm font-medium text-gray-700 mb-2">
                  <LockClosedIcon className="w-4 h-4 inline mr-1" />
                  Enter your password to confirm
                </label>
                <input
                  type="password"
                  id="delete-password"
                  value={deletePassword}
                  onChange={(e) => setDeletePassword(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  placeholder="Enter your password"
                  autoComplete="current-password"
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={handleCloseDeleteModal}
                  disabled={deleting}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleDeleteReport}
                  disabled={deleting || !deletePassword.trim()}
                  className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors disabled:opacity-50"
                >
                  {deleting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Deleting...
                    </>
                  ) : (
                    'Delete Report'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Result Modal */}
      <Dialog open={showAnalysisModal} onClose={() => setShowAnalysisModal(false)} className="fixed z-50 inset-0 overflow-y-auto">
        <div className="flex items-center justify-center min-h-screen px-4 py-8">
          <Dialog.Overlay className="fixed inset-0 bg-black opacity-30" />
          <div className="relative bg-white rounded-xl shadow-xl max-w-4xl w-full mx-auto p-6 z-10 max-h-[90vh] overflow-y-auto">
            <button onClick={() => setShowAnalysisModal(false)} className="absolute top-4 right-4 text-gray-400 hover:text-gray-700 z-20">
              <XMarkIcon className="h-6 w-6" />
            </button>
            <h2 className="text-2xl font-bold text-medical-900 mb-4 flex items-center space-x-2 pr-8">
              <ChartBarIcon className="h-7 w-7 text-primary-600" />
              <span>Complete Blood Test Analysis</span>
            </h2>
            {selectedReport && (
              <div className="mb-6 p-4 bg-medical-50 rounded-lg border border-medical-200">
                <p className="text-sm font-medium text-medical-900">File: {selectedReport.filename}</p>
                <p className="text-xs text-medical-600">Uploaded: {new Date(selectedReport.upload_date).toLocaleDateString()}</p>
              </div>
            )}
            {selectedReportAnalysis ? (
              <div className="space-y-6">
                {renderSection('📋 Summary of Key Findings', parseAnalysisResult(selectedReportAnalysis).summary, 'summary', <InformationCircleIcon className="h-6 w-6 text-blue-600" />)}
                {renderSection('🔍 Interpretation of Abnormal Values', parseAnalysisResult(selectedReportAnalysis).interpretation, 'interpretation', <ExclamationCircleIcon className="h-6 w-6 text-orange-600" />)}
                {renderSection('🏥 Clinical Significance of Results', parseAnalysisResult(selectedReportAnalysis).clinical, 'clinical', <CheckIcon className="h-6 w-6 text-green-600" />)}
                {renderSection('💡 Recommendations for Follow-up', parseAnalysisResult(selectedReportAnalysis).recommendations, 'recommendations', <StarIcon className="h-6 w-6 text-purple-600" />)}
                {renderSection('💊 General Health Insights', parseAnalysisResult(selectedReportAnalysis).insights, 'insights', <ChartBarIcon className="h-6 w-6 text-indigo-600" />)}
                
                <div className="mt-8 pt-6 border-t border-medical-200">
                  <button
                    onClick={() => exportReportSummaryToPDF(selectedReport)}
                    className="inline-flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
                  >
                    <DocumentTextIcon className="w-5 h-5 mr-2" />
                    Download Complete PDF Report
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center text-medical-600 py-8">No analysis result available.</div>
            )}
          </div>
        </div>
      </Dialog>
    </div>
  );
};

export default Dashboard; 